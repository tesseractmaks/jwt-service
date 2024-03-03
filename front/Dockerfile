FROM python:3.11

RUN mkdir "app"

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . ./





