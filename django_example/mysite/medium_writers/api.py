from typing import List

from asgiref.sync import sync_to_async
from django.shortcuts import aget_object_or_404
from ninja import Router
from ninja.errors import HttpError
from pydantic import UUID4

from mysite.medium_writers.models import Writer
from mysite.medium_writers.models import WriterPartnerProgram
from mysite.medium_writers.schemas import WriterInSchema
from mysite.medium_writers.schemas import WriterOutSchema
from mysite.medium_writers.schemas import WriterPartnerProgramInSchema

medium_writers_router = Router()


@medium_writers_router.post("", response=WriterOutSchema)
async def create_writer(request, input_data: WriterInSchema):
    writer_obj = await Writer.objects.filter(email=input_data.email).afirst()
    if writer_obj:
        raise HttpError(status_code=409, message="Email already used!")

    return await Writer.objects.acreate(
        first_name=input_data.first_name, last_name=input_data.last_name, email=input_data.email, about=input_data.about
    )


@medium_writers_router.get("", response=List[WriterOutSchema])
async def list_writers(request):
    return await sync_to_async(list)(Writer.objects.all().order_by("joined_timestamp"))


@medium_writers_router.get("/{writer_id}", response=WriterOutSchema)
async def get_writer(request, writer_id: UUID4):
    return await aget_object_or_404(Writer, writer_id=writer_id)


@medium_writers_router.put("/{writer_id}", response=WriterOutSchema)
async def update_writer(request, writer_id: UUID4, input_data: WriterInSchema):
    writer_obj = await Writer.objects.filter(email=input_data.email).exclude(writer_id=writer_id).afirst()
    if writer_obj:
        raise HttpError(status_code=409, message="Email already used!")

    writer_obj = await aget_object_or_404(Writer, writer_id=writer_id)

    writer_obj.first_name = input_data.first_name
    writer_obj.last_name = input_data.last_name
    writer_obj.about = input_data.about
    writer_obj.email = input_data.email

    await writer_obj.asave()

    return writer_obj


@medium_writers_router.delete("/{writer_id}")
async def delete_writer(request, writer_id: UUID4):
    writer_obj = await aget_object_or_404(Writer, writer_id=writer_id)
    await writer_obj.adelete()

    return {"success": True}


@medium_writers_router.post("/partner-program/{writer_id}")
async def update_partner_program(request, writer_id: UUID4, input_data: WriterPartnerProgramInSchema):
    await WriterPartnerProgram.objects.aupdate_or_create(
        writer_id=writer_id,
        defaults={
            "country_code": input_data.country_code,
            "payment_method": input_data.payment_method,
            "active": input_data.active,
        },
    )

    return {"success": True}
