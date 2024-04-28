FROM alpine:latest

RUN apk update
RUN apk add --no-cache python3-dev py3-pip gdb

ENV PIP_BREAK_SYSTEM_PACKAGES 1

COPY ./app/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

# Emplacement réseau des conteneurs de la stack
ENV MYSQL_SERVICE_NAME=ade-mysql
ENV MONGO_SERVICE_NAME=ade-mongodb
ENV PARSER_SERVICE_NAME=ade-python-parser
ENV APP_MODE=prod

# Fix des prints qui ne s'affichent pas correctement
ENV PYTHONUNBUFFERED=1

COPY ./app /app
ENTRYPOINT ["python3", "main.py"]