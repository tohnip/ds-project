# syntax=docker/dockerfile:1

FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD python3 send_material.py