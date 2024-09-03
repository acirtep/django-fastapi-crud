import asyncio
import glob
import multiprocessing
import os.path
from datetime import datetime
from datetime import timezone
from pathlib import Path

import bs4
from pydantic import UUID4
from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import text

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.database import SessionLocal
from mysite.text_analytics.models import ArticleTermOccurrenceMV
from mysite.text_analytics.models import CorpusTermOccurrenceMV
from mysite.writers.models import Writer


def get_article_object(writer_id: UUID4, article: str) -> Article:
    with open(article) as article_file:
        soup = bs4.BeautifulSoup(article_file, "html.parser")
        # remove the pre tags (used for code snippets)
        for s in soup("pre"):
            s.decompose()
        # remove the footer tag
        for s in soup("footer"):
            s.decompose()

        article_file_name = os.path.basename(article)
        article_content = soup.text.replace("\n", " ").replace("\t", " ")
        return Article(
            article_name=article_file_name.replace(".html", "")[11:].rsplit("-", 1)[0].replace("-", " ").strip(),
            article_content=article_content,
            writer_id=writer_id,
            article_status=ArticleStatus.published.value,
            members_only_flag=True,
            date_created=datetime.fromisoformat(article_file_name.replace(".html", "")[:10]).astimezone(
                tz=timezone.utc
            ),
            date_first_published=datetime.fromisoformat(article_file_name.replace(".html", "")[:10]).astimezone(
                tz=timezone.utc
            ),
        )


async def get_article_objects(writer_id: UUID4) -> list[dict]:
    start_datetime = datetime.now()
    medium_articles_directory = f"{Path(__file__).parent.parent.parent}/medium_data/"
    medium_articles_path = glob.glob(f"{medium_articles_directory}*.html")

    pool = multiprocessing.Pool(processes=4)

    results = [pool.apply_async(get_article_object, args=(writer_id, article)) for article in medium_articles_path]

    pool.close()
    pool.join()
    article_objects = [r.get() for r in results]

    end_datetime = datetime.now()

    print(f"Parsing medium files took {(end_datetime - start_datetime).total_seconds() * 1000} ms")

    return article_objects


async def get_writer() -> UUID4:
    async with SessionLocal() as db:
        writer_id = await db.scalar(select(Writer.writer_id).where(Writer.email == "user+medium_data@example.com"))
        if not writer_id:
            writer_obj = Writer(
                first_name="Medium", last_name="Writer", email="user+medium_data@example.com", about="me"
            )
            db.add(writer_obj)
            await db.commit()
            await db.refresh(writer_obj)
            writer_id = writer_obj.writer_id

    return writer_id


async def validate_term_occurrence_mv():
    async with SessionLocal() as db:
        print(
            f"""Number of records in {CorpusTermOccurrenceMV.__tablename__}: {
                await db.scalar(select(func.count(CorpusTermOccurrenceMV.word)))
            }"""
        )
        print(
            f"""Number of records in {ArticleTermOccurrenceMV.__tablename__}: {
                await db.scalar(select(func.count(ArticleTermOccurrenceMV.article_id)))
            }"""
        )

        corpus_query = select(
            CorpusTermOccurrenceMV.word,
            CorpusTermOccurrenceMV.number_of_occurrences,
            CorpusTermOccurrenceMV.number_of_articles,
        )
        article_query = select(
            ArticleTermOccurrenceMV.word,
            func.sum(ArticleTermOccurrenceMV.number_of_occurrences),
            func.count(ArticleTermOccurrenceMV.article_id),
        ).group_by(ArticleTermOccurrenceMV.word)

        corpus_vs_article_subquery = corpus_query.except_(article_query).subquery()
        print(
            f"""Number of records {CorpusTermOccurrenceMV.__tablename__} vs {ArticleTermOccurrenceMV.__tablename__}: {
                await db.scalar(select(func.count(corpus_vs_article_subquery.c.word)))
            }"""
        )

        article_vs_corpus_subquery = article_query.except_(corpus_query).subquery()

        print(
            f"""Number of records {ArticleTermOccurrenceMV.__tablename__} vs {CorpusTermOccurrenceMV.__tablename__}: {
                await db.scalar(select(func.count(article_vs_corpus_subquery.c.word)))
            }"""
        )


async def load_articles(writer_id: UUID4, article_objects: list[Article]):
    start_datetime = datetime.now()

    async with SessionLocal() as db:
        await db.execute(delete(Article).where(Article.writer_id == writer_id))

        db.add_all(article_objects)
        await db.commit()

        end_datetime = datetime.now()

        print(f"Loading articles took {(end_datetime - start_datetime).total_seconds() * 1000} ms")

        await db.execute(text(f"refresh materialized view {CorpusTermOccurrenceMV.__tablename__}"))
        await db.commit()
        await db.execute(text(f"refresh materialized view {ArticleTermOccurrenceMV.__tablename__}"))
        await db.commit()
        await validate_term_occurrence_mv()


async def load_medium_data():
    start_datetime = datetime.now()
    writer_id = await get_writer()
    article_objects = await get_article_objects(writer_id=writer_id)
    await load_articles(writer_id=writer_id, article_objects=article_objects)
    end_datetime = datetime.now()

    print(f"Parsing and loading articles took {(end_datetime-start_datetime).total_seconds()*1000} ms")


if __name__ == "__main__":
    asyncio.run(load_medium_data())
