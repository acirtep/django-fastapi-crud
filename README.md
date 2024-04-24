# About

This repository is created to show-case how data models, APIs and unit testing are developed in Django Ninja and FastAPI.

The scope of it is for learning purposes only and it is the base for the following Medium articles:

1. [Django and FastAPI: Introduction](https://medium.com/@petrica.leuca/7a2b55c7da27?sk=6db4c4e36c5adce6e052f6cee1844d5d)
2. [Django and FastAPI: One To One Relationships](https://medium.com/@petrica.leuca/4ea1f11b8986?source=friends_link&sk=1287df230b6ed4f9d759ed60e97208ab)


Pre-requisites:
1. docker
2. docker-compose


# Django

Django docs: https://www.djangoproject.com/

Django Ninja docs: https://django-ninja.dev/

1. `make django_app`, to run the app at http://0.0.0.0:3000
2. `make django_test`, to execute the tests


# FastAPI

FastAPI docs: https://fastapi.tiangolo.com/

SQLAlchemy docs: https://docs.sqlalchemy.org/en/20/

Alembic: https://alembic.sqlalchemy.org/en/latest/

1. `make fastapi_app`, to run the app at http://0.0.0.0:3001
2. `make fastapi_test`, to execute the tests

# Others
- Pydantic docs: https://docs.pydantic.dev/latest/
- run `make check` for formatting
