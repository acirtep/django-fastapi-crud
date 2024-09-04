import random
import string

import pytest
from httpx import ASGITransport
from httpx import AsyncClient
from pydantic import UUID4
from sqlalchemy import select

from mysite.database import SessionLocal
from mysite.main import app
from mysite.writers.models import Writer


@pytest.mark.asyncio(scope="session")
class TestTextAnalytics:
    async def writer_1_id(self) -> UUID4:
        async with SessionLocal() as db:
            writer_obj = await db.scalar(select(Writer).where(Writer.email == "user+1@example.com"))
            if not writer_obj:
                writer_obj = Writer(first_name="string", last_name="string", email="user+1@example.com", about="me")
                db.add(writer_obj)
                await db.commit()
                await db.refresh(writer_obj)

        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.post(
                "/api/v1/fastapi/articles",
                json={
                    "article_name": "Dummy article",
                    "article_content": "".join(random.choice(string.ascii_lowercase) for i in range(200)),
                    "members_only_flag": True,
                },
                headers={"Authorization": f"Bearer {str(writer_obj.writer_id)}"},
            )
            response.raise_for_status()

        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.post(
                "/api/v1/fastapi/articles",
                json={
                    "article_name": "Dummy article",
                    "article_content": "".join(random.choice(string.ascii_lowercase) for i in range(200)),
                    "members_only_flag": True,
                },
                headers={"Authorization": f"Bearer {str(writer_obj.writer_id)}"},
            )
            response.raise_for_status()

        return writer_obj.writer_id

    async def test_get_writer_content_length(self):
        writer_id = await self.writer_1_id()
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(
                f"/api/v1/fastapi/text-analytics/writer-content-length/{writer_id}",
            )

        assert response.status_code == 200

    async def test_get_writer_most_used_words(self):
        writer_id = await self.writer_1_id()
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(
                f"/api/v1/fastapi/text-analytics/writer-stats-most-user-words/{writer_id}",
            )

        assert response.status_code == 200

    async def test_get_wordcloud(self):
        async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
            response = await client.get(
                "/api/v1/fastapi/text-analytics/wordcloud",
            )

        assert response.status_code == 404
