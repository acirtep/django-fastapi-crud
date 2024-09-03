# About

This repository is created to show-case how data models, APIs and unit testing are developed in Django Ninja and FastAPI.

The scope of it is for learning purposes only and it is the base for the following Medium articles:

1. [Django and FastAPI: Introduction](https://medium.com/@petrica.leuca/7a2b55c7da27?sk=6db4c4e36c5adce6e052f6cee1844d5d)
2. [Django and FastAPI: One To One Relationships](https://medium.com/@petrica.leuca/4ea1f11b8986?source=friends_link&sk=1287df230b6ed4f9d759ed60e97208ab)
3. [Django and FastAPI: One To Many Relationships](https://medium.com/@petrica.leuca/320602329fd2?source=friends_link&sk=1b34bd36b546ee5f32c82e3d43609517)
4. [Django and FastAPI: Many To Many Relationships](https://medium.com/@petrica.leuca/django-and-fastapi-many-to-many-relationships-4d37487d7c8a)

## Text Analytics With PostgreSQL
The FastAPI codebase is also use for data analysis of Medium articles, using the text analysis features from PostgreSQL.
If you are a medium writer, export your articles and place them under `medium_data`.
Run:
1. `make fastapi_app`
2. in another shell, `load_medium_data`

Articles:
1. [Text Analytics With PostgreSQL And SQLAlchemy - Part1](https://medium.com/@petrica.leuca/163f0c454bbe?source=friends_link&sk=0ca82c2bc4fa5ab2db127014034f7421)
2. [3 Ways To Filter On Order In PostgreSQL](https://medium.com/@petrica.leuca/63741f5912a4?sk=c468bd6386ef14b47e920ab88df3d8c1)
3. [Term Frequency With PostgreSQL] (https://medium.com/@petrica.leuca/fbe914a5de03?source=friends_link&sk=17ba92ecf785d80516ff1095392f6970)

Pre-requisites:
1. docker
2. docker-compose


# Django

Django docs: https://www.djangoproject.com/

Django Ninja docs: https://django-ninja.dev/

1. `make django_app`, to run the app at http://0.0.0.0:3010
2. `make django_test`, to execute the tests


# FastAPI

FastAPI docs: https://fastapi.tiangolo.com/

SQLAlchemy docs: https://docs.sqlalchemy.org/en/20/

Alembic: https://alembic.sqlalchemy.org/en/latest/

1. `make fastapi_app`, to run the app at http://0.0.0.0:3011
2. `make fastapi_test`, to execute the tests

# Others
- Pydantic docs: https://docs.pydantic.dev/latest/
- run `make check` for formatting
