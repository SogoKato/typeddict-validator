FROM python:latest

WORKDIR /app

ENV PATH "/root/.local/bin:$PATH"

COPY . .

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry install
