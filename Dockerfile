# pull official base image
FROM continuumio/miniconda3:4.10.3p0-alpine

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0


# install psycopg2
RUN apk update \
    && apk add --no-cache --virtual build-essential gcc g++ libffi-dev musl-dev gfortran lapack-dev\
    && apk add postgresql-dev \
    && pip install psycopg2

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN conda install -c kumatea tensorflow

# copy project
COPY . .

RUN python manage.py collectstatic --noinput

# add and run as non-root user
RUN adduser -D myuser
USER myuser