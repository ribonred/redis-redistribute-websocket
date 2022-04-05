FROM python:3.10-slim

RUN mkdir src
WORKDIR /src
COPY src/requirements.txt .
RUN apt-get update \
    && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -U pip && pip install -r requirements.txt \
    && apt-get purge -y --auto-remove gcc
COPY src/ .
ENTRYPOINT [ "python" ]
