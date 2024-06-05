from ninja import NinjaAPI

from mysite.articles.api import articles_router
from mysite.writers.api import writers_router

api = NinjaAPI()

api.add_router("/api/v1/django/writers", writers_router)
api.add_router("/api/v1/django/articles", articles_router)
