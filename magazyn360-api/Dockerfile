ARG REGISTRY_PYTHON_IMAGE=python:3.13-slim-bullseye
FROM ${REGISTRY_PYTHON_IMAGE}

ARG BUILD_DATE
ARG CURRENT_BRANCH
ARG BUILD_VERSION
ARG REPOSITORY

LABEL org.opencontainers.image.authors="aleksander.bialka@icloud.com"

LABEL org.label-schema.schema-version="1.0" \
      org.label-schema.name="Magazyn360-api" \
      org.label-schema.description="Magazyn360-API" \
      org.label-schema.url="https://${REPOSITORY}/magazyn360" \
      org.label-schema.vcs-url="https://${REPOSITORY}/magazyn360" \
      org.label-schema.vcs-ref="${CURRENT_BRANCH}" \
      org.label-schema.build-date="${BUILD_DATE}"

VOLUME /var/log/magazyn360
SHELL ["/bin/bash", "-c"]

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes \
    build-essential libpq-dev gcc g++ make libffi-dev \
    libssl-dev python3-dev python3-pip python3-setuptools \
    python3-wheel git supervisor curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

RUN mkdir -p /var/www/magazyn360/app/magazyn360-api/
RUN python3 -m venv /var/www/magazyn360/app/magazyn360_env/

COPY ./pyproject.toml /var/www/magazyn360/app/magazyn360-api/
COPY ./poetry.lock /var/www/magazyn360/app/magazyn360-api/
COPY ./README.md /var/www/magazyn360/app/magazyn360-api/
COPY ./manage.py /var/www/magazyn360/app/magazyn360-api/
COPY ./magazyn360 /var/www/magazyn360/app/magazyn360-api/magazyn360/
COPY ./apps /var/www/magazyn360/app/magazyn360-api/apps/
COPY ./docs /var/www/magazyn360/app/magazyn360-api/docs/
RUN ls -la /var/www/magazyn360/app/magazyn360-api/*

WORKDIR /var/www/magazyn360/app/magazyn360-api/

RUN source /var/www/magazyn360/app/magazyn360_env/bin/activate \
    && pip install --default-timeout=1000 --no-cache-dir --upgrade pip \
    && pip install poetry==1.8.5
RUN source /var/www/magazyn360/app/magazyn360_env/bin/activate \
    && poetry config virtualenvs.create false \
    && cd /var/www/magazyn360/app/magazyn360-api/ \
    && poetry install
RUN source /var/www/magazyn360/app/magazyn360_env/bin/activate && python manage.py collectstatic --noinput

CMD ["/var/www/magazyn360/app/magazyn360_env/bin/gunicorn", "magazyn360.wsgi:application", "--bind", "0.0.0.0:8000"]
