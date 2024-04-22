from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from mysite.database import get_db
from mysite.medium_writers.models import Writer
from mysite.medium_writers.schemas import WriterInSchema
from mysite.medium_writers.schemas import WriterOutSchema

medium_writers_router = APIRouter(prefix="/api/v1/medium-writers")


@medium_writers_router.post("", response_model=WriterOutSchema)
async def create_writer(input_data: WriterInSchema, db: Session = Depends(get_db)):
    writer_obj = Writer(
        first_name=input_data.first_name,
        last_name=input_data.last_name,
        email=input_data.email,
        about=input_data.about,
    )
    db.add(writer_obj)
    db.commit()
    db.refresh(writer_obj)

    return writer_obj
