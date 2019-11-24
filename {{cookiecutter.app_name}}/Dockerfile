FROM python:3.8-alpine

MAINTAINER {{cookiecutter.author_email}}

# Arguments
ARG server_host="{{cookiecutter.server_host}}"
ARG server_port={{cookiecutter.server_port}}
ARG db_host="{{cookiecutter.db_host}}"
ARG db_port={{cookiecutter.db_port}}
ARG db_user="{{cookiecutter.db_user}}"
ARG db_name="{{cookiecutter.db_name}}"
ARG db_schema="{{cookiecutter.db_schema}}"

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

# Setup environment and run application
ENV SERVER_HOST $server_host
ENV SERVER_PORT $server_port
ENV DB_HOST $db_host
ENV DB_PORT $db_port
ENV DB_NAME $db_name
ENV DB_USER $db_user

EXPOSE $SERVER_PORT

ENTRYPOINT ["python", "{{cookiecutter.app_name}}/app.py"]