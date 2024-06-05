from django.http import Http404
from django.http import HttpRequest
from django.shortcuts import aget_object_or_404
from ninja.errors import HttpError
from ninja.security import APIKeyHeader
from ninja.security import HttpBearer

from mysite.writers.models import Writer


class AuthenticateWriter(HttpBearer):
    async def authenticate(self, request: HttpRequest, token: str) -> Writer:
        """
        Authentication class, never use the id as the token in production. This is just a learning code base.
        Checkout JWT tokens or 3rd parties for authentication services.

        :param request: the http request
        :param token: the id of the writer
        :return:
            the writer object
        """
        try:
            return await aget_object_or_404(Writer, writer_id=token)
        except Http404 as error:
            raise HttpError(status_code=401, message="you are not known to us") from error


class AuthenticateUser(APIKeyHeader):
    async def authenticate(self, request: HttpRequest, key: str) -> dict:
        """
        Authentication class for general access. This is just a learning code base.

        :param request: the http request
        :param key: api key
        :return:
            validate if the user exists registered in a potential User table
        """

        match key:
            case "public":
                return {"medium_member": False}
            case "thisshouldbeatoken":
                return {"medium_member": True}
            case _:
                raise HttpError(status_code=401, message="unknown")
