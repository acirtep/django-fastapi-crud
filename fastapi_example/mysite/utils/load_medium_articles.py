import glob
import os.path
from datetime import datetime, timezone
from pathlib import Path

import asyncio

from pydantic import UUID4
from sqlalchemy import select, delete

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.database import SessionLocal
from mysite.writers.models import Writer
import bs4
import multiprocessing


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


async def get_article_objects(writer_id: UUID4) -> list[Article]:
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


async def load_articles(writer_id: UUID4, article_objects: list[Article]):
    start_datetime = datetime.now()

    async with SessionLocal() as db:
        await db.execute(delete(Article).where(Article.writer_id == writer_id))

        db.add_all(article_objects)
        await db.commit()

        # await db.execute(pg_insert(Article).values(article_objects).on_conflict_do_nothing())

    end_datetime = datetime.now()

    print(f"Loading articles took {(end_datetime-start_datetime).total_seconds()*1000} ms")


async def load_medium_data():
    start_datetime = datetime.now()
    writer_id = await get_writer()
    article_objects = await get_article_objects(writer_id=writer_id)
    await load_articles(writer_id=writer_id, article_objects=article_objects)
    end_datetime = datetime.now()

    print(f"Parsing and loading articles took {(end_datetime-start_datetime).total_seconds()*1000} ms")


if __name__ == "__main__":
    asyncio.run(load_medium_data())
