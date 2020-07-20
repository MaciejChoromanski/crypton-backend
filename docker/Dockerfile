# Dockerfile for development

FROM python:3.8-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /crypton
WORKDIR /crypton
COPY ./ /crypton

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev
RUN pip install virtualenv \
    && virtualenv venv \
    && source venv/bin/activate
RUN pip install -r requirements.txt
RUN apk del .tmp-build-deps

ENTRYPOINT ["./docker/entrypoint.sh"]
