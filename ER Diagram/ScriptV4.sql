CREATE TABLE leilao (
	leilao_id	 INTEGER,
	data_inicio	 TIMESTAMP NOT NULL,
	data_fim	 TIMESTAMP NOT NULL,
	preco_minimo	 FLOAT(8) NOT NULL,
	is_canceled	 BOOL NOT NULL DEFAULT false,
	pessoa_user_id INTEGER NOT NULL,
	artigo_codigo	 VARCHAR(13) NOT NULL,
	PRIMARY KEY(leilao_id)
);

CREATE TABLE pessoa (
	user_id		 INTEGER,
	username		 VARCHAR(512) UNIQUE NOT NULL,
	password		 VARCHAR(512) NOT NULL,
	email		 VARCHAR(512) UNIQUE NOT NULL,
	data_ultimo_acesso TIMESTAMP NOT NULL,
	token		 VARCHAR(512) UNIQUE,
	validade_token	 TIMESTAMP,
	is_admin		 BOOL NOT NULL DEFAULT False,
	is_banido		 BOOL NOT NULL DEFAULT False,
	PRIMARY KEY(user_id)
);

CREATE TABLE artigo (
	codigo	 VARCHAR(13),
	nome	 VARCHAR(512) NOT NULL,
	descricao TEXT(1024) NOT NULL,
	PRIMARY KEY(codigo)
);

CREATE TABLE licitacao (
	data		 TIMESTAMP,
	valor		 FLOAT(8) NOT NULL,
	is_valido	 BOOL NOT NULL DEFAULT true,
	pessoa_user_id	 INTEGER,
	leilao_leilao_id INTEGER,
	PRIMARY KEY(data,pessoa_user_id,leilao_leilao_id)
);

CREATE TABLE leilao_descricao (
	data_modificao	 TIMESTAMP,
	descricao	 TEXT(1024) NOT NULL,
	titulo		 TEXT(512) NOT NULL,
	leilao_leilao_id INTEGER,
	PRIMARY KEY(data_modificao,leilao_leilao_id)
);

CREATE TABLE mensagem (
	data		 TIMESTAMP,
	msg		 TEXT(512) NOT NULL,
	pessoa_user_id	 INTEGER,
	leilao_leilao_id INTEGER,
	PRIMARY KEY(data,pessoa_user_id,leilao_leilao_id)
);

CREATE TABLE not_leilao (
	leilao_leilao_id		 INTEGER,
	notificacao_data		 TIMESTAMP,
	notificacao_msg		 TEXT(1024) NOT NULL,
	notificacao_is_read	 BOOL NOT NULL DEFAULT False,
	notificacao_pessoa_user_id INTEGER,
	PRIMARY KEY(notificacao_data,notificacao_pessoa_user_id)
);

CREATE TABLE not_msg (
	mensagem_data		 TIMESTAMP,
	mensagem_pessoa_user_id	 INTEGER,
	mensagem_leilao_leilao_id	 INTEGER,
	notificacao_data		 TIMESTAMP,
	notificacao_msg		 TEXT(1024) NOT NULL,
	notificacao_is_read	 BOOL NOT NULL DEFAULT False,
	notificacao_pessoa_user_id INTEGER,
	PRIMARY KEY(notificacao_data,notificacao_pessoa_user_id)
);

CREATE TABLE not_licitacao (
	licitacao_data		 TIMESTAMP,
	licitacao_pessoa_user_id	 INTEGER,
	licitacao_leilao_leilao_id INTEGER,
	notificacao_data		 TIMESTAMP,
	notificacao_msg		 TEXT(1024) NOT NULL,
	notificacao_is_read	 BOOL NOT NULL DEFAULT False,
	notificacao_pessoa_user_id INTEGER,
	PRIMARY KEY(notificacao_data,notificacao_pessoa_user_id)
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
ALTER TABLE not_msg ADD CONSTRAINT not_msg_fk1 FOREIGN KEY (mensagem_data) REFERENCES mensagem(data);
ALTER TABLE not_msg ADD CONSTRAINT not_msg_fk2 FOREIGN KEY (mensagem_pessoa_user_id) REFERENCES mensagem(pessoa_user_id);
ALTER TABLE not_msg ADD CONSTRAINT not_msg_fk3 FOREIGN KEY (mensagem_leilao_leilao_id) REFERENCES mensagem(leilao_leilao_id);
ALTER TABLE not_msg ADD CONSTRAINT not_msg_fk4 FOREIGN KEY (notificacao_pessoa_user_id) REFERENCES pessoa(user_id);
ALTER TABLE not_licitacao ADD CONSTRAINT not_licitacao_fk1 FOREIGN KEY (licitacao_data) REFERENCES licitacao(data);
ALTER TABLE not_licitacao ADD CONSTRAINT not_licitacao_fk2 FOREIGN KEY (licitacao_pessoa_user_id) REFERENCES licitacao(pessoa_user_id);
ALTER TABLE not_licitacao ADD CONSTRAINT not_licitacao_fk3 FOREIGN KEY (licitacao_leilao_leilao_id) REFERENCES licitacao(leilao_leilao_id);
ALTER TABLE not_licitacao ADD CONSTRAINT not_licitacao_fk4 FOREIGN KEY (notificacao_pessoa_user_id) REFERENCES pessoa(user_id);

