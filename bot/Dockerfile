FROM python:3.12-alpine

WORKDIR /bot

COPY . .

RUN pip install --no-cache-dir poetry
RUN poetry install --only main --no-root --no-directory

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD [ "poetry", "run", "python", "main.py" ]