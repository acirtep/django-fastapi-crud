import random
import string

from django.core.management.base import BaseCommand
from django.db import transaction

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.articles.models import Tag
from mysite.writers.models import Writer


class Command(BaseCommand):
    help = "Initial load writer on local environment"

    def handle(self, *args, **options):
        with transaction.atomic():
            writer_obj, _ = Writer.objects.get_or_create(
                first_name="Django", last_name="Writer", email="user+initialload@example.com", about="me"
            )

            tag_1_obj, _ = Tag.objects.get_or_create(tag_name="Tag Name 1")
            tag_2_obj, _ = Tag.objects.get_or_create(tag_name="Tag Name 2")

            if not Article.objects.filter(article_name="Test 1 article", writer_id=writer_obj.writer_id).first():
                article_obj = Article.objects.create(
                    article_name="Test 1 article",
                    article_content="".join(random.choice(string.ascii_lowercase) for i in range(200)),
                    writer=writer_obj,
                    article_status=ArticleStatus.published,
                    members_only_flag=True,
                )
                article_obj.tags.add(tag_1_obj, tag_2_obj)

            if not Article.objects.filter(article_name="Test 2 article", writer_id=writer_obj.writer_id).first():
                article_obj = Article.objects.create(
                    article_name="Test 2 article",
                    article_content="".join(random.choice(string.ascii_lowercase) for i in range(200)),
                    writer=writer_obj,
                    article_status=ArticleStatus.published,
                    members_only_flag=True,
                )
                article_obj.tags.add(tag_1_obj)

            if not Article.objects.filter(article_name="Test 3 article", writer_id=writer_obj.writer_id).first():
                article_obj = Article.objects.create(
                    article_name="Test 3 article",
                    article_content="".join(random.choice(string.ascii_lowercase) for i in range(200)),
                    writer=writer_obj,
                    article_status=ArticleStatus.published,
                    members_only_flag=True,
                )
                article_obj.tags.add(tag_2_obj)
