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

FROM library/postgres


ENV POSTGRES_USER admin
ENV POSTGRES_PASSWORD admin
ENV POSTGRES_DB dbproj

COPY dbleiloes_start.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
