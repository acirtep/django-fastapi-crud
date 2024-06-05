from datetime import datetime

from pydantic import UUID4
from pydantic import BaseModel
from pydantic import Field

from mysite.articles.constants import ArticleStatus


class ArticleInSchema(BaseModel):
    article_name: str = Field(..., description="the name of the article")
    article_content: str | None = Field(None, description="the content of the article")
    members_only_flag: bool | None = Field(False, description="true if it is a members only article")


class ArticleOutSchema(BaseModel):
    article_id: UUID4 = Field(..., description="unique identifier of the article")
    writer_id: UUID4 = Field(..., description="unique identifier of the writer")
    article_name: str = Field(..., description="the name of the article")
    article_content: str | None = Field(None, description="the content of the article")
    article_status: ArticleStatus = Field(..., description="the status of the article")
    date_first_published: datetime | None = Field(None, description="the date the article was published the first time")
    members_only_flag: bool = Field(..., description="true if it is a members only article")


class WriterOutSchema(BaseModel):
    first_name: str | None = Field(None, description="the first name of the writer")
    last_name: str | None = Field(None, description="the last name of the writer")
    about: str | None = Field(None, description="a short intro of the writer")


class ArticleExtendedOutSchema(ArticleOutSchema):
    writer: WriterOutSchema = Field(..., description="information about the writer of the article")
