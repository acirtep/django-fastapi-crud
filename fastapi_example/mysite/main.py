import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from mysite.articles.api import articles_router
from mysite.text_analytics.api import text_analytics_router
from mysite.writers.api import writers_router


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s | %(message)s | %(filename)s:%(lineno)d")
logger = logging.getLogger(__name__)

app = FastAPI(swagger_ui_parameters={"displayRequestDuration": True})

app.include_router(writers_router, prefix="/api/v1/fastapi")
app.include_router(articles_router, prefix="/api/v1/fastapi")
app.include_router(text_analytics_router, prefix="/api/v1/fastapi")


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse("http://0.0.0.0:3011/docs")


logger.info("Running at http://0.0.0.0:3011")
