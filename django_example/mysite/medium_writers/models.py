from django.contrib.postgres.functions import RandomUUID
from django.db import models
from django.db.models import F
from django.db.models.functions import Now


class WriterManager(models.Manager):

    def get_queryset(self):
        return super(WriterManager, self).get_queryset().annotate(partner_program_status=F("partner_program__active"))


class Writer(models.Model):

    writer_id = models.UUIDField(
        primary_key=True,
        db_default=RandomUUID(),
        db_comment="unique identifier of the writer",
    )
    first_name = models.CharField(null=True, blank=False, db_comment="the first name of the writer")
    last_name = models.CharField(null=True, blank=False, db_comment="the last name of the writer")
    email = models.EmailField(unique=True, blank=False, db_comment="the email of the writer")
    about = models.CharField(null=True, blank=False, db_comment="a short intro of the writer")
    joined_timestamp = models.DateTimeField(db_default=Now(), db_comment="the date time in UTC, when the writer joined")

    objects = WriterManager()

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
        related_name="partner_program",
    )
    joined_timestamp = models.DateTimeField(
        db_default=Now(),
        db_comment="the date time in UTC, when the writer joined the partner program",
    )
    payment_method = models.CharField(db_comment="the payment method of the partner program")
    country_code = models.CharField(db_comment="the country iso code of the writer")
    active = models.BooleanField(db_default=True, db_comment="true if the partner program is active")

    class Meta:
        db_table = "django_partner_program"
        db_table_comment = "information about partner program at writer level"
