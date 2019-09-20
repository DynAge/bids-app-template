# editme: change this file as needed
# Use the latest Python 3 docker image
FROM python:3 as base

MAINTAINER Flywheel <support@flywheel.io>

RUN apt-get update && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
    apt-get install -y \
    zip \
    nodejs \
    tree && \
    rm -rf /var/lib/apt/lists/* 
# The last line above is to help keep the docker image smaller

RUN npm install -g bids-validator@1.3.0

RUN pip install flywheel-sdk==9.0.2 \
        flywheel-bids==0.8.0 \
        psutil==5.6.3 && \
    rm -rf /var/lib/apt/lists/*
# could add pybids
# The last line above is to help keep the docker image smaller

# Save docker environ
RUN python -c 'import os, json; f = open("/tmp/gear_environ.json", "w"); json.dump(dict(os.environ), f)' 

# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Copy executable/manifest to Gear
COPY run.py ${FLYWHEEL}/run.py
COPY utils ${FLYWHEEL}/utils
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY test.sh ${FLYWHEEL}/test.sh

# Configure entrypoint
RUN chmod a+x ${FLYWHEEL}/run.py
ENTRYPOINT ["/flywheel/v0/run.py"]
