from datetime import datetime
from datetime import timezone

import pytest
from httpx import ASGITransport
from httpx import AsyncClient
from pydantic import UUID4
from sqlalchemy import select

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.database import SessionLocal
from mysite.main import app
from mysite.writers.models import Writer
from mysite.writers.models import WriterPartnerProgram


@pytest.mark.asyncio(scope="session")
class TestWriter:

    async def writer_id(self) -> UUID4:
        async with SessionLocal() as db:
            writer_obj = await db.scalar(select(Writer).where(Writer.email == "user@example.com"))
            if not writer_obj:
                writer_obj = Writer(first_name="string", last_name="string", email="user@example.com", about="me")
                db.add(writer_obj)
                await db.commit()
                await db.refresh(writer_obj)

        return writer_obj.writer_id

    async def partner_program_id(self) -> None:
        writer_id = await self.writer_id()
        async with SessionLocal() as db:
            partner_program_obj = await db.scalar(
                select(WriterPartnerProgram).where(WriterPartnerProgram.writer_id == writer_id)
            )
            if not partner_program_obj:
                partner_program_obj = WriterPartnerProgram(
                    writer_id=writer_id, country_code="AB", payment_method="STRIPE"
                )
                db.add(partner_program_obj)
                await db.commit()
                await db.refresh(partner_program_obj)

    async def test_create_conflict(self):
        await self.writer_id()
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.post(
                "/api/v1/fastapi/writers",
                json={"first_name": "string", "last_name": "string", "email": "user@example.com", "about": "string"},
            )

        assert response.status_code == 409

    async def test_create_ok(self):
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.post(
                "/api/v1/fastapi/writers",
                json={"first_name": "string", "last_name": "string", "email": "user1@example.com", "about": "string"},
            )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["first_name"] == "string"
        assert response_data["joined_timestamp"]
        assert response_data["writer_id"]
        assert not response_data["partner_program_status"]

    async def test_update(self):
        writer_id = await self.writer_id()
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.put(
                f"/api/v1/fastapi/writers/{writer_id}",
                json={
                    "first_name": "string new",
                    "last_name": "string",
                    "email": "user@example.com",
                    "about": "string",
                },
            )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["first_name"] == "string new"

    async def test_list(self):
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get("/api/v1/fastapi/writers")
        assert response.status_code == 200
        assert len(response.json()) == 4

    async def test_get(self):
        writer_id = await self.writer_id()
        await self.partner_program_id()

        async with SessionLocal() as db:
            article_published_1_obj = Article(
                article_name="Main published article",
                writer_id=writer_id,
                date_first_published=datetime.now().astimezone(tz=timezone.utc),
                article_status=ArticleStatus.published.value,
            )
            db.add(article_published_1_obj)
            db.add(
                Article(
                    article_name="Main draft article",
                    writer_id=writer_id,
                    article_status=ArticleStatus.draft.value,
                )
            )
            article_published_2_obj = Article(
                article_name="First published article",
                writer_id=writer_id,
                date_first_published=datetime.now().astimezone(tz=timezone.utc),
                article_status=ArticleStatus.published.value,
                members_only_flag=True,
            )
            db.add(article_published_2_obj)

            await db.commit()
            await db.refresh(article_published_1_obj)
            await db.refresh(article_published_2_obj)

        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(f"/api/v1/fastapi/writers/{writer_id}")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["writer_id"] == str(writer_id)
        assert response_data["partner_program_status"]
        assert response_data["articles"][0] == {
            "article_id": str(article_published_2_obj.article_id),
            "article_name": article_published_2_obj.article_name,
            "members_only_flag": article_published_2_obj.members_only_flag,
        }
        assert response_data["articles"][1] == {
            "article_id": str(article_published_1_obj.article_id),
            "article_name": article_published_1_obj.article_name,
            "members_only_flag": article_published_1_obj.members_only_flag,
        }

    async def test_delete(self):
        writer_id = await self.writer_id()
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.delete(f"/api/v1/fastapi/writers/{writer_id}")
        assert response.status_code == 200

        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(f"/api/v1/fastapi/writers/{writer_id}")
        assert response.status_code == 404

    async def test_update_partner_program(self):
        writer_id = await self.writer_id()
        await self.partner_program_id()

        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.post(
                f"/api/v1/fastapi/writers/partner-program/{writer_id}",
                json={"active": False, "country_code": "AB", "payment_method": "abcd"},
            )

        assert response.status_code == 200

        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(f"/api/v1/fastapi/writers/{writer_id}")
        assert not response.json()["partner_program_status"]
