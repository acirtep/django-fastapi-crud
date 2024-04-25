from fastapi import FastAPI

from mysite.writers.api import writers_router

app = FastAPI()

app.include_router(writers_router, prefix="/api/v1/fastapi")
