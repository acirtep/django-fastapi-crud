import logging
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.ext.asyncio import AsyncSession

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.database import get_db
from mysite.writers.models import Writer
from mysite.writers.models import WriterPartnerProgram
from mysite.writers.schemas import WriterExtendedOutSchema
from mysite.writers.schemas import WriterInSchema
from mysite.writers.schemas import WriterOutSchema
from mysite.writers.schemas import WriterPartnerProgramInSchema

logger = logging.getLogger(__name__)

writers_router = APIRouter(prefix="/writers")


@writers_router.post("", response_model=WriterOutSchema)
async def create_writer(input_data: WriterInSchema, db: AsyncSession = Depends(get_db)):
    writer_obj = await db.scalar(select(Writer).where(Writer.email == input_data.email))
    if writer_obj:
        raise HTTPException(status_code=409, detail="Email already used!")

    writer_obj = Writer(
        first_name=input_data.first_name,
        last_name=input_data.last_name,
        email=input_data.email,
        about=input_data.about,
    )
    db.add(writer_obj)
    await db.commit()
    await db.refresh(writer_obj)

    return writer_obj


@writers_router.get("", response_model=List[WriterOutSchema])
async def list_writers(db: AsyncSession = Depends(get_db)):
    return await db.scalars(select(Writer).order_by(Writer.joined_timestamp))


@writers_router.get("/{writer_id}", response_model=WriterExtendedOutSchema)
async def get_writer(writer_id: UUID4, db: AsyncSession = Depends(get_db)):
    article_subquery = (
        select(
            Article.article_id,
            Article.writer_id,
            Article.article_name,
            Article.members_only_flag,
            Article.date_first_published,
        )
        .where(Article.writer_id == writer_id, Article.article_status == ArticleStatus.published.value)
        .order_by(Article.date_first_published.desc())
        .limit(2)
    ).subquery("article_subquery")

    writer_obj = (
        await db.execute(
            select(
                Writer.writer_id,
                Writer.first_name,
                Writer.last_name,
                Writer.email,
                Writer.about,
                Writer.joined_timestamp,
                WriterPartnerProgram.active.label("partner_program_status"),
                func.array_agg(
                    aggregate_order_by(
                        func.jsonb_build_object(
                            "article_id",
                            article_subquery.c.article_id,
                            "article_name",
                            article_subquery.c.article_name,
                            "members_only_flag",
                            article_subquery.c.members_only_flag,
                        ),
                        desc(article_subquery.c.date_first_published),
                    )
                ).label("articles"),
            )
            .join(WriterPartnerProgram, WriterPartnerProgram.writer_id == Writer.writer_id, isouter=True)
            .join(article_subquery, article_subquery.c.writer_id == Writer.writer_id, isouter=True)
            .where(Writer.writer_id == writer_id)
            .group_by(Writer, WriterPartnerProgram.writer_id, WriterPartnerProgram.active)
        )
    ).first()
    if not writer_obj:
        raise HTTPException(status_code=404, detail="Writer not found")

    return writer_obj


@writers_router.put("/{writer_id}", response_model=WriterOutSchema)
async def update_writer(writer_id: UUID4, input_data: WriterInSchema, db: AsyncSession = Depends(get_db)):
    writer_obj = await db.scalar(select(Writer).where(Writer.email == input_data.email, Writer.writer_id != writer_id))
    if writer_obj:
        raise HTTPException(status_code=409, detail="Email already used by!")

    writer_obj = await db.scalar(select(Writer).where(Writer.writer_id == writer_id))
    if not writer_obj:
        raise HTTPException(status_code=404, detail="Writer not found")

    writer_obj.first_name = input_data.first_name
    writer_obj.last_name = input_data.last_name
    writer_obj.about = input_data.about
    writer_obj.email = input_data.email

    db.add(writer_obj)
    await db.commit()
    await db.refresh(writer_obj)

    return writer_obj


@writers_router.delete("/{writer_id}")
async def delete_writer(writer_id: UUID4, db: AsyncSession = Depends(get_db)):
    writer_obj = await db.scalar(select(Writer).where(Writer.writer_id == writer_id))
    if not writer_obj:
        raise HTTPException(status_code=404, detail="Writer not found")
    await db.delete(writer_obj)
    await db.commit()
    return {"success": True}


@writers_router.post("/partner-program/{writer_id}")
async def update_partner_program(
    writer_id: UUID4, input_data: WriterPartnerProgramInSchema, db: AsyncSession = Depends(get_db)
):
    writer_program_partner_obj = await db.scalar(
        select(WriterPartnerProgram).where(WriterPartnerProgram.writer_id == writer_id)
    )

    if not writer_program_partner_obj:
        writer_program_partner_obj = WriterPartnerProgram(
            writer_id=writer_id,
            country_code=input_data.country_code,
            payment_method=input_data.payment_method,
            active=input_data.active,
        )
    else:
        writer_program_partner_obj.country_code = input_data.country_code
        writer_program_partner_obj.payment_method = input_data.payment_method
        writer_program_partner_obj.active = input_data.active
    db.add(writer_program_partner_obj)
    await db.commit()
    return {"success": True}
