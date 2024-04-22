from django.contrib.postgres.functions import RandomUUID
from django.db import models
from django.db.models.functions import Now


class Writer(models.Model):

    writer_id = models.UUIDField(
        primary_key=True,
        db_default=RandomUUID(),
        db_comment="unique identifier of the writer",
    )
    first_name = models.CharField(db_comment="the first name of the writer", null=True)
    last_name = models.CharField(db_comment="the last name of the writer", null=True)
    email = models.EmailField(
        unique=True, db_comment="the email of the writer", null=False
    )
    about = models.CharField(db_comment="a short intro of the writer", null=True)
    joined_timestamp = models.DateTimeField(
        db_default=Now(), db_comment="the date time in UTC, when the writer joined"
    )

    class Meta:
        db_table = "django_writer"
        db_table_comment = "general information about writers"


class WriterPartnerProgram(models.Model):
    # more on one-to-one fields https://docs.djangoproject.com/en/5.0/ref/models/fields/#onetoonefield
    writer = models.OneToOneField(
        Writer,
        primary_key=True,
        db_comment="unique identifier of the writer",
        on_delete=models.CASCADE,
    )
    joined_timestamp = models.DateTimeField(
        db_default=Now(),
        db_comment="the date time in UTC, when the writer joined the partner program",
    )
    payment_method = models.CharField(
        db_comment="the payment method of the partner program"
    )
    writer_country_code = models.CharField(
        db_comment="the country iso code of the writer"
    )

    class Meta:
        db_table = "django_partner_program"
        db_table_comment = "information about partner program at writer level"
