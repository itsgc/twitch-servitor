FROM ubuntu:16.04


RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get -qq -y install python python-pip && \
    apt-get -qq -y install build-essential && \
    apt-get -qq -y install uwsgi && \
    apt-get -qq -y update && \
    apt-get clean

RUN mkdir /code
WORKDIR /code
ADD . /code
ADD $credsfile /code

RUN pip install -r /code/requirements.txt
ENTRYPOINT ["uwsgi", "--ini", "/code/uwsgi.ini"]