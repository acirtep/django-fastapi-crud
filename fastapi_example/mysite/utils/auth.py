import logging

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import APIKeyHeader
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mysite.database import get_db
from mysite.writers.models import Writer

api_bearer_token = HTTPBearer(auto_error=False)
api_key = APIKeyHeader(name="key", auto_error=False)

logger = logging.getLogger(__file__)


async def authenticate_writer(token=Depends(api_bearer_token), db: AsyncSession = Depends(get_db)) -> Writer:
    writer_obj = await db.scalar(select(Writer).where(Writer.writer_id == token.credentials))
    if not writer_obj:
        raise HTTPException(status_code=401, detail="You are not know to us")

    return writer_obj


async def authenticate_public_user(key: str = Depends(api_key)) -> dict:
    match key:
        case "public":
            return {"medium_member": False}
        case "thisshouldbeatoken":
            return {"medium_member": True}
        case _:
            raise HTTPException(status_code=401, detail="unknown")


async def authenticate_user(
    public_api_key: str = Depends(api_key), writer_token=Depends(api_bearer_token), db: AsyncSession = Depends(get_db)
):
    if public_api_key:
        return await authenticate_public_user(key=public_api_key)

    if writer_token:
        return await authenticate_writer(token=writer_token, db=db)

    raise HTTPException(status_code=401, detail="unknown")
