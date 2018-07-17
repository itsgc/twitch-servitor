FROM ubuntu:16.04


RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get -qq -y install python python-pip && \
    apt-get -qq -y install build-essential && \
    apt-get -qq -y install uwsgi && \
    apt-get -qq -y update && \
    apt-get clean

ARG creds
ARG settingsfile
ARG secretsdir
ARG secretsfile

RUN mkdir /code
RUN mkdir $secretsdir
WORKDIR /code
COPY --chown=www-data:www-data . /code

ENV SETTINGS_FILE=$settingsfile
ENV SECRETS_FILE=$secretsfile

RUN pip install -r /code/requirements.txt
ENTRYPOINT ["uwsgi", "--uid", "www-data", "--gid", "www-data", "--ini", "/code/uwsgi.ini"]