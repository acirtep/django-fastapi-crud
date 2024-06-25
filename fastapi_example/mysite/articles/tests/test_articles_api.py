import random
import string
import uuid

import pytest
from httpx import ASGITransport
from httpx import AsyncClient
from pydantic import UUID4
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.articles.schemas import TagInSchema
from mysite.database import SessionLocal
from mysite.main import app
from mysite.writers.models import Writer


@pytest.mark.asyncio(scope="session")
class TestArticle:
    async def writer_1_id(self) -> UUID4:
        async with SessionLocal() as db:
            writer_obj = await db.scalar(select(Writer).where(Writer.email == "user+1@example.com"))
            if not writer_obj:
                writer_obj = Writer(first_name="string", last_name="string", email="user+1@example.com", about="me")
                db.add(writer_obj)
                await db.commit()
                await db.refresh(writer_obj)

        return writer_obj.writer_id

    async def writer_2_id(self) -> UUID4:
        async with SessionLocal() as db:
            writer_obj = await db.scalar(select(Writer).where(Writer.email == "user+2@example.com"))
            if not writer_obj:
                writer_obj = Writer(first_name="string", last_name="string", email="user+2@example.com", about="me")
                db.add(writer_obj)
                await db.commit()
                await db.refresh(writer_obj)

        return writer_obj.writer_id

    async def test_create_ok(self):
        writer_id = await self.writer_1_id()
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.post(
                "/api/v1/fastapi/articles",
                json={
                    "article_name": "Dummy article",
                    "article_content": "".join(random.choice(string.ascii_lowercase) for i in range(200)),
                    "members_only_flag": True,
                },
                headers={"Authorization": f"Bearer {str(writer_id)}"},
            )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["article_id"]
        assert response_data["writer_id"] == str(writer_id)
        assert response_data["members_only_flag"]
        assert response_data["article_name"] == "Dummy article"
        assert response_data["article_status"] == ArticleStatus.draft.value

    async def test_get_article_unauthenticated_unknown_bearer_token(self):
        async with SessionLocal() as db:
            article_obj = await db.scalar(select(Article).limit(1))
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(
                f"/api/v1/fastapi/articles/{article_obj.article_id}",
                headers={"Authorization": f"Bearer {uuid.uuid4()}"},
            )

        assert response.status_code == 401

    async def test_get_article_unauthenticated_unknown_key(self):
        async with SessionLocal() as db:
            article_obj = await db.scalar(select(Article).limit(1))
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(
                f"/api/v1/fastapi/articles/{article_obj.article_id}", headers={"key": "whatever"}
            )

        assert response.status_code == 401

    async def test_get_article_unauthenticated_no_token(self):
        async with SessionLocal() as db:
            article_obj = await db.scalar(select(Article).limit(1))
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(f"/api/v1/fastapi/articles/{article_obj.article_id}")

        assert response.status_code == 401

    async def test_get_article_ok_writer(self):
        async with SessionLocal() as db:
            writer_obj = await db.scalar(select(Writer).where(Writer.writer_id == await self.writer_1_id()))
            article_obj = await db.scalar(select(Article).limit(1))
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(
                f"/api/v1/fastapi/articles/{article_obj.article_id}",
                headers={"Authorization": f"Bearer {writer_obj.writer_id}"},
            )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["article_id"] == str(article_obj.article_id)
        assert response_data["writer"] == {
            "first_name": writer_obj.first_name,
            "last_name": writer_obj.last_name,
            "about": writer_obj.about,
        }

    async def test_get_article_unauthorized_another_writer(self):
        async with SessionLocal() as db:
            writer_obj = await db.scalar(select(Writer).where(Writer.writer_id == await self.writer_2_id()))
            article_obj = await db.scalar(select(Article).limit(1))
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(
                f"/api/v1/fastapi/articles/{article_obj.article_id}",
                headers={"Authorization": f"Bearer {writer_obj.writer_id}"},
            )

        assert response.status_code == 403

    async def test_get_article_ok_no_user(self):
        async with SessionLocal() as db:
            article_obj = await db.scalar(select(Article).limit(1))
            article_obj.article_status = ArticleStatus.published.value
            db.add(article_obj)
            await db.commit()
            await db.refresh(article_obj)

        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(f"/api/v1/fastapi/articles/{article_obj.article_id}", headers={"key": "public"})
        assert response.status_code == 200
        assert len(response.json()["article_content"]) == 100

    async def test_get_article_ok_member_user(self):
        async with SessionLocal() as db:
            article_obj = await db.scalar(select(Article).limit(1))
            article_obj.article_status = ArticleStatus.published.value
            db.add(article_obj)
            await db.commit()
            await db.refresh(article_obj)

        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(
                f"/api/v1/fastapi/articles/{article_obj.article_id}", headers={"key": "thisshouldbeatoken"}
            )
        assert response.status_code == 200
        assert len(response.json()["article_content"]) == len(article_obj.article_content)

    async def test_tags_schema_incorrect_length(self):
        tags = []
        for i in range(6):
            tags.append({"tag_name": "".join(random.choice(string.ascii_lowercase) for i in range(10))})

        with pytest.raises(ValidationError):
            TagInSchema(tags=tags)

    async def test_tags_schema_duplicate_tags(self):
        tags = [{"tag_name": "tag name"}, {"tag_name": "tag name"}]
        with pytest.raises(ValidationError):
            TagInSchema(tags=tags)

    async def test_tags_schema_ok(self):
        tags = [{"tag_name": "tag name 1"}, {"tag_name": "tag name 2  "}]
        validated_tags = TagInSchema(tags=tags)
        assert validated_tags.tags[0].tag_name == "Tag Name 1"
        assert validated_tags.tags[1].tag_name == "Tag Name 2"

    async def test_add_tags_to_article_ok(self):
        async with SessionLocal() as db:
            writer_obj = await db.scalar(select(Writer).where(Writer.writer_id == await self.writer_1_id()))
            article_obj = await db.scalar(select(Article).limit(1))

        tags = []
        for i in range(5):
            tags.append({"tag_name": "".join(random.choice(string.ascii_lowercase) for i in range(10))})

        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.put(
                f"/api/v1/fastapi/articles/{article_obj.article_id}/tags",
                headers={"Authorization": f"Bearer {writer_obj.writer_id}"},
                json={"tags": tags},
            )
        assert response.status_code == 200

        async with SessionLocal() as db:
            article_obj = await db.scalar(
                select(Article)
                .where(Article.article_id == article_obj.article_id)
                .options(joinedload(Article.tags, innerjoin=False))
            )
            assert len(article_obj.tags) == 5
