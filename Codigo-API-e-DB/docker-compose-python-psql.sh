#!/bin/bash

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


#
# ATTENTION: This will stop and delete all the running containers
# Use it only if you are not using docker for other ativities
#
#docker rm $(docker stop $(docker ps -a -q)) 


mkdir -p python/app/logs


# add  -d  to the command below if you want the containers running in background without logs
docker-compose  -f docker-compose-python-psql.yml up --build
