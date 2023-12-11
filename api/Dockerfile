FROM alpine:latest

RUN apk update
RUN apk add --no-cache python3-dev py3-pip

ENV PIP_BREAK_SYSTEM_PACKAGES 1

COPY ./app/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

# Informations mongodb
ENV DATABASE_HOST=localhost
ENV DATABASE_PORT=27017
ENV APP_MODE=prod

# Fix des prints qui ne s'affichent pas correctement
ENV PYTHONUNBUFFERED=1

COPY ./app /app
ENTRYPOINT ["python3", "main.py"]