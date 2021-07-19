/********************************************************************************
 * "YOU MAY THINK THAT THIS FUNCTION IS OBSOLETE AND DOESNT SEEM TO DO ANYTHING *
 * AND YOU WOULD BE CORRECT BUT WHEN WE REMOVE THIS FUNTION FOR SOME REASON     *
 * THE WHOLE PROGRAM CRASHES AND WE CANT FIGURE OUT WHY SO HERE IT WILL STAY"   *
 *                                       - Fernando Pessoa (segundo a internet) *
 *  Autores:                                                                    *
 *      > Beatriz Madeira (N.2018280169)                                        *
 *      > Claudia Campos (N.2018285941)                                         *
 *      > Dario Felix (N.2018275530)                                            *
 *                                                                              *
 *  Agradecimentos:                                                             *
 *      > Google                                                                *
 *      > Stackoverflow                                                         *
 *      > IDEs                                                                  *
 *      > Take Away do Pingo Doce                                               *
 *      > Take Away do SASUC                                                    *
 *      > Cantinas do SASUC                                                     *
 *      > Cafe                                                                  *
 *      > Professores                                                           *
 *      > Onda (https://onda.dei.uc.pt/v3/)                                     *
 *      > Projeto DEMO (https://github.com/nmsa/bd-demo-api)                    *
 *      > Docker, Postman, WSL2, Windows, quando querem                         *
 *                                                                              *
 *  Leiloes Online                                                              *
 *  FCTUC - DEI/LEI - Bases de Dados                                            *
 *  Coimbra, 31 de maio de 2021, 23:59h                                         *
 ********************************************************************************/
 
 
 
/* FICHEIRO SQL: BASE DE DADOS */

/* User: admin | Password: admin | Nome Database: dbproj | Host: localhost:5432 | Container: db-leiloes-container */
 
 
 
/* REMOVER DATABASE */
-- DROP DATABASE dbproj;



/* CRIAR DATABASE */
-- CREATE DATABASE dbproj;



/* REMOVER DADOS */
-- DELETE FROM not_leilao;
-- DELETE FROM not_msg;
-- DELETE FROM not_licitacao;
-- DELETE FROM mensagem;
-- DELETE FROM licitacao;
-- DELETE FROM leilao_descricao;
-- DELETE FROM leilao;
-- DELETE FROM pessoa;
-- DELETE FROM artigo;



/* REMOVER TABELAS */
-- DROP TABLE not_leilao;
-- DROP TABLE not_msg;
-- DROP TABLE not_licitacao;
-- DROP TABLE mensagem;
-- DROP TABLE licitacao;
-- DROP TABLE leilao_descricao;
-- DROP TABLE leilao;
-- DROP TABLE pessoa;
-- DROP TABLE artigo;



/* CONFIGURACOES */
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";



/* CRIAR TABELAS */
CREATE TABLE leilao (
	leilao_id		UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
	data_inicio		TIMESTAMP NOT NULL,
	data_fim		TIMESTAMP NOT NULL,
	preco_minimo	NUMERIC NOT NULL,
	is_canceled		BOOL NOT NULL DEFAULT false,
	pessoa_user_id	UUID NOT NULL,
	artigo_codigo	VARCHAR(13) NOT NULL,
	PRIMARY KEY(leilao_id)
);

CREATE TABLE pessoa (
	user_id				UUID UNIQUE NOT NULL DEFAULT uuid_generate_v4(),
	username			VARCHAR(512) UNIQUE NOT NULL,
	password			VARCHAR(512) NOT NULL,
	email				VARCHAR(512) UNIQUE NOT NULL,
	data_ultimo_acesso	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	token				UUID UNIQUE,
	validade_token		TIMESTAMP,
	is_admin			BOOL NOT NULL DEFAULT False,
	is_banido			BOOL NOT NULL DEFAULT False,
	PRIMARY KEY(user_id)
);

CREATE TABLE artigo (
	codigo		VARCHAR(13) UNIQUE NOT NULL,
	nome		VARCHAR(512) NOT NULL,
	descricao	TEXT NOT NULL,
	PRIMARY KEY(codigo)
);

CREATE TABLE licitacao (
	data_licitacao		TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	valor				NUMERIC NOT NULL,
	is_valido			BOOL NOT NULL DEFAULT true,
	pessoa_user_id		UUID NOT NULL,
	leilao_leilao_id	UUID NOT NULL,
	PRIMARY KEY(data_licitacao, pessoa_user_id, leilao_leilao_id)
);

CREATE TABLE leilao_descricao (
	data_modificao		TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	descricao			TEXT NOT NULL,
	titulo				TEXT NOT NULL,
	leilao_leilao_id	UUID NOT NULL,
	PRIMARY KEY(data_modificao, leilao_leilao_id)
);

CREATE TABLE mensagem (
	data_msg			TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	msg					TEXT NOT NULL,
	pessoa_user_id		UUID NOT NULL,
	leilao_leilao_id	UUID NOT NULL,
	PRIMARY KEY(data_msg, pessoa_user_id, leilao_leilao_id)
);

CREATE TABLE not_leilao (
	leilao_leilao_id			UUID NOT NULL,
	notificacao_data_not		TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	notificacao_msg				TEXT NOT NULL,
	notificacao_is_read			BOOL NOT NULL DEFAULT False,
	notificacao_pessoa_user_id	UUID NOT NULL,
	PRIMARY KEY(notificacao_data_not, notificacao_pessoa_user_id)
);

CREATE TABLE not_msg (
	mensagem_data_msg			TIMESTAMP NOT NULL,
	mensagem_pessoa_user_id		UUID NOT NULL,
	mensagem_leilao_leilao_id	UUID NOT NULL,
	notificacao_data_not		TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	notificacao_msg				TEXT NOT NULL,
	notificacao_is_read			BOOL NOT NULL DEFAULT False,
	notificacao_pessoa_user_id	UUID NOT NULL,
	PRIMARY KEY(notificacao_data_not, notificacao_pessoa_user_id)
);

CREATE TABLE not_licitacao (
	licitacao_data_licitacao	 TIMESTAMP NOT NULL,
	licitacao_pessoa_user_id	 UUID NOT NULL,
	licitacao_leilao_leilao_id UUID NOT NULL,
	notificacao_data_not	 TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	notificacao_msg		 TEXT NOT NULL,
	notificacao_is_read	 BOOL NOT NULL DEFAULT False,
	notificacao_pessoa_user_id UUID NOT NULL,
	PRIMARY KEY(notificacao_data_not,notificacao_pessoa_user_id)
);

ALTER TABLE leilao ADD CONSTRAINT leilao_fk1 FOREIGN KEY (pessoa_user_id) REFERENCES pessoa(user_id);
ALTER TABLE leilao ADD CONSTRAINT leilao_fk2 FOREIGN KEY (artigo_codigo) REFERENCES artigo(codigo);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk1 FOREIGN KEY (pessoa_user_id) REFERENCES pessoa(user_id);
ALTER TABLE licitacao ADD CONSTRAINT licitacao_fk2 FOREIGN KEY (leilao_leilao_id) REFERENCES leilao(leilao_id);
ALTER TABLE leilao_descricao ADD CONSTRAINT leilao_descricao_fk1 FOREIGN KEY (leilao_leilao_id) REFERENCES leilao(leilao_id);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk1 FOREIGN KEY (pessoa_user_id) REFERENCES pessoa(user_id);
ALTER TABLE mensagem ADD CONSTRAINT mensagem_fk2 FOREIGN KEY (leilao_leilao_id) REFERENCES leilao(leilao_id);
ALTER TABLE not_leilao ADD CONSTRAINT not_leilao_fk1 FOREIGN KEY (leilao_leilao_id) REFERENCES leilao(leilao_id);
ALTER TABLE not_leilao ADD CONSTRAINT not_leilao_fk2 FOREIGN KEY (notificacao_pessoa_user_id) REFERENCES pessoa(user_id);
ALTER TABLE not_msg ADD CONSTRAINT not_msg_fk1 FOREIGN KEY (mensagem_data_msg, mensagem_pessoa_user_id, mensagem_leilao_leilao_id) REFERENCES mensagem(data_msg, pessoa_user_id, leilao_leilao_id);
ALTER TABLE not_msg ADD CONSTRAINT not_msg_fk2 FOREIGN KEY (notificacao_pessoa_user_id) REFERENCES pessoa(user_id);
ALTER TABLE not_licitacao ADD CONSTRAINT not_licitacao_fk1 FOREIGN KEY (licitacao_data_licitacao, licitacao_pessoa_user_id, licitacao_leilao_leilao_id) REFERENCES licitacao(data_licitacao, pessoa_user_id, leilao_leilao_id);
ALTER TABLE not_licitacao ADD CONSTRAINT not_licitacao_fk2 FOREIGN KEY (notificacao_pessoa_user_id) REFERENCES pessoa(user_id);



/* ROLES UTILIZADORES */
-- meter codigo aqui...



/* INDEX E PERFORMANCE */
CREATE UNIQUE INDEX index_pessoa_token ON pessoa(token);
CREATE INDEX index_leilao_pessoa_user_id ON leilao(pessoa_user_id);

-- DROP INDEX index_pessoa_token;
-- DROP INDEX index_leilao_pessoa_user_id;



/* INSERIR DADOS INICIAIS */
INSERT INTO artigo VALUES('1234567890000', 'Livro Velho',  'Um livro bastante velho');
INSERT INTO artigo VALUES('9876543210987', 'Mota',  'Uma mota qualquer');
INSERT INTO artigo VALUES('0123456789012', 'Carro',  'a um bom preço de mercado');
INSERT INTO artigo VALUES('0000000000001', 'OVNI',  'sim, um ovni');
INSERT INTO artigo VALUES('6666666666666', 'alma e dignidade',  'e porque nao?');
INSERT INTO artigo VALUES('9999999999999', '5G',  'ANACOM - Atribuição de direitos de utilização de frequências nas faixas dos 700 MHz, 900 MHz, 2,1 GHz, 2,6 GHz e 3,6 GHz.');

INSERT INTO pessoa VALUES(uuid_generate_v4(), 'admin1', 'passadmin1', 'admin1@dei.uc.pt', CURRENT_TIMESTAMP, uuid_generate_v4(), CURRENT_TIMESTAMP, TRUE, FALSE);
INSERT INTO pessoa VALUES(uuid_generate_v4(), 'admin2', 'passadmin2', 'admin2@dei.uc.pt', CURRENT_TIMESTAMP, uuid_generate_v4(), CURRENT_TIMESTAMP, TRUE, FALSE);


