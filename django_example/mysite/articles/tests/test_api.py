import random
import string
import uuid

from django.db.models import Count
from django.test import TestCase
from mysite.articles.api import articles_router
from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.articles.schemas import TagInSchema
from mysite.writers.models import Writer
from ninja.testing import TestAsyncClient, TestClient
from pydantic import ValidationError


class TestArticle(TestCase):

    def setUp(self) -> None:
        self.client = TestAsyncClient(articles_router)

        self.sync_client = TestClient(articles_router)

        self.writer_1_obj = Writer.objects.create(
            first_name="string", last_name="string", email="user+1@example.com", about="me"
        )

        self.article_obj = Article.objects.create(
            article_name="Main test for article",
            article_content="".join(random.choice(string.ascii_lowercase) for i in range(200)),
            writer_id=self.writer_1_obj.writer_id,
            members_only_flag=True,
        )

        self.writer_2_obj = Writer.objects.create(
            first_name="string", last_name="string", email="user+2@example.com", about="me"
        )

    async def test_create_ok(self):

        response = await self.client.post(
            "",
            json={
                "article_name": "Dummy article",
                "article_content": "this is a dummy article",
            },
            headers={"Authorization": f"Bearer {self.writer_1_obj.writer_id}"},
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["article_id"]
        assert response_data["writer_id"] == str(self.writer_1_obj.writer_id)
        assert response_data["article_name"] == "Dummy article"
        assert response_data["article_status"] == ArticleStatus.draft
        assert not response_data["members_only_flag"]

    async def test_get_article_unauthenticated_unknown_bearer_token(self):
        response = await self.client.get(
            f"{self.article_obj.article_id}", headers={"Authorization": f"Bearer {uuid.uuid4()}"}
        )

        assert response.status_code == 401

    async def test_get_article_unauthenticated_unknown_key(self):
        response = await self.client.get(f"{self.article_obj.article_id}", headers={"key": "whatever"})

        assert response.status_code == 401

    async def test_get_article_unauthenticated_no_token(self):
        response = await self.client.get(f"{self.article_obj.article_id}")

        assert response.status_code == 401

    async def test_get_article_ok_writer(self):
        response = await self.client.get(
            f"{self.article_obj.article_id}", headers={"Authorization": f"Bearer {self.writer_1_obj.writer_id}"}
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["article_id"] == str(self.article_obj.article_id)
        assert response_data["writer"] == {
            "first_name": self.writer_1_obj.first_name,
            "last_name": self.writer_1_obj.last_name,
            "about": self.writer_1_obj.about,
        }

    async def test_get_article_unauthorized_another_writer(self):
        response = await self.client.get(
            f"{self.article_obj.article_id}", headers={"Authorization": f"Bearer {self.writer_2_obj.writer_id}"}
        )
        assert response.status_code == 403

    async def test_get_article_ok_no_user(self):
        self.article_obj.article_status = ArticleStatus.published
        await self.article_obj.asave()
        response = await self.client.get(f"{self.article_obj.article_id}", headers={"key": "public"})

        assert response.status_code == 200
        assert len(response.json()["article_content"]) == 100

    async def test_get_article_ok_member_user(self):
        self.article_obj.article_status = ArticleStatus.published
        await self.article_obj.asave()

        response = await self.client.get(f"{self.article_obj.article_id}", headers={"key": "thisshouldbeatoken"})
        assert response.status_code == 200
        assert len(response.json()["article_content"]) == len(self.article_obj.article_content)

    async def test_tags_schema_incorrect_length(self):
        tags = []
        for i in range(6):
            tags.append({"tag_name": "".join(random.choice(string.ascii_lowercase) for i in range(10))})

        with self.assertRaises(ValidationError):
            TagInSchema(tags=tags)

    async def test_tags_schema_duplicate_tags(self):
        tags = [{"tag_name": "tag name"}, {"tag_name": "tag name"}]
        with self.assertRaises(ValidationError):
            TagInSchema(tags=tags)

    async def test_tags_schema_ok(self):
        tags = [{"tag_name": "tag name 1"}, {"tag_name": "tag name 2  "}]
        validated_tags = TagInSchema(tags=tags)
        assert validated_tags.tags[0].tag_name == "Tag Name 1"
        assert validated_tags.tags[1].tag_name == "Tag Name 2"

    def test_add_tags_to_article_ok(self):
        tags = []
        for i in range(5):
            tags.append({"tag_name": "".join(random.choice(string.ascii_lowercase) for i in range(10))})
        response = self.sync_client.put(
            f"{self.article_obj.article_id}/tags",
            headers={"Authorization": f"Bearer {self.writer_1_obj.writer_id}"},
            json={"tags": tags},
        )
        assert response.status_code == 200

        assert (
            Article.objects.filter(article_id=self.article_obj.article_id)
            .annotate(cnt_tags=Count("tags"))
            .values_list("cnt_tags", flat=True)[0]
            == 5
        )
