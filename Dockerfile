FROM python:3.7-alpine

#run python in unbuffered mode recomended in docker
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --updat --no-cache --virtual .temp-build-deps \
    gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .temp-build-deps 
RUN mkdir /app
WORKDIR /app
COPY ./app /app

#security purposes(default account is root.so new user with limited privilages is required) 
RUN adduser -D user
USER user





