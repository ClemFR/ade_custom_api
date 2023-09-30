FROM alpine:latest

RUN apk update
RUN apk add --no-cache python3-dev py3-pip

COPY ./app/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt

# Informations selenium
ENV SELENIUM_HOST=localhost
ENV SELENIUM_PORT=4444

# Informations ADE
ENV ADE_JSP_URL=""
ENV ADE_LOGIN=""
ENV ADE_PASSWORD=""

ENV ADE_YEAR_ID=""

# format YYYYMMAA
ENV ADE_START_DATE=""

ENV APP_MODE=dev
ENV WORKERS_COUNT=1

COPY ./app /app
ENTRYPOINT ["python3", "main.py"]