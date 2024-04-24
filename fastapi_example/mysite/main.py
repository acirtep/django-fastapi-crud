from fastapi import FastAPI

from mysite.medium_writers.api import medium_writers_router

app = FastAPI()

app.include_router(medium_writers_router, prefix="/api/v1/fastapi")
