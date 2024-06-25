from asgiref.sync import async_to_sync
from django.db import transaction
from django.shortcuts import aget_object_or_404
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from pydantic import UUID4

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.articles.models import Tag
from mysite.articles.schemas import ArticleExtendedOutSchema
from mysite.articles.schemas import ArticleInSchema
from mysite.articles.schemas import ArticleOutSchema
from mysite.articles.schemas import TagInSchema
from mysite.utils.auth import AuthenticateUser
from mysite.utils.auth import AuthenticateWriter
from mysite.writers.models import Writer

articles_router = Router()


@articles_router.post("", response=ArticleOutSchema, auth=AuthenticateWriter())
async def create_article(request, input_data: ArticleInSchema):
    return await Article.objects.acreate(
        article_name=input_data.article_name,
        article_content=input_data.article_content,
        members_only_flag=input_data.members_only_flag,
        writer_id=request.auth.writer_id,
    )


@async_to_sync
@articles_router.put("/{article_id}/tags", auth=AuthenticateWriter())
def add_tags(request, article_id: UUID4, input_data: TagInSchema):
    with transaction.atomic():
        article_obj = get_object_or_404(Article, article_id=article_id, writer_id=request.auth.writer_id)

        article_obj.tags.clear()

        tag_name_list = [tag.tag_name for tag in input_data.tags]
        for tag_name in tag_name_list:
            Tag.objects.get_or_create(tag_name=tag_name)

        article_obj.tags.add(*Tag.objects.filter(tag_name__in=(tag_name_list)).all())

    return {"detail": "Added successfully"}


@articles_router.get(
    "/{article_id}", response=ArticleExtendedOutSchema, auth=[AuthenticateWriter(), AuthenticateUser()]
)
async def get_article(request, article_id: UUID4):
    """
    This code is intended for learning purposes, in the area of using multiple authenticators in one API.
    """
    article_obj = await aget_object_or_404(
        Article.objects.select_related("writer").prefetch_related("tags"), article_id=article_id
    )

    if isinstance(request.auth, Writer):
        if article_obj.article_status == ArticleStatus.draft and article_obj.writer_id != request.auth.writer_id:
            raise HttpError(status_code=403, message="you are not allowed to read this article")
        return article_obj
    else:
        if article_obj.article_status != ArticleStatus.published:
            raise HttpError(status_code=403, message="you are not allowed to read this article")

    if article_obj.members_only_flag and not request.auth.get("medium_member", False):
        article_obj.article_content = article_obj.article_content[:100]

    return article_obj
