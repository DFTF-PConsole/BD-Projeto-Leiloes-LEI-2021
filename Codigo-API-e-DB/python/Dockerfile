# 
#   Bases de Dados - FCTUC/LEI 2020/21
#   Projeto: "Leiloes Online"
#
#   Autores:
#       Beatriz Madeira, 2018280169, uc2018280169@student.uc.pt
#       Claudia Campos, 2018285941, cfcampos@student.dei.uc.pt
#       Dario Felix, 2018275530, dario@student.dei.uc.pt
#
#   Codigo adaptado de: 
#       Nuno Antunes <nmsa@dei.uc.pt>
#       BD 2021 Team - https://dei.uc.pt/lei/
#       University of Coimbra
#

from python:3.9-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

run pip install flask

run pip install pyjwt

run pip install psycopg2-binary

copy . /app

volume ["/app"]

workdir /app

run mkdir -p logs

EXPOSE 5000

CMD ["python", "leiloes-api.py"]
