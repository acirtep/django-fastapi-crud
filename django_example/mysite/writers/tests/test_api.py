from datetime import datetime
from datetime import timezone

from django.test import TestCase
from ninja.testing import TestAsyncClient

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.writers.api import writers_router
from mysite.writers.models import Writer
from mysite.writers.models import WriterPartnerProgram


class TestWriter(TestCase):

    def setUp(self) -> None:
        self.client = TestAsyncClient(writers_router)

        self.writer_obj = Writer.objects.create(
            first_name="string", last_name="string", email="user@example.com", about="me"
        )

        self.partner_program = WriterPartnerProgram.objects.create(
            writer_id=self.writer_obj.writer_id, country_code="AB", payment_method="STRIPE"
        )

    async def test_create_conflict(self):

        response = await self.client.post(
            "", json={"first_name": "string", "last_name": "string", "email": "user@example.com", "about": "string"}
        )
        assert response.status_code == 409

    async def test_create_ok(self):

        response = await self.client.post(
            "", json={"first_name": "string", "last_name": "string", "email": "user1@example.com", "about": "string"}
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["first_name"] == "string"
        assert response_data["joined_timestamp"]
        assert response_data["writer_id"]
        assert not response_data["partner_program_status"]

    async def test_update(self):

        response = await self.client.put(
            f"/{self.writer_obj.writer_id}",
            json={"first_name": "string new", "last_name": "string", "email": "user@example.com", "about": "string"},
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["first_name"] == "string new"

    async def test_list(self):
        response = await self.client.get("")
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_get(self):
        article_published_1_obj = await Article.objects.acreate(
            article_name="Main published article",
            writer_id=self.writer_obj.writer_id,
            date_first_published=datetime.now().astimezone(tz=timezone.utc),
            article_status=ArticleStatus.published,
        )
        await Article.objects.acreate(
            article_name="Main draft article", writer_id=self.writer_obj.writer_id, article_status=ArticleStatus.draft
        )

        article_published_2_obj = await Article.objects.acreate(
            article_name="First published article",
            writer_id=self.writer_obj.writer_id,
            date_first_published=datetime.now().astimezone(tz=timezone.utc),
            article_status=ArticleStatus.published,
            members_only_flag=True,
        )

        response = await self.client.get(f"/{self.writer_obj.writer_id}")
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["writer_id"] == str(self.writer_obj.writer_id)
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
        response = await self.client.delete(f"/{self.writer_obj.writer_id}")
        assert response.status_code == 200

        response = await self.client.get(f"/{self.writer_obj.writer_id}")
        assert response.status_code == 404

    async def test_update_partner_program(self):
        response = await self.client.post(
            f"/partner-program/{self.writer_obj.writer_id}",
            json={"active": False, "country_code": "AB", "payment_method": "abcd"},
        )
        assert response.status_code == 200

        response = await self.client.get(f"/{self.writer_obj.writer_id}")
        assert not response.json()["partner_program_status"]
