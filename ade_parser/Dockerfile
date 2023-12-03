FROM alpine:latest

RUN apk update
RUN apk add --no-cache python3-dev py3-pip

COPY ./app/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

ENV ADE_URL=""
ENV SELENIUM_HOST=localhost
ENV SELENIUM_PORT=4444
ENV DATABASE_HOST=localhost
ENV DATABASE_PORT=27017
ENV EXPOSE_PORT=5000
ENV PYTHONUNBUFFERED=1

COPY ./app /app
ENTRYPOINT ["python3", "main.py"]