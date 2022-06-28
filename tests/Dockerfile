FROM python:3.9

WORKDIR /usr/src/app

ARG CODECOV_TOKEN
ARG GITHUB_API_TOKEN
ARG GITHUB_USER_NAME

ENV CODECOV_TOKEN $CODECOV_TOKEN
ENV GITHUB_API_TOKEN $GITHUB_API_TOKEN
ENV GITHUB_USER_NAME $GITHUB_USER_NAME

#Install gh cli
ARG GH_VERSION=2.13.0
RUN apt-get install wget && \
    wget https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz && \
    tar -zxvf gh_${GH_VERSION}_linux_amd64.tar.gz && \
    chmod +x gh_${GH_VERSION}_linux_amd64/bin/gh && \
    cp gh_${GH_VERSION}_linux_amd64/bin/gh /bin

# set python path to include working directory
ENV PYTHONPATH="${PYTHONPATH}:/usr/src/app"

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the content of the local src directory to the working directory
COPY . .

RUN pip install .
