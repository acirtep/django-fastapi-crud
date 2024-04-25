from ninja import NinjaAPI

from mysite.writers.api import writers_router

api = NinjaAPI()

api.add_router("/api/v1/django/writers", writers_router)
