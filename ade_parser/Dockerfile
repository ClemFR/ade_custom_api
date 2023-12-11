FROM alpine:latest

RUN apk update
RUN apk add --no-cache python3-dev py3-pip

ENV PIP_BREAK_SYSTEM_PACKAGES 1

COPY ./app/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

ENV ADE_URL=""
ENV SELENIUM_HOST=localhost
ENV SELENIUM_PORT=4444
ENV MONGO_DATABASE_HOST=localhost
ENV MONGO_DATABASE_PORT=27017
ENV MYSQL_DATABASE_HOST=localhost
ENV MYSQL_DATABASE_PORT=3306
ENV EXPOSE_PORT=5000

# Fix des prints qui ne s'affichent pas correctement
ENV PYTHONUNBUFFERED=1

COPY ./app /app
ENTRYPOINT ["python3", "main.py"]