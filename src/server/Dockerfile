# syntax=docker/dockerfile:1

FROM python:3.11
WORKDIR /app
COPY . .
EXPOSE 15000
RUN pip install -r requirements.txt
CMD python3 app.py