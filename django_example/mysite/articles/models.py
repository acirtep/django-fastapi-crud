from django.contrib.postgres.functions import RandomUUID
from django.db import models
from django.db.models import CASCADE
from django.db.models.functions import Now

from mysite.articles.constants import ArticleStatus
from mysite.writers.models import Writer


class Article(models.Model):

    article_id = models.UUIDField(
        primary_key=True,
        db_default=RandomUUID(),
        db_comment="unique identifier of the article",
    )

    article_name = models.CharField(null=False, blank=False, db_comment="the content of the article")
    article_content = models.TextField(null=True, db_comment="the content of the article")

    date_created = models.DateTimeField(
        db_default=Now(), db_comment="the date time in UTC, when the article was created"
    )
    date_updated = models.DateTimeField(null=True, db_comment="the date time in UTC, when the article was update")
    date_first_published = models.DateTimeField(
        null=True, db_comment="the date time in UTC, when the article was published the first time"
    )
    article_status = models.CharField(
        db_default=ArticleStatus.draft,
        null=False,
        choices=ArticleStatus.choices,
        db_comment="the status of the article",
    )
    members_only_flag = models.BooleanField(
        db_default=False, null=False, db_comment="true if it is a members only article"
    )

    writer = models.ForeignKey(
        to=Writer, on_delete=CASCADE, related_name="articles", db_comment="the writer of the article"
    )

    class Meta:
        db_table = "django_article"
        db_table_comment = "general information about articles"
