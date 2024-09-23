FROM --platform=linux/amd64 python:3.12-alpine as base

RUN apk update

RUN pip install poetry
RUN pip install --upgrade pip

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install --no-root --no-ansi --without dev

ENV PATH="/.venv/bin:$PATH"

COPY ./tado .

CMD [“poetry run python”, “./main.py”]