from django.shortcuts import redirect
from mysite.articles.api import articles_router
from mysite.writers.api import writers_router
from ninja import NinjaAPI, Swagger

api = NinjaAPI(docs=Swagger(settings={"displayRequestDuration": True}))

api.add_router("/api/v1/django/writers", writers_router)
api.add_router("/api/v1/django/articles", articles_router)


@api.get("/", include_in_schema=False)
async def redirect_to_docs(request):
    return redirect("http://0.0.0.0:3010/docs")
