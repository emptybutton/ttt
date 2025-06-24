FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS wheel

WORKDIR /run/build
ENV UV_COMPILE_BYTECODE=1

COPY . .
RUN uv build --wheel --no-python-downloads


FROM python:3.13-slim-bookworm AS ttt

WORKDIR /run/app

COPY --from=wheel /run/build/dist dist
RUN pip install dist/* && rm dist -fr

COPY deploy/prod/ttt/alembic.ini /usr/local/lib/python3.13/site-packages/ttt
WORKDIR /usr/local/lib/python3.13/site-packages/ttt
CMD ["ttt"]
