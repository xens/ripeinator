FROM        python:3.8.6-alpine
LABEL maintainer="Romain Aviolat <r.aviolat@gmail.com>"

WORKDIR /app

RUN python3 -m pip install --upgrade pip

COPY requirements.txt .

RUN python3 -m pip install -r requirements.txt

COPY ripe.py  /bin/ripe

CMD sh
