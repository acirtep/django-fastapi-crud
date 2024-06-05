from datetime import datetime

from ninja import Schema
from pydantic import UUID4
from pydantic import EmailStr
from pydantic import Field


class WriterInSchema(Schema):
    first_name: str | None = Field(None, description="the first name of the writer")
    last_name: str | None = Field(None, description="the last name of the writer")
    email: EmailStr = Field(..., description="the email of the writer")
    about: str | None = Field(None, description="a short intro of the writer")


class WriterPartnerProgramInSchema(Schema):
    country_code: str = Field(..., description="the country iso code of the writer", max_length=2)
    payment_method: str = Field("STRIPE", description="the payment method of the partner program, eg: stripe")
    active: bool = Field(True, description="true if the partner program is active")


class WriterOutSchema(Schema):
    writer_id: UUID4 = Field(..., description="unique identifier of the writer")
    first_name: str | None = Field(None, description="the first name of the writer")
    last_name: str | None = Field(None, description="the last name of the writer")
    email: str = Field(..., description="the email of the writer")
    about: str | None = Field(None, description="a short intro of the writer")
    joined_timestamp: datetime = Field(..., description="the date time in UTC, when the writer joined")
    partner_program_status: bool | None = Field(None, description="the partner program status of the writer")


class ArticleOutSchema(Schema):
    article_id: UUID4 | None = Field(None, description="unique identifier of the article")
    article_name: str | None = Field(None, description="the name of the article")
    members_only_flag: bool | None = Field(None, description="true if it is a members only article")


class WriterExtendedOutSchema(WriterOutSchema):
    articles: list[ArticleOutSchema] | None = Field(None, description="last 2 published articles")
