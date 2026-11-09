# syntax=docker/dockerfile:1

FROM python:3.12-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip wheel --wheel-dir /wheels .


FROM python:3.12-slim-bookworm AS runtime

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --gid 10001 raceops \
    && useradd \
        --uid 10001 \
        --gid raceops \
        --no-create-home \
        --home-dir /nonexistent \
        --shell /usr/sbin/nologin \
        raceops

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN python -m pip install \
        --no-index \
        --find-links=/wheels \
        raceops \
    && rm -rf /wheels

COPY --chown=raceops:raceops alembic.ini ./
COPY --chown=raceops:raceops migrations ./migrations

USER raceops

EXPOSE 8000

CMD ["uvicorn", "raceops.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
