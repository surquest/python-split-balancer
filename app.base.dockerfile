FROM python:3.12-slim AS base

# Update the base image
# RUN apt update && apt full-upgrade -y

COPY /app/requirements.txt /tmp/requirements.txt

# Install python packages
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy local code to the container image.
ENV DIR_PROJECT /opt/project
ENV DIR_SRC /opt/project/src
ENV DIR_TEST /opt/project/test
ENV HOME $DIR_PROJECT
RUN mkdir -p $DIR_PROJECT
WORKDIR $DIR_PROJECT

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV ENVIRONMENT DEV
ENV PYTHONUNBUFFERED True
ENV PYTHONPATH="${PYTHONPATH}:${DIR_PROJECT}:${DIR_SRC}:${DIR_TEST}"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

FROM base AS test

COPY /test/test.requirements.txt /tmp/test.requirements.txt
RUN pip install --no-cache-dir -r /tmp/test.requirements.txt
ENV ENVIRONMENT TEST
WORKDIR $DIR_TEST


FROM base AS app

COPY src $DIR_PROJECT/src

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
