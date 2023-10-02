FROM python:latest
RUN groupadd -r user && useradd -r --create-home --home-dir /home/user -g user user
ADD ./requirements.txt .
RUN pip3 install -r requirements.txt
#ADD ./dbexport.pgsql /docker-entrypoint-initdb.d

RUN mkdir ./src
ADD ./src /src
WORKDIR src
USER user