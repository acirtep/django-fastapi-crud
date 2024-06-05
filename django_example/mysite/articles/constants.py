from django.db import models


class ArticleStatus(models.TextChoices):
    draft = "DRAFT"
    published = "PUBLISHED"
