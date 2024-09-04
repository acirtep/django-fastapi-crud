import datetime
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from PIL import Image
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from pydantic import UUID4
from sqlalchemy import case
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse
from starlette.responses import Response
from wordcloud import WordCloud

from mysite.articles.models import Article
from mysite.database import get_db
from mysite.database import query_to_pandas_df
from mysite.text_analytics.models import ArticleTermOccurrenceMV
from mysite.text_analytics.models import CorpusTermOccurrenceMV
from mysite.writers.models import Writer

text_analytics_router = APIRouter(prefix="/text-analytics")


@text_analytics_router.get("/writer-content-length/{writer_id}", response_class=HTMLResponse)
async def get_writer_content_length(writer_id: UUID4, db: AsyncSession = Depends(get_db)):
    writer_obj = await db.scalar(select(Writer).where(Writer.writer_id == writer_id))

    query = (
        select(Article.article_name, func.length(Article.article_content).label("number_of_words"))
        .where(Article.writer_id == writer_id)
        .order_by(func.length(Article.article_content))
    )

    article_df = await db.run_sync(query_to_pandas_df, query)

    fig = px.bar(
        article_df,
        y="article_name",
        x="number_of_words",
        orientation="h",
        title=f"Content length for {writer_obj.first_name} {writer_obj.last_name}'s articles",
    )

    return fig.to_html()


@text_analytics_router.get("/writer-stats-most-user-words/{writer_id}", response_class=HTMLResponse)
async def get_writer_most_used_words(
    writer_id: UUID4,
    db: AsyncSession = Depends(get_db),
):
    writer_obj = await db.scalar(select(Writer).where(Writer.writer_id == writer_id))

    query = select(Article.article_content_simple_with_no_stop_words).where(Article.writer_id == writer_id)

    ts_stat = text(
        f"""select word, ndoc as number_of_articles, nentry number_of_occurrences
            from ts_stat($${query.compile(dialect=postgresql.dialect(), compile_kwargs={'literal_binds': True})}$$)
            order by number_of_occurrences desc
            limit 20
            """
    )
    article_df = await db.run_sync(query_to_pandas_df, ts_stat)

    fig = px.bar(
        article_df,
        y="number_of_occurrences",
        x="number_of_articles",
        color="word",
        title=f"""Top 20 most used words by {writer_obj.first_name} {writer_obj.last_name}""",
        labels={"number_of_articles": "Number of documents", "number_of_occurrences": "Number of occurrences"},
    )

    return fig.to_html()


@text_analytics_router.get("/wordcloud", response_class=Response, responses={200: {"content": {"image/png": {}}}})
async def get_wordcloud(db: AsyncSession = Depends(get_db)):
    word_occurrences_subquery = select(
        ArticleTermOccurrenceMV.word,
        ArticleTermOccurrenceMV.number_of_occurrences,
        func.row_number()
        .over(
            partition_by=ArticleTermOccurrenceMV.article_id,
            order_by=desc(ArticleTermOccurrenceMV.number_of_occurrences),
        )
        .label("rank"),
    ).subquery("word_occurrences_subquery")

    top_word_occurrences_subquery = (
        select(
            word_occurrences_subquery.c.word,
            func.sum(word_occurrences_subquery.c.number_of_occurrences).label("number_of_occurrences"),
        )
        .where(word_occurrences_subquery.c.rank <= 20)
        .group_by(word_occurrences_subquery.c.word)
    ).subquery("top_word_occurrences_subquery")

    # words_with_frequencies = {
    #     db_record[0]: db_record[1] for db_record in await db.execute(select(top_word_occurrences_subquery))
    # }

    words_with_frequencies = await db.scalar(
        select(
            func.json_object_agg(
                top_word_occurrences_subquery.c.word, top_word_occurrences_subquery.c.number_of_occurrences
            )
        )
    )

    if not words_with_frequencies:
        raise HTTPException(status_code=404, detail="No data found")

    try:

        picture_np = np.asarray(
            Image.open(f"{Path(__file__).parent.parent.parent}/medium_data/100_1.png"), dtype="int32"
        )

        wc = WordCloud(
            background_color="white",
            mask=picture_np,
            contour_width=3,
            contour_color="gold",
            colormap="autumn",
            collocations=False,
            stopwords=["ve"],
        )
        wc.generate_from_frequencies(words_with_frequencies)

        fig = plt.figure(figsize=(20, 5))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")

        with BytesIO() as buf:
            fig.savefig(buf, format="png")
            plt.close()

            return Response(
                content=buf.getvalue(),
                headers={
                    "Content-Disposition": f'inline; filename="wordcloud-{datetime.datetime.now().isoformat()}.png"'  # NOQA
                },
                media_type="image/png",
            )

    except Exception:
        # log error
        raise HTTPException(status_code=500, detail="Something went wrong")


@text_analytics_router.get("/tf-idf-most-user-word", response_class=HTMLResponse)
async def get_term_frequency_corpus(
    db: AsyncSession = Depends(get_db),
):
    writer_id = await db.scalar(select(Writer.writer_id).where(Writer.email == "user+medium_data@example.com"))

    number_of_articles, limit_words = (
        await db.execute(
            select(
                func.count(Article.article_id),
                func.sum(
                    case(
                        (func.length(Article.article_content_simple_with_no_stop_words) >= 5, 5),
                        else_=func.length(Article.article_content_simple_with_no_stop_words),
                    )
                ),
            ).where(Article.writer_id == writer_id)
        )
    ).first()

    tf_cte = (
        select(
            ArticleTermOccurrenceMV.article_id,
            Article.article_name,
            ArticleTermOccurrenceMV.word,
            (
                ArticleTermOccurrenceMV.number_of_occurrences
                / func.length(Article.article_content_simple_with_no_stop_words)
            ).label("tf"),
        )
        .join(Article, ArticleTermOccurrenceMV.article_id == Article.article_id)
        .where(Article.writer_id == writer_id)
    ).cte("tf_cte")

    idf_cte = (
        (
            select(
                CorpusTermOccurrenceMV.word,
                func.log((number_of_articles / CorpusTermOccurrenceMV.number_of_articles)).label("idf"),
            )
        )
        .cte("idf_cte")
        .prefix_with("MATERIALIZED")
    )

    tf_idf_count_query = (
        select(
            tf_cte.c.article_name,
            tf_cte.c.word,
            (tf_cte.c.tf * idf_cte.c.idf * 100).label("score"),
            literal("TF-IDF").label("rank_type"),
        )
        .join(idf_cte, tf_cte.c.word == idf_cte.c.word)
        .order_by(
            func.row_number().over(partition_by=tf_cte.c.article_id, order_by=desc(tf_cte.c.tf * idf_cte.c.idf * 100))
        )
        .limit(limit_words)
        .union_all(
            select(
                Article.article_name,
                ArticleTermOccurrenceMV.word,
                ArticleTermOccurrenceMV.number_of_occurrences.label("score"),
                literal("COUNT").label("rank_type"),
            )
            .join(Article, ArticleTermOccurrenceMV.article_id == Article.article_id)
            .where(Article.writer_id == writer_id)
            .where(ArticleTermOccurrenceMV.word != "data")
            .order_by(
                func.row_number().over(
                    partition_by=ArticleTermOccurrenceMV.article_id,
                    order_by=desc(ArticleTermOccurrenceMV.number_of_occurrences),
                )
            )
            .limit(limit_words)
        )
    )

    df = await db.run_sync(query_to_pandas_df, tf_idf_count_query)
    fig = px.bar(
        df,
        x="score",
        y="word",
        facet_col="rank_type",
        facet_row="article_name",
        orientation="h",
        facet_row_spacing=0.002,
        facet_col_spacing=0.10,
    )

    for row in range(1, number_of_articles + 1):
        fig.update_yaxes(showticklabels=True, matches=f"y{(row - 1) * 2 + 1}", title=None, row=row)

    annotations = []
    col_tf_idf = 1
    col_count = 2

    for fig_annotation in list(fig.layout.annotations):
        if "article_name=" in fig_annotation.text:
            fig_annotation.x = 0
            fig_annotation.y = fig_annotation.y + 0.005
            fig_annotation.textangle = 0
            fig_annotation.text = fig_annotation.text.split("=")[-1]
            fig_annotation.font = {"size": 14, "color": "green"}
            annotations.append(fig_annotation)

        if fig_annotation.text == "rank_type=TF-IDF":
            col_tf_idf = 1 if fig_annotation.x < 0.5 else 2

        if fig_annotation.text == "rank_type=COUNT":
            col_count = 1 if fig_annotation.x < 0.5 else 2

    fig.update_layout(annotations=annotations, height=20000, width=1800)

    for row in range(1, number_of_articles + 1):
        fig.add_annotation(
            {
                "text": "COUNT",
                "font": {"size": 14, "color": "red"},
                "textangle": 0,
                "x": 1,
                "y": 1,
                "showarrow": False,
                "xref": "x domain",
                "yanchor": "top",
                "yref": "y domain",
            },
            row=row,
            col=col_count,
        )

        fig.add_annotation(
            {
                "text": "TF-IDF",
                "font": {"size": 14, "color": "red"},
                "textangle": 0,
                "x": 1,
                "y": 1,
                "showarrow": False,
                "xref": "x domain",
                "yanchor": "top",
                "yref": "y domain",
            },
            row=row,
            col=col_tf_idf,
        )

    return fig.to_html()


@text_analytics_router.get("/order-by-postgres", response_class=HTMLResponse)
async def get_order_by_plot(
    db: AsyncSession = Depends(get_db),
):
    writer_id = await db.scalar(select(Writer.writer_id).where(Writer.email == "user+medium_data@example.com"))

    df = await db.run_sync(
        query_to_pandas_df,
        select(Article.article_id, Article.article_name, ArticleTermOccurrenceMV.word)
        .distinct(Article.article_id)
        .join(Article, ArticleTermOccurrenceMV.article_id == Article.article_id)
        .where(Article.writer_id == writer_id)
        .order_by(Article.article_id, desc(ArticleTermOccurrenceMV.number_of_occurrences)),
    )

    fig = px.bar(
        df, y="word", color="article_name", title="""Most used word per article - Distinct On""", orientation="h"
    )
    fig.update_yaxes(categoryorder="category descending")
    return fig.to_html()

    # using row_number with filter
    # article_word_subquery = (
    #     select(
    #         Article.article_name,
    #         ArticleTermOccurrenceMV.word,
    #         func.row_number().over(partition_by=[ArticleTermOccurrenceMV.article_id],
    #                                order_by=desc(ArticleTermOccurrenceMV.number_of_occurrences)).label("row_number")
    #     )
    #     .join(Article, ArticleTermOccurrenceMV.article_id == Article.article_id)
    #     .where(Article.writer_id == writer_id)
    # ).subquery("article_word_subquery")
    #
    # df = await db.run_sync(
    #     query_to_pandas_df,
    #     select(article_word_subquery).where(article_word_subquery.c.row_number==1))
    # fig = px.bar(
    #     df,
    #     y="word",
    #     color="article_name",
    #     title=f"""Most used word per article - Subquery""",
    #     orientation="h"
    # )
    # fig.update_yaxes(categoryorder='category descending')
    # return fig.to_html()

    # using row_number with limit
    # df = await db.run_sync(
    #     query_to_pandas_df,
    #     select(Article.article_name, ArticleTermOccurrenceMV.word, ArticleTermOccurrenceMV.number_of_occurrences)
    #     .join(Article, ArticleTermOccurrenceMV.article_id == Article.article_id)
    #     .where(Article.writer_id == writer_id)
    #     .order_by(
    #         func.row_number().over(
    #             partition_by=ArticleTermOccurrenceMV.article_id,
    #             order_by=desc(ArticleTermOccurrenceMV.number_of_occurrences),
    #         )
    #     )
    #     .limit(96),
    # )
    # fig = px.bar(
    #     df, y="word", color="article_name", title="""Most used word per article - Order By""", orientation="h"
    # )
    # fig.update_yaxes(categoryorder="category descending")
    # return fig.to_html()

    # Not working (see https://github.com/duckdb/pg_duckdb/discussions/155)
    # await db.execute(text("SET duckdb.execution TO true"))
    #
    # query = text(
    #     """select * from duckdb.query('SELECT fastapi_article.article_name,
    #    term_occurrence_per_article_mv.word,
    #    term_occurrence_per_article_mv.number_of_occurrences
    #     FROM term_occurrence_per_article_mv
    #              JOIN fastapi_article
    #                  ON term_occurrence_per_article_mv.article_id = fastapi_article.article_id
    #     QUALIFY row_number()
    #              OVER (
    #                     PARTITION BY term_occurrence_per_article_mv.article_id
    #                     ORDER BY term_occurrence_per_article_mv.number_of_occurrences DESC
    #              ) = 1') as (article_name text, word text, number_of_occurrences integer)"""
    # )
    #
    # df = await db.run_sync(
    #     query_to_pandas_df,
    #     query)
    #
    # fig = px.bar(
    #     df,
    #     y="word",
    #     color="article_name",
    #     title=f"""Most used word per article - Order By""",
    #     orientation="h"
    # )
    # fig.update_yaxes(categoryorder='category descending')
