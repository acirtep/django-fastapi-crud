from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from mysite.database import get_db
from mysite.medium_writers.models import Writer
from mysite.medium_writers.models import WriterPartnerProgram
from mysite.medium_writers.schemas import WriterInSchema
from mysite.medium_writers.schemas import WriterOutSchema
from mysite.medium_writers.schemas import WriterPartnerProgramInSchema

medium_writers_router = APIRouter(prefix="/medium-writers")


@medium_writers_router.post("", response_model=WriterOutSchema)
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


@medium_writers_router.get("", response_model=List[WriterOutSchema])
async def list_writers(db: AsyncSession = Depends(get_db)):
    return await db.scalars(select(Writer).order_by(Writer.joined_timestamp))


@medium_writers_router.get("/{writer_id}", response_model=WriterOutSchema)
async def get_writer(writer_id: UUID4, db: AsyncSession = Depends(get_db)):
    writer_obj = await db.scalar(
        select(Writer).options(joinedload(Writer.partner_program)).where(Writer.writer_id == writer_id)
    )
    if not writer_obj:
        raise HTTPException(status_code=404, detail="Writer not found")

    return writer_obj


@medium_writers_router.put("/{writer_id}", response_model=WriterOutSchema)
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


@medium_writers_router.delete("/{writer_id}")
async def delete_writer(writer_id: UUID4, db: AsyncSession = Depends(get_db)):
    writer_obj = await db.scalar(select(Writer).where(Writer.writer_id == writer_id))
    if not writer_obj:
        raise HTTPException(status_code=404, detail="Writer not found")
    await db.delete(writer_obj)
    await db.commit()
    return {"success": True}


@medium_writers_router.post("/partner-program/{writer_id}")
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
