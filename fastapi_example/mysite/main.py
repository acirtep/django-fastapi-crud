import logging

from fastapi import FastAPI

from mysite.articles.api import articles_router
from mysite.writers.api import writers_router

logger = logging.getLogger(__name__)

app = FastAPI(swagger_ui_parameters={"displayRequestDuration": True})

app.include_router(writers_router, prefix="/api/v1/fastapi")
app.include_router(articles_router, prefix="/api/v1/fastapi")
