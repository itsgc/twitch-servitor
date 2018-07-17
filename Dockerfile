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
ADD . /code

RUN cat $creds > $secretsfile
ENV SETTINGS_FILE=$settingsfile
ENV SECRETS_FILE=$secretsfile

RUN ls /code/creds.yml
RUN pip install -r /code/requirements.txt
ENTRYPOINT ["uwsgi", "--ini", "/code/uwsgi.ini"]