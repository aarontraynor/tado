FROM python:3.12-alpine AS base

RUN apk update

RUN pip install poetry
RUN pip install --upgrade pip

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install --no-root --no-ansi --without dev

ENV PATH="/.venv/bin:${PATH}"
ENV TADO_USERNAME=${TADO_USERNAME}
ENV TADO_PASSWORD=${TADO_PASSWORD}

COPY ./tado .

ENTRYPOINT ["poetry", "run", "python", "./main.py"]