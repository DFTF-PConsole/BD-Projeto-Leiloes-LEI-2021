# Bases de Dados - FCTUC/LEI 2020/21 - Projeto: "Leilões Online" - Postgresql


## Requisitos

- Para executar este projeto é necessário ter instalado:
  - Docker



## Desenvolvimento

Use apenas se precisar de ter a base de dados a correr separadamente.
O executavél na root está preparado para iniciar a base de dados e conecta-la com a aplicação web.



## Conexão a Base de Dados

- **User**: admin
- **Password**: admin
- **Nome da Base de Dados**: dbproj
- **Host**: localhost:5432



## Configuração e Execução

Para construir a imagem do docker deves correr:

```sh
sh build.sh
```

Para correr o container:

```sh
sh run.sh
```

- _nota: ao modificar o script `run.sh` para incluir -dit irá fazer com que o container execute em background. Não se esqueça de usar o script `stop.sh` para para-lo/remove-lo._

Para parar o container:

```sh
sh stop.sh
```



## Autores

* Beatriz Madeira, 2018280169, uc2018280169@student.uc.pt
* Claudia Campos, 2018285941, cfcampos@student.dei.uc.pt
* Dario Felix, 2018275530, dario@student.dei.uc.pt



## Codigo de configuração adaptado de: 

* Nuno Antunes <nmsa@dei.uc.pt>
* BD 2021 Team - https://dei.uc.pt/lei/
* University of Coimbra
* https://github.com/nmsa/bd-demo-api
