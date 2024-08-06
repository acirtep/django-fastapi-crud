from fastapi import APIRouter, Depends
from mysite.database import get_db, query_to_pandas_df
from pydantic import UUID4
from sqlalchemy import select, func, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse

from mysite.articles.models import Article
from mysite.writers.models import Writer

text_analytics_router = APIRouter(prefix="/text-analytics")

import plotly.express as px


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
        f"""select word, ndoc, nentry
            from ts_stat($${query.compile(dialect=postgresql.dialect(), compile_kwargs={'literal_binds': True})}$$)
            order by nentry desc
            limit 20
            """
    )
    article_df = await db.run_sync(query_to_pandas_df, ts_stat)

    fig = px.bar(
        article_df,
        y="nentry",
        x="ndoc",
        color="word",
        title=f"""Top 20 most used words by {writer_obj.first_name} {writer_obj.last_name}""",
        labels={"ndoc": "Number of documents", "nentry": "Number of occurrences"},
    )

    return fig.to_html()
