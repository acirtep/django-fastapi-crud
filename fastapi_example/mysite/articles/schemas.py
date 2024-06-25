from datetime import datetime
from string import capwords
from typing import Annotated

from pydantic import UUID4
from pydantic import AfterValidator
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator
from pydantic_core import PydanticCustomError

from mysite.articles.constants import ArticleStatus


def string_to_capwords(input_string: str | None) -> str | None:
    if not input_string:
        return None
    return capwords(input_string)


CapWordsString = Annotated[str, AfterValidator(string_to_capwords)]


class TagSchema(BaseModel):
    tag_name: CapWordsString = Field(..., max_length=70, description="The tag name")


class TagInSchema(BaseModel):
    tags: list[TagSchema] | None = Field(None, max_length=5, description="the list of tags of the article")

    @field_validator("tags")
    @classmethod
    def validate_unique_tags(cls, tags: list[TagSchema] | None) -> list[TagSchema] | None:
        if not tags:
            return None
        tag_name_list = [tag.tag_name for tag in tags]
        if len(tag_name_list) == len(set(tag_name_list)):
            return tags
        raise PydanticCustomError("unique_list", "List must be unique")


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
    tags: list[TagSchema] | None = Field(None, max_length=5, description="the list of tags of the article")
