FROM python:3.13-slim-bullseye

RUN mkdir -p /etc/magazyn360 && mkdir /var/log/magazyn360 && mkdir /usr/src/magazyn360

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes \
    build-essential libpq-dev gcc g++ make libffi-dev \
    libssl-dev python3-dev python3-pip python3-setuptools \
    python3-wheel git supervisor curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*


WORKDIR /usr/src/magazyn360-api

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root

COPY . .

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
