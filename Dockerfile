FROM python:3.11.10-alpine3.20
LABEL maintainer="ottolindholmplay@gmail.com"

ENV PYTHONBUFFERED 1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

USER my_user
