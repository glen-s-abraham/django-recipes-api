FROM python:3.7-alpine

#run python in unbuffered mode recomended in docker
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt 

RUN pip install -r /requirements.txt
RUN mkdir /app
WORKDIR /app
COPY ./app /app

#security purposes(default account is root.so new user with limited privilages is required) 
RUN adduser -D user
USER user





