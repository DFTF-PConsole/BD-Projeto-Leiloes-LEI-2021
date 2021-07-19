# Bases de Dados - FCTUC/LEI 2020/21 - Projeto: "Leilões Online"


O projeto é totalmente automatizado para ser facilmente deployed com a ajuda da ferramenta `docker`.



## Conteúdo

- [**`PostgreSQL`**](postgresql) - Base de Dados pronta para correr num `docker` container com ou sem a ajuda da ferramenta `docker-compose`;
- [**`Codigo Python`**](python) - Codigo fonte da aplicação web em python com o `docker` container configurado. Pornto para correr no `docker-compose` com PostgreSQL;
  - [`app/`](python/app) pasta é montada para permitir o desenvolvimento com o container em execução
- [**`Testes no Postman`**](testes_postman) - Uma coleção de testes (requests) exportados da ferramenta `postman`(https://www.postman.com/)



## Requisitos

Para executar este projecto é preciso ter instalado:

- `docker`
- `docker-compose`



## Python REST API 


Para executar este projecto corra o script [`./docker-compose-python-psql.sh`](docker-compose-python-psql.sh) para ter a base de dados e o servidor a funcionar.
Este script usa o `docker-compose` e segue as configurações disponiveis em [`docker-compose-python-psql.yml`](docker-compose-python-psql.yml).

A pasta [`app`](python/app) é mapeada para o container.
Podes modificar o conteudo e o servidor irá atualizar sem que seja necessário reinicializar o container.

* Acesso via browser/web: http://localhost:8080



## Autores

* Beatriz Madeira, 2018280169, uc2018280169@student.uc.pt
* Claudia Campos, 2018285941, cfcampos@student.dei.uc.pt
* Dario Felix, 2018275530, dario@student.dei.uc.pt



## Codigo de configuração adaptado de: 

* Nuno Antunes <nmsa@dei.uc.pt>
* BD 2021 Team - https://dei.uc.pt/lei/
* University of Coimbra
* https://github.com/nmsa/bd-demo-api
