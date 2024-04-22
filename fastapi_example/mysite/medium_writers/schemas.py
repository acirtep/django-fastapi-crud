from datetime import datetime

from pydantic import UUID4
from pydantic import BaseModel
from pydantic import Field


class WriterInSchema(BaseModel):
    first_name: str | None = Field(None, description="the first name of the writer")
    last_name: str | None = Field(None, description="the last name of the writer")
    email: str = Field(..., description="the email of the writer")
    about: str | None = Field(None, description="a short intro of the writer")


class WriterOutSchema(BaseModel):
    writer_id: UUID4 = Field(..., description="unique identifier of the writer")
    first_name: str | None = Field(None, description="the first name of the writer")
    last_name: str | None = Field(None, description="the last name of the writer")
    email: str = Field(..., description="the email of the writer")
    about: str | None = Field(None, description="a short intro of the writer")
    joined_timestamp: datetime = Field(
        ..., description="the date time in UTC, when the writer joined"
    )
