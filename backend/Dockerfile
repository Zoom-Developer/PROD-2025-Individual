FROM python:3.12-alpine

WORKDIR /app
COPY . .

RUN apk update; apk add curl gcc

RUN pip install --no-cache-dir poetry
RUN poetry install --only main --no-root --no-directory

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN chmod +x entry.sh
ENTRYPOINT [ "sh", "entry.sh" ]