FROM python:3.12.3-slim-bookworm

# configure and argument to point to the path of the source code to copy and install
ARG SOURCE_CODE_PATH=$SOURCE_CODE_PATH

RUN apt update -y  \
    && apt install -y --no-install-recommends build-essential libpq-dev

WORKDIR /app

COPY ./README.md .
COPY ./$SOURCE_CODE_PATH .

RUN pip3 install poetry==1.8.2

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

RUN groupadd -r django-fastapi-crud && useradd -ms /bin/bash -g django-fastapi-crud django-fastapi-crud
