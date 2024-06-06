from ninja import NinjaAPI
from ninja import Swagger

from mysite.articles.api import articles_router
from mysite.writers.api import writers_router

api = NinjaAPI(docs=Swagger(settings={"displayRequestDuration": True}))

api.add_router("/api/v1/django/writers", writers_router)
api.add_router("/api/v1/django/articles", articles_router)
