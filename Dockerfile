FROM python:3.12.0-alpine3.17

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

COPY . /app/

EXPOSE 8000

ENV NAME main

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" , "--reload"]
