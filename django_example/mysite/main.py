from ninja import NinjaAPI

from mysite.medium_writers.api import medium_writers_router

api = NinjaAPI()

api.add_router("/api/v1/django/medium-writers", medium_writers_router)
