FROM python:3.8-alpine

MAINTAINER {{cookiecutter.author_email}}

# Arguments
ARG SERVER_HOST="{{cookiecutter.server_host}}"
ARG SERVER_PORT={{cookiecutter.server_port}}
ARG DB_HOST="{{cookiecutter.db_host}}"
ARG DB_PORT={{cookiecutter.db_port}}
ARG DB_USER="{{cookiecutter.db_user}}"
ARG DB_NAME="{{cookiecutter.db_name}}"
ARG DB_SCHEMA="{{cookiecutter.db_schema}}"
ARG DB_PASSWORD=password

# Set the LANG ENV VAR
ENV LANG C.UTF-8

# Install system-wide dependencies
RUN apk add --update --no-cache \
    build-base \
    python3-dev \
    make \
    postgresql-dev

# Make sure pip is up-to date
RUN pip install --upgrade pip

# Copy the application code
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY . /app/

# Install the application
WORKDIR /app/
RUN python setup.py install

# Copy the config file to users home dir
RUN mkdir -p ~/.config/
RUN cp config/default.conf ~/.config/{{cookiecutter.app_name}}.conf

# Configure the postgresql secrets file
# Format:
#   hostname:port:database:username:password
RUN touch ~/.pgpass
RUN echo $DB_HOST:$DB_PORT:$DB_NAME:$DB_USER:$DB_PASSWORD >> ~/.pgpass
RUN chmod 600 ~/.pgpass

# Setup environment and run application
ENV SERVER_HOST $SERVER_HOST
ENV SERVER_PORT $SERVER_PORT
ENV DB_HOST $DB_HOST
ENV DB_PORT $DB_PORT
ENV DB_NAME $DB_NAME
ENV DB_USER $DB_USER

EXPOSE $SERVER_PORT

ENTRYPOINT ["python", "{{cookiecutter.app_name}}/app.py"]