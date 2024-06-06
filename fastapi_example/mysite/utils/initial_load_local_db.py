import asyncio
import random
import string

from sqlalchemy import select

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.database import SessionLocal
from mysite.writers.models import Writer
from mysite.writers.models import WriterPartnerProgram


async def initial_load():
    async with SessionLocal() as db:
        writer_id = await db.scalar(select(Writer.writer_id).where(Writer.email == "user+initialload@example.com"))
        if not writer_id:
            writer_obj = Writer(
                first_name="FastAPI", last_name="Writer", email="user+initialload@example.com", about="me"
            )
            db.add(writer_obj)
            await db.commit()
            await db.refresh(writer_obj)
            writer_id = writer_obj.writer_id

        writer_partner_program_obj = await db.scalar(
            select(WriterPartnerProgram).where(WriterPartnerProgram.writer_id == writer_id)
        )
        if not writer_partner_program_obj:
            writer_partner_program_obj = WriterPartnerProgram(
                writer_id=writer_id, payment_method="stripe", country_code="NL"
            )
            db.add(writer_partner_program_obj)
            await db.commit()
            await db.refresh(writer_partner_program_obj)

        article_1_obj = await db.scalar(
            select(Article).where(Article.article_name == "Test 1 article", Article.writer_id == writer_id)
        )
        if not article_1_obj:
            article_1_obj = Article(
                article_name="Test 1 article",
                article_content="".join(random.choice(string.ascii_lowercase) for i in range(200)),
                writer_id=writer_id,
                article_status=ArticleStatus.published.value,
                members_only_flag=True,
            )
            db.add(article_1_obj)
            await db.commit()
            await db.refresh(article_1_obj)

        article_2_obj = await db.scalar(
            select(Article).where(Article.article_name == "Test 2 article", Article.writer_id == writer_id)
        )
        if not article_2_obj:
            article_2_obj = Article(
                article_name="Test 2 article",
                article_content="".join(random.choice(string.ascii_lowercase) for i in range(200)),
                writer_id=writer_id,
                article_status=ArticleStatus.published.value,
                members_only_flag=True,
            )
            db.add(article_2_obj)
            await db.commit()
            await db.refresh(article_2_obj)

        article_3_obj = await db.scalar(
            select(Article).where(Article.article_name == "Test 3 article", Article.writer_id == writer_id)
        )
        if not article_3_obj:
            article_3_obj = Article(
                article_name="Test 3 article",
                article_content="".join(random.choice(string.ascii_lowercase) for i in range(200)),
                writer_id=writer_id,
                article_status=ArticleStatus.published.value,
                members_only_flag=True,
            )
            db.add(article_3_obj)
            await db.commit()
            await db.refresh(article_3_obj)


if __name__ == "__main__":
    asyncio.run(initial_load())
