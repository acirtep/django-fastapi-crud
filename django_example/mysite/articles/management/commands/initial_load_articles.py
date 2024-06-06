import random
import string

from django.core.management.base import BaseCommand

from mysite.articles.constants import ArticleStatus
from mysite.articles.models import Article
from mysite.writers.models import Writer


class Command(BaseCommand):
    help = "Initial load writer on local environment"

    def handle(self, *args, **options):
        writer_obj, _ = Writer.objects.get_or_create(
            first_name="Django", last_name="Writer", email="user+initialload@example.com", about="me"
        )

        if not Article.objects.filter(article_name="Test 1 article", writer_id=writer_obj.writer_id).first():
            Article.objects.create(
                article_name="Test 1 article",
                article_content="".join(random.choice(string.ascii_lowercase) for i in range(200)),
                writer=writer_obj,
                article_status=ArticleStatus.published,
                members_only_flag=True,
            )

        if not Article.objects.filter(article_name="Test 2 article", writer_id=writer_obj.writer_id).first():
            Article.objects.create(
                article_name="Test 2 article",
                article_content="".join(random.choice(string.ascii_lowercase) for i in range(200)),
                writer=writer_obj,
                article_status=ArticleStatus.published,
                members_only_flag=True,
            )

        if not Article.objects.filter(article_name="Test 3 article", writer_id=writer_obj.writer_id).first():
            Article.objects.create(
                article_name="Test 3 article",
                article_content="".join(random.choice(string.ascii_lowercase) for i in range(200)),
                writer=writer_obj,
                article_status=ArticleStatus.published,
                members_only_flag=True,
            )
