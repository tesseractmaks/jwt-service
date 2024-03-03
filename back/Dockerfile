FROM python:3.11

RUN mkdir "app"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install libgl1-mesa-glx -y

RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY ./jwt-app/jwt_app ./

CMD ["hypercorn", "main:app", "--bind", "0.0.0.0:8000", "--reload"]







