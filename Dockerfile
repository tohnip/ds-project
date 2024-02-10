# syntax=docker/dockerfile:1

FROM python:3.11
WORKDIR /app
COPY ./src ./src
EXPOSE 3000
CMD python3 -m http.server 3000