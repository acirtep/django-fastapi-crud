import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.articles.models import ArticleTags
from mysite.articles.models import Tag
from mysite.articles.schemas import ArticleExtendedOutSchema
from mysite.articles.schemas import ArticleInSchema
from mysite.articles.schemas import ArticleOutSchema
from mysite.articles.schemas import TagInSchema
from mysite.database import get_db
from mysite.utils.auth import authenticate_user
from mysite.utils.auth import authenticate_writer
from mysite.writers.models import Writer

articles_router = APIRouter(prefix="/articles")
logger = logging.getLogger(__file__)


@articles_router.post("", response_model=ArticleOutSchema)
async def create_article(
    input_data: ArticleInSchema, auth: Writer = Depends(authenticate_writer), db: AsyncSession = Depends(get_db)
):
    article_obj = Article(
        article_name=input_data.article_name,
        article_content=input_data.article_content,
        members_only_flag=input_data.members_only_flag,
        writer_id=auth.writer_id,
    )
    db.add(article_obj)
    await db.commit()
    await db.refresh(article_obj)

    return article_obj


@articles_router.put("/{article_id}/tags")
async def add_tags(
    article_id: UUID4, input_data: TagInSchema, auth=Depends(authenticate_writer), db: AsyncSession = Depends(get_db)
):
    article_obj = await db.scalar(
        select(Article)
        .options(joinedload(Article.writer, innerjoin=True))
        .options(joinedload(Article.tags, innerjoin=False))
        .where(Article.article_id == article_id)
    )

    if not article_obj:
        raise HTTPException(status_code=404, detail="Article not found")

    await db.execute(delete(ArticleTags).where(ArticleTags.article_id == article_id))

    tag_name_list = [tag.tag_name for tag in input_data.tags]
    for tag_name in tag_name_list:
        tag_obj = await db.scalar(select(Tag).where(Tag.tag_name == tag_name))
        if not tag_obj:
            tag_obj = Tag(tag_name=tag_name)
            db.add(tag_obj)

        article_obj.tags.append(tag_obj)
    db.add(article_obj)

    await db.commit()

    return {"detail": "Added successfully"}


@articles_router.get("/{article_id}", response_model=ArticleExtendedOutSchema)
async def get_article(article_id: UUID4, auth=Depends(authenticate_user), db: AsyncSession = Depends(get_db)):
    """
    This code is intended for learning purposes, in the area of using multiple authenticators in one API.
    """
    article_obj = await db.scalar(
        select(Article)
        .options(joinedload(Article.writer, innerjoin=True))
        .options(joinedload(Article.tags, innerjoin=False))
        .where(Article.article_id == article_id)
    )
    if not article_obj:
        raise HTTPException(status_code=404, detail="Article not found")

    if isinstance(auth, Writer):
        if article_obj.article_status == ArticleStatus.draft.value and article_obj.writer_id != auth.writer_id:
            raise HTTPException(status_code=403, detail="you are not allowed to read this article")
        return article_obj
    else:
        if article_obj.article_status != ArticleStatus.published.value:
            raise HTTPException(status_code=403, detail="you are not allowed to read this article")

    if article_obj.members_only_flag and not auth.get("medium_member", False):
        article_obj.article_content = article_obj.article_content[:100]

    return article_obj
