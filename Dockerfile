
FROM ubuntu:16.04

MAINTAINER Mathew Alexander 
LABEL 


RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*
RUN apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv
RUN apt-get install -y git

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel


RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Fix certificate issues
RUN apt-get update && \
    apt-get install ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f;

# Setup JAVA_HOME -- useful for docker commandline
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
RUN export JAVA_HOME



WORKDIR /pp2j

COPY . .  



RUN python3.6 -m pip install -r requirements.txt
RUN [ "python3.6", "-c", "import nltk; nltk.download('punkt')" ]
RUN [ "python3.6", "-c", "import nltk; nltk.download('stopwords')" ]

RUN gdown --id  0B6VhzidiLvjSa19uYWlLUEkzX3c




ENTRYPOINT [ "python3.6" ]

CMD [ "server.py" ]
