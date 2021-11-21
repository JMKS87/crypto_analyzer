FROM python:3.9-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev build-base

ARG UID
ARG GID

# Create a group and user
RUN addgroup -S appuser && adduser -S appuser -G appuser

#RUN groupadd -g ${GID} appuser \
#    && useradd -m -u ${UID} -g appuser appuser

WORKDIR /app

RUN mkdir -p django_cache && chown appuser:appuser django_cache

COPY --chown=appuser:appuser requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY --chown=appuser:appuser . /app

USER appuser
