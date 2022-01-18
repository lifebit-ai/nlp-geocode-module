FROM python:3.9

WORKDIR /usr/src/app

# set python path to include working directory
ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app"

ENV PHOTON_SERVER=test
ENV GEONAMES_SERVER=test

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the content of the local src directory to the working directory
COPY . .

RUN pip install .
