FROM python:3.8-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-dev \
    && rm -rf /root/.cache/pip

COPY . /app/
