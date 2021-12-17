# syntax=docker/dockerfile:1

FROM python:3.8-alpine

COPY /requirements.txt /requirements.txt
COPY /services/ /services/
COPY /app.py /app.py

ENV PYTHONUNBUFFERED=TRUE
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "./app.py"]