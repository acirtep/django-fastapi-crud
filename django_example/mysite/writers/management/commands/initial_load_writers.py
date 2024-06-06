from django.core.management.base import BaseCommand

from mysite.writers.models import Writer
from mysite.writers.models import WriterPartnerProgram


class Command(BaseCommand):
    help = "Initial load writer on local environment"

    def handle(self, *args, **options):
        writer_obj, _ = Writer.objects.get_or_create(
            first_name="Django", last_name="Writer", email="user+initialload@example.com", about="me"
        )
        WriterPartnerProgram.objects.get_or_create(
            writer_id=writer_obj.writer_id, payment_method="stripe", country_code="NL"
        )
