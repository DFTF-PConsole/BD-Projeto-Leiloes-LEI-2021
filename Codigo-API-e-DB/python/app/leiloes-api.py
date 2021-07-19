#
# "YOU MAY THINK THAT THIS FUNCTION IS OBSOLETE AND DOESNT SEEM TO DO ANYTHING
# AND YOU WOULD BE CORRECT BUT WHEN WE REMOVE THIS FUNTION FOR SOME REASON
# THE WHOLE PROGRAM CRASHES AND WE CANT FIGURE OUT WHY SO HERE IT WILL STAY"
#                                       - Fernando Pessoa (segundo a internet)
#  Autores:
#      > Beatriz Madeira (N.2018280169)
#      > Claudia Campos (N.2018285941)
#      > Dario Felix (N.2018275530)
#
#  Agradecimentos:
#      > Google
#      > Stackoverflow
#      > IDEs
#      > Take Away do Pingo Doce
#      > Take Away do SASUC
#      > Cantinas do SASUC
#      > Cafe
#      > Professores
#      > Projeto DEMO (https://github.com/nmsa/bd-demo-api)
#      > Onda (https://onda.dei.uc.pt/v3/)
#      > Docker, Postman, WSL2, Windows, quando querem
#
#  Leiloes Online
#  FCTUC - DEI/LEI - Bases de Dados
#  Coimbra, 31 de maio de 2021, 23:59h
#


# FICHEIRO PYTHON: API WEB APP


# [*** SELO DE QUALIDADE ***] -> significa que ja se encontra bem implementada, revista e testada intensivamente


# IMPORTS
import logging
import psycopg2
import time
from flask import Flask, jsonify, request, redirect


# VARS GLOBAIS
app = Flask(__name__)
token_ttl = 12


# Tratar Erro Code 404 Not Found   [*** SELO DE QUALIDADE ***]
@app.errorhandler(404)
def not_found(e):
    logger.info("### NOT FOUND 404 ###")
    return """<h1>Pagina Não Encontrada (Erro 404)</h1> <br/>
            Homepage: <a href="http://localhost:8080/dbproj">http://localhost:8080/dbproj</a> """


# Redirect to Homepage   [*** SELO DE QUALIDADE ***]
@app.route('/')
def hello():
    logger.info("### REDIRECT / ###")
    return redirect("http://localhost:8080/dbproj", code=302)


# HOMEPAGE   [*** SELO DE QUALIDADE ***]
@app.route('/dbproj')
def homepage():
    logger.info("### /dbproj ###")
    return """<h1>Projeto: "Leilões Online"</h1> <br/>
        FCTUC/LEI 2020/21 - Bases de Dados<br/>
        Autores: Beatriz Madeira, Cláudia Campos, Dário Félix<br/><br/>
        Login: <a href="http://localhost:8080/dbproj/user">http://localhost:8080/dbproj/user</a> <br/>
        Criar Conta: <a href="http://localhost:8080/dbproj/user">http://localhost:8080/dbproj/user</a> <br/>
        (Usar Postman)"""


# Um administrador pode obter estatísticas de atividade na aplicação | get | GET | restricoes: verificar se é admin
# REQUEST (GET)  - ---                                                                    [*** SELO DE QUALIDADE ***]
# RESPONSE       - { "topUserIdComLeiloesCriados": [ "user1", "user2", ... ],
#                    "topUserIdComLeiloesGanhos": [ "user1", "user2", ... ],
#                    "totalLeiloesUltimos10Dias": 3 } em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/estatisticas", methods=['GET'])
def estatisticas():
    logger.info("### GET /dbproj/estatisticas ###")

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)

    res_bool_admin = False
    res_str_admin = False
    if res_bool is True:
        res_bool_admin, res_str_admin = is_admin(cur, res_str)

    if res_bool is False:
        result = {"erro": res_str}
    elif res_bool_admin is False:
        result = {"erro": res_str_admin}
    elif bool(res_str_admin) is False:
        result = {"erro": "sem permissões (apenas admins)"}
    else:
        statement_esta1 = """ 
            SELECT pessoa_user_id, COUNT(leilao_id) AS total
                FROM leilao
                    GROUP BY pessoa_user_id
                        ORDER BY total DESC
                            LIMIT 10
                        ; """

        statement_esta2 = """ 
            SELECT l.pessoa_user_id, COUNT(l.leilao_leilao_id) AS total
                FROM licitacao l, leilao e
                    WHERE l.is_valido = TRUE
                        AND l.leilao_leilao_id = e.leilao_id
                        AND e.data_fim <= CURRENT_TIMESTAMP
                        AND e.is_canceled = FALSE
                        AND l.valor = (SELECT MAX(valor) 
                                            FROM licitacao j
                                                WHERE j.is_valido = TRUE 
                                                    AND j.leilao_leilao_id = l.leilao_leilao_id) 
                            GROUP BY l.pessoa_user_id
                                ORDER BY total DESC
                                    LIMIT 10
                        ; """

        statement_esta3 = """ 
            SELECT COUNT(*) AS total
                FROM leilao
                    WHERE (data_inicio >= (CURRENT_TIMESTAMP - INTERVAL '10 days') AND data_inicio <= CURRENT_TIMESTAMP)
                        OR (data_fim >= (CURRENT_TIMESTAMP - INTERVAL '10 days') AND data_fim <= CURRENT_TIMESTAMP)
                        ; """

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            cur.execute("SET TRANSACTION READ ONLY;")

            # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement_esta1)
            rows1 = cur.fetchall()

            cur.execute(statement_esta2)
            rows2 = cur.fetchall()

            cur.execute(statement_esta3)
            esta3 = cur.fetchone()[0]

            cur.execute("COMMIT;")
            lista_esta1 = []
            lista_esta2 = []

            for row in rows1:
                content = {"userId": row[0]}
                lista_esta1.append(content)

            for row in rows2:
                content = {"userId": row[0]}
                lista_esta2.append(content)

            result = {"topUserIdComLeiloesCriados": lista_esta1, "topUserIdComLeiloesGanhos": lista_esta2,
                      "totalLeiloesUltimos10Dias": int(esta3)}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Um administrador pode banir permanentemente um utilizador | get | GET | restricoes: verificar se é admin
# REQUEST (GET)  - ---
# RESPONSE       - { "sucesso": "msg" } em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/user/<user_id>/banir", methods=['GET'])
def banir_user(user_id):
    logger.info("### GET /dbproj/user/<user_id>/banir ###")

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    logger.info("---- banir  ----")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)

    res_bool_admin = False
    res_str_admin = False
    if res_bool is True:
        res_bool_admin, res_str_admin = is_admin(cur, res_str)

    if res_bool is False:
        result = {"erro": res_str}
    elif res_bool_admin is False:
        result = {"erro": res_str_admin}
    elif bool(res_str_admin) is False:
        result = {"erro": "sem permissões (apenas admins)"}
    else:
        statement_verifica = """ SELECT * 
                                    FROM pessoa
                                        WHERE user_id = %s
                                            AND is_banido = FALSE
                        ; """

        values_verifica = (user_id,)

        # Cancela todos os leilões do utilizador banido
        statement = """ UPDATE leilao SET is_canceled = TRUE 
                            WHERE is_canceled = FALSE 
                                AND pessoa_user_id = %s::UUID; """

        values = (user_id,)

        # Notificar utilizadores dos leilões cancelados
        statement2 = """  
            INSERT INTO not_leilao (leilao_leilao_id, notificacao_msg, notificacao_pessoa_user_id) 
                (SELECT leilao_leilao_id, 'O Leilão no qual licitou foi cancelado.', pessoa_user_id 
                    FROM licitacao 
                        WHERE leilao_leilao_id IN (SELECT leilao_id 
                                                        FROM leilao 
                                                            WHERE pessoa_user_id = %s::UUID) 
                            GROUP BY pessoa_user_id, leilao_leilao_id) 
            RETURNING *;
            """
        values2 = (user_id,)

        # Invalidar as licitações do utilizador banido incluindo todas as superiores a esta (menos as melhores)
        statement3 = """ 
            UPDATE licitacao AS l SET is_valido = FALSE
                WHERE l.leilao_leilao_id IN (SELECT leilao_leilao_id 
                                                FROM licitacao 
                                                    WHERE pessoa_user_id = %s::UUID)
                    AND valor >= ANY (SELECT valor 
                                        FROM licitacao 
                                            WHERE pessoa_user_id = %s::UUID 
                                            AND l.leilao_leilao_id = leilao_leilao_id)
                    AND valor <> (SELECT valor 
                                    FROM licitacao 
                                        WHERE leilao_leilao_id = l.leilao_leilao_id 
                                            AND pessoa_user_id <> %s::UUID 
                                                GROUP BY valor 
                                                    HAVING valor = (SELECT max(valor) 
                                                                        FROM licitacao 
                                                                        WHERE leilao_leilao_id = l.leilao_leilao_id))
            RETURNING *; """

        values3 = (user_id, user_id, user_id)

        # Modificar o valor da melhor licitacao (que não seja do utilizador banido) para o valor da menor licitação
        # invalidada
        statement4 = """ 
            UPDATE licitacao as ll 
                SET valor = (SELECT valor 
                                FROM licitacao AS l 
                                    WHERE l.leilao_leilao_id IN (SELECT leilao_leilao_id 
                                                                    FROM licitacao 
                                                                        WHERE pessoa_user_id = %s::UUID) 
                                        AND valor IN (SELECT valor 
                                                        FROM licitacao 
                                                            WHERE licitacao.leilao_leilao_id = l.leilao_leilao_id 
                                                                GROUP BY valor 
                                                                    HAVING valor = (SELECT min(valor) 
                                                                        FROM licitacao 
                                                                WHERE licitacao.leilao_leilao_id = l.leilao_leilao_id 
            AND is_valido = FALSE)) AND ll.leilao_leilao_id = l.leilao_leilao_id), data_licitacao = CURRENT_TIMESTAMP
            WHERE ll.leilao_leilao_id IN 
            (SELECT leilao_leilao_id FROM licitacao WHERE pessoa_user_id = %s::UUID) 
            AND valor IN (SELECT valor FROM licitacao WHERE licitacao.leilao_leilao_id = ll.leilao_leilao_id 
            GROUP BY valor HAVING valor = (SELECT max(valor) FROM licitacao 
            WHERE licitacao.leilao_leilao_id = ll.leilao_leilao_id))
            """

        values4 = (user_id, user_id)

        # Escrever mensagem no mural de cada leilão afectado a lamentar o sucedido
        statement5 = """ INSERT INTO mensagem (msg, pessoa_user_id, leilao_leilao_id) 
            (SELECT 'Um dos utilizadores que licitou neste leilão foi banido. Lamentamos o inconveniente causado.', 
             %s::UUID, leilao_leilao_id FROM licitacao WHERE pessoa_user_id = %s::UUID)
             RETURNING *; """

        values5 = (res_str, user_id)
        # Enviar notificações aos envolvidos
        statement6 = """ 
            INSERT INTO not_msg (mensagem_data_msg, mensagem_pessoa_user_id, mensagem_leilao_leilao_id, notificacao_msg, 
                notificacao_pessoa_user_id)
                SELECT mensagem.data_msg, %s::UUID, mensagem.leilao_leilao_id, mensagem.msg, licitacao.pessoa_user_id
                FROM mensagem, licitacao
                WHERE licitacao.leilao_leilao_id IN (SELECT leilao_leilao_id FROM licitacao 
                WHERE pessoa_user_id = %s::UUID)
                AND mensagem.leilao_leilao_id = licitacao.leilao_leilao_id
                AND licitacao.pessoa_user_id <> %s::UUID
                GROUP BY licitacao.pessoa_user_id, mensagem.leilao_leilao_id, mensagem.msg, mensagem.data_msg; """

        values6 = (res_str, user_id, user_id)

        statement7 = """ UPDATE pessoa SET is_banido = TRUE
        WHERE is_banido = FALSE AND user_id = %s::UUID RETURNING *; """
        values7 = (user_id,)

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            cur.execute("LOCK TABLE pessoa IN SHARE ROW EXCLUSIVE MODE;")
            cur.execute("LOCK TABLE leilao IN ACCESS EXCLUSIVE MODE;")
            cur.execute("LOCK TABLE licitacao IN ACCESS EXCLUSIVE MODE;")
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement_verifica, values_verifica)
            if cur.fetchone() is None:
                raise Exception("O userId nao existe ou foi banido.")

            cur.execute(statement, values)
            cur.execute(statement2, values2)
            cur.execute(statement3, values3)
            cur.execute(statement4, values4)
            cur.execute(statement5, values5)
            cur.execute(statement6, values6)
            cur.execute(statement7, values7)
            cur.execute("COMMIT;")
            result = {"sucesso": "Utilizador banido."}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Um administrador pode cancelar um leilão | get | GET | restricoes: verificar se é admin
# REQUEST (GET)  - ---                                                               [*** SELO DE QUALIDADE ***]
# RESPONSE       - { "sucesso": "msg" } em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/leilao/<leilao_id>/abortar", methods=['GET'])
def abortar_leilao(leilao_id):
    logger.info("### GET /dbproj/leilao/<leilao_id>/abortar ###")

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    logger.info("---- cancelar leilao  ----")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)

    if res_bool is False:
        result = {"erro": res_str}

    else:
        statement = """ UPDATE leilao SET is_canceled = TRUE 
        WHERE leilao_id = %s::UUID AND is_canceled = FALSE AND 
        (SELECT is_admin FROM pessoa WHERE user_id = %s::UUID) = TRUE RETURNING is_canceled ; """
        
        values = (leilao_id, res_str)
        
        statement2 = """ INSERT INTO not_leilao (leilao_leilao_id, notificacao_msg, notificacao_pessoa_user_id)
        (SELECT %s::UUID, 'O Leilão no qual licitou foi cancelado.', pessoa_user_id
        FROM licitacao
        WHERE leilao_leilao_id = %s::UUID
        GROUP BY pessoa_user_id) RETURNING TRUE ; """
        
        values2 = (leilao_id, leilao_id)
        
        statement3 = """ INSERT INTO not_leilao (leilao_leilao_id, notificacao_msg, notificacao_pessoa_user_id)
        (SELECT %s::UUID, 'O seu leilão foi cancelado por um administrador.', pessoa_user_id
        FROM leilao
        WHERE leilao_id = %s::UUID AND is_canceled = TRUE) RETURNING TRUE ; """
        
        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            cur.execute("LOCK TABLE leilao IN SHARE ROW EXCLUSIVE MODE;")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement, values)
            if cur.fetchone() is None:
                raise Exception("O leilão já se encontra cancelado ou o utilizador não é administrador da plataforma.")
            cur.execute(statement2, values2)
            cur.execute(statement3, values2)
            cur.execute("COMMIT;")

            result = {"sucesso": "Leilão abortado."}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()
        
    return jsonify(result)


# Término do leilão na data, hora e minuto marcados | get | GET | restricoes: apenas o user que criou pode terminar
# REQUEST (GET)  - ---                                                                   [*** SELO DE QUALIDADE ***]
# RESPONSE       - { "userId" : "123", "valor": 15.0 } em caso de sucesso
# RESPONSE       - { "sucesso": "ainda não existem licitações associadas a este leilao" } se nao houver licitacoes
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/leilao/<leilao_id>/terminar", methods=['GET'])
def terminar_leilao(leilao_id):
    logger.info("### GET /dbproj/leilao/<leilao_id>/terminar ###")

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)
    if res_bool is False:
        result = {"erro": res_str}

    else:
        statement_leilao_update = """ 
                    UPDATE leilao SET data_fim = CURRENT_TIMESTAMP
                        WHERE data_fim > CURRENT_TIMESTAMP 
                            AND is_canceled = FALSE 
                            AND leilao_id = %s 
                            AND pessoa_user_id = %s 
                    RETURNING data_fim ; """

        values_leilao_update = (leilao_id, res_str)

        statement_licitacao = """ 
                    SELECT pessoa_user_id, valor 
                        FROM licitacao 
                            WHERE is_valido = TRUE 
                                AND valor = (SELECT MAX(valor) 
                                                FROM licitacao 
                                                    WHERE is_valido = TRUE 
                                                        AND leilao_leilao_id = %s) 
                                AND leilao_leilao_id = %s ; """

        values_licitacao = (leilao_id, leilao_id)

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            cur.execute("LOCK TABLE leilao IN SHARE ROW EXCLUSIVE MODE;")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement_leilao_update, values_leilao_update)
            data_fetch = cur.fetchone()

            if data_fetch is None or data_fetch[0] == "":
                cur.execute("ROLLBACK;")
                result = {"erro": "nao foi possivel terminar, possiveis razões: ou id do leilão não existe, "
                                  "ou já se encontra terminado, ou foi cancelado por um admin, ou não tem permissões "
                                  "para o terminar (token)"}

            else:
                cur.execute(statement_licitacao, values_licitacao)
                licitacao_atual = cur.fetchone()

                cur.execute("COMMIT;")

                if licitacao_atual is not None and licitacao_atual[0] != "":
                    result = {"userId": licitacao_atual[0], "valor": float(licitacao_atual[1])}
                else:
                    result = {"sucesso": "ainda não existem licitações associadas a este leilao"}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Entrega imediata de notificações a utilizadores TODAS (& Notificação de licitação ultrapassada) | get | GET [OPCIONAL]
# REQUEST (GET)  - ---                                                                      [*** SELO DE QUALIDADE ***]
# RESPONSE       - { "notificacao_leilao": [ { "leilaoId": "1", "data": "2021", "mensagem": "msg" }, ... ],
#           "notificacao_mensagem": [ { "leilaoId": "1", "data": "2021", "pessoa": "Ana", "mensagem": "msg" }, ... ],
#           "notificacao_licitacao": [ { "leilaoId": "1", "data": "2021", "pessoa": "Ana", "mensagem": "msg" }, ... ] }
#           em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/notificacoes/todas", methods=['GET'])
def get_notificacoes_todas():
    logger.info("### GET /dbproj/notificacoes/todas ###")

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)
    if res_bool is False:
        result = {"erro": res_str}

    else:
        statement_notificacao_leilao = """ 
            UPDATE not_leilao SET notificacao_is_read = True
                WHERE notificacao_pessoa_user_id = %s
            RETURNING leilao_leilao_id, notificacao_data_not, notificacao_msg ; """

        statement_notificacao_mensagem = """ 
            UPDATE not_msg SET notificacao_is_read = True
                WHERE notificacao_pessoa_user_id = %s
            RETURNING mensagem_leilao_leilao_id, notificacao_data_not, mensagem_pessoa_user_id, notificacao_msg ; """

        statement_notificacao_licitacao = """ 
            UPDATE not_licitacao SET notificacao_is_read = True
                WHERE notificacao_pessoa_user_id = %s
            RETURNING licitacao_leilao_leilao_id, notificacao_data_not, licitacao_pessoa_user_id, notificacao_msg ; """

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            # LOCK IMPLICITO
            # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement_notificacao_leilao, (res_str,))
            rows_notificacao_leilao = cur.fetchall()
            cur.execute(statement_notificacao_mensagem, (res_str,))
            rows_notificacao_mensagem = cur.fetchall()
            cur.execute(statement_notificacao_licitacao, (res_str,))
            rows_notificacao_licitacao = cur.fetchall()
            cur.execute("COMMIT;")

            listinha_notificacao_leilao = []
            listinha_notificacao_mensagem = []
            listinha_notificacao_licitacao = []

            for row in rows_notificacao_leilao:
                content = {"leilaoId": row[0], "data": row[1], "mensagem": row[2]}
                listinha_notificacao_leilao.append(content)

            for row in rows_notificacao_mensagem:
                content = {"leilaoId": row[0], "data": row[1], "userId": row[2], "mensagem": row[3]}
                listinha_notificacao_mensagem.append(content)

            for row in rows_notificacao_licitacao:
                content = {"leilaoId": row[0], "data": row[1], "userId": row[2], "mensagem": row[3]}
                listinha_notificacao_licitacao.append(content)

            result = {"notificacao_leilao": listinha_notificacao_leilao,
                      "notificacao_mensagem": listinha_notificacao_mensagem,
                      "notificacao_licitacao": listinha_notificacao_licitacao}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Entrega imediata de notificações a utilizadores NOVAS (& Notificação de licitação ultrapassada) | get | GET
# REQUEST (GET)  - ---                                                                   [*** SELO DE QUALIDADE ***]
# RESPONSE       - { "notificacao_leilao": [ { "leilaoId": "1", "data": "2021", "mensagem": "msg" }, ... ],
#           "notificacao_mensagem": [ { "leilaoId": "1", "data": "2021", "userId": "Ana", "mensagem": "msg" }, ... ],
#           "notificacao_licitacao": [ { "leilaoId": "1", "data": "2021", "userId": "Ana", "mensagem": "msg" }, ... ] }
#           em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/notificacoes/novas", methods=['GET'])
def get_notificacoes_novas():
    logger.info("### GET /dbproj/notificacoes/novas ###")

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)
    if res_bool is False:
        result = {"erro": res_str}

    else:
        statement_notificacao_leilao = """ 
            UPDATE not_leilao SET notificacao_is_read = True
                WHERE notificacao_pessoa_user_id = %s
                    AND notificacao_is_read = False
            RETURNING leilao_leilao_id, notificacao_data_not, notificacao_msg ; """

        statement_notificacao_mensagem = """ 
            UPDATE not_msg SET notificacao_is_read = True
                WHERE notificacao_pessoa_user_id = %s
                    AND notificacao_is_read = False
            RETURNING mensagem_leilao_leilao_id, notificacao_data_not, mensagem_pessoa_user_id, notificacao_msg ; """

        statement_notificacao_licitacao = """ 
            UPDATE not_licitacao SET notificacao_is_read = True
                WHERE notificacao_pessoa_user_id = %s
                    AND notificacao_is_read = False
            RETURNING licitacao_leilao_leilao_id, notificacao_data_not, licitacao_pessoa_user_id, notificacao_msg ; """

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            # LOCK IMPLICITO
            # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement_notificacao_leilao, (res_str,))
            rows_notificacao_leilao = cur.fetchall()
            cur.execute(statement_notificacao_mensagem, (res_str,))
            rows_notificacao_mensagem = cur.fetchall()
            cur.execute(statement_notificacao_licitacao, (res_str,))
            rows_notificacao_licitacao = cur.fetchall()
            cur.execute("COMMIT;")

            listinha_notificacao_leilao = []
            listinha_notificacao_mensagem = []
            listinha_notificacao_licitacao = []

            for row in rows_notificacao_leilao:
                content = {"leilaoId": row[0], "data": row[1], "mensagem": row[2]}
                listinha_notificacao_leilao.append(content)

            for row in rows_notificacao_mensagem:
                content = {"leilaoId": row[0], "data": row[1], "userId": row[2], "mensagem": row[3]}
                listinha_notificacao_mensagem.append(content)

            for row in rows_notificacao_licitacao:
                content = {"leilaoId": row[0], "data": row[1], "userId": row[2], "mensagem": row[3]}
                listinha_notificacao_licitacao.append(content)

            result = {"notificacao_leilao": listinha_notificacao_leilao,
                      "notificacao_mensagem": listinha_notificacao_mensagem,
                      "notificacao_licitacao": listinha_notificacao_licitacao}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Escrever mensagem no mural de um leilão | add | POST | PARAM: leilao_id       [*** SELO DE QUALIDADE ***]
# REQUEST (POST)  - { "mensagem": "msg1" }
# RESPONSE       - { "sucesso": "msg" } em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/mensagem/<leilao_id>", methods=['POST'])
def add_mensagem(leilao_id):
    logger.info("### POST /dbproj/mensagem/<leilao_id> ###")

    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    logger.info("---- Nova Mensagem  ----")
    logger.debug(f'payload: {payload}')

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    res_bool, res_str = get_id_by_token(cur, token)

    if res_bool is False:
        result = {"erro": res_str}
    else:

        statement_leilao = """ 
                    SELECT preco_minimo 
                        FROM leilao 
                            WHERE data_fim > CURRENT_TIMESTAMP 
                                AND is_canceled = FALSE 
                                AND leilao_id = %s ; """

        values_leilao = (leilao_id,)

        statement_insert_mensagem = """
                INSERT INTO mensagem (data_msg, msg, pessoa_user_id, leilao_leilao_id) 
                    VALUES ( CURRENT_TIMESTAMP , %s , %s , %s )
                        RETURNING data_msg ; """

        values_insert_mensagem = (payload["mensagem"], res_str, leilao_id)

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            # LOCK IMPLICITO
            # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement_leilao, values_leilao)
            preco_minimo = cur.fetchone()

            if preco_minimo is None or preco_minimo[0] == "":
                cur.execute("ROLLBACK;")
                result = {"erro": "leilaoId invalido, possiveis razoes: ou id nao existe, "
                                  "ou ja terminado, ou cancelado por um admin"}

            else:
                cur.execute(statement_insert_mensagem, values_insert_mensagem)
                data_inserida = cur.fetchone()[0]

                envia_notifs_msg(cur, data_inserida, leilao_id, "mensagem nova.", res_str)

                cur.execute("COMMIT;")
                result = {"sucesso": "foi inserido com sucesso"}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro", str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Editar propriedades de um leilão | update | PUT | PARAM: leilao_id   [*** SELO DE QUALIDADE ***]
# REQUEST (PUT)  - { "titulo": "Titulo do Novo Leilão", "descricao": "Descrição do Novo Leilão" }
# RESPONSE       - {“leilaoId”: 1, “titulo”: “tit”, “descricao”: “desc1”, "artigoId": "1", "precoMinimo": 10.0,
#                   "dataInicio": "3", "dataFim": "4" } em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/leilao/<leilao_id>", methods=['PUT'])
def update_leilao(leilao_id):
    logger.info("### PUT /dbproj/leilao/<leilao_id> ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    logger.debug(f'payload: {payload}')

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)
    if res_bool is False:
        result = {"erro": res_str}

    else:
        # Insere novas descrições textuais na tabela leilao_descricao
        statement = """ 
            INSERT INTO leilao_descricao (leilao_leilao_id, titulo, descricao) 
                (SELECT leilao_id, %s, %s 
                    FROM leilao 
                        WHERE leilao_id = %s 
                            AND is_canceled = FALSE 
                            AND data_fim > CURRENT_TIMESTAMP
                            AND pessoa_user_id = %s)
            RETURNING leilao_leilao_id ; """

        values = (payload["titulo"], payload["descricao"], leilao_id, res_str)

        statement2 = """ SELECT leilao_id, data_inicio, data_fim, preco_minimo, artigo_codigo 
                            FROM leilao 
                                WHERE leilao_id = %s ; """

        value = (leilao_id,)

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            # LOCK IMPLICITO
            # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement, values)
            if cur.fetchone() is None:
                raise Exception("O leilão ainda não terminou ou encontra-se cancelado")

            cur.execute(statement2, value)
            row = cur.fetchone()
            cur.execute("COMMIT;")
            result = {"leilaoId": row[0], "dataInicio": row[1], "dataFim": row[2], "precoMinimo": float(row[3]),
                      "artigoId": row[4], "titulo": payload["titulo"], "descricao": payload[
                    "descricao"]}
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro", str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Efetuar uma licitação num leilão | get | GET | PARAM: leilao_id, licitacao   [*** SELO DE QUALIDADE ***]
# REQUEST (GET)  - ---
# RESPONSE       - "Sucesso" em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/licitar/<leilao_id>/<licitacao>", methods=['GET'])
def licitar(leilao_id, licitacao):
    logger.info("### GET /dbproj/licitar/<leilao_id>/<licitacao> ###")

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    res_bool, res_str = get_id_by_token(cur, token)

    if res_bool is False:
        result = {"erro": res_str}

    else:
        licitacao = float(licitacao)

        statement_leilao = """ 
            SELECT preco_minimo 
                FROM leilao 
                    WHERE data_fim > CURRENT_TIMESTAMP 
                        AND is_canceled = FALSE 
                        AND leilao_id = %s ; """

        values_leilao = (leilao_id,)

        statement_licitacao = """ 
            SELECT pessoa_user_id, valor 
                FROM licitacao 
                    WHERE is_valido = TRUE 
                        AND valor = (SELECT MAX(valor) 
                                        FROM licitacao 
                                            WHERE is_valido = TRUE 
                                                AND leilao_leilao_id = %s) 
                        AND leilao_leilao_id = %s ; """

        values_licitacao = (leilao_id, leilao_id)

        statement_licitacao_inserir = """ 
                    INSERT INTO licitacao (data_licitacao, valor, pessoa_user_id, leilao_leilao_id) 
                        VALUES (CURRENT_TIMESTAMP, %s, %s, %s) 
                    RETURNING data_licitacao ; """

        values_licitacao_inserir = (str(licitacao), res_str, leilao_id)

        statement_not_licitacao = """
            INSERT INTO not_licitacao (licitacao_data_licitacao, licitacao_pessoa_user_id, licitacao_leilao_leilao_id, 
                    notificacao_data_not, notificacao_msg, notificacao_is_read, notificacao_pessoa_user_id)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, FALSE, %s) ; """

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            cur.execute("LOCK TABLE licitacao IN ACCESS EXCLUSIVE MODE;")
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement_leilao, values_leilao)
            preco_minimo = cur.fetchone()

            cur.execute(statement_licitacao, values_licitacao)
            licitacao_atual = cur.fetchone()

            if preco_minimo is None or preco_minimo[0] == "" or licitacao <= float(preco_minimo[0]) or \
                    (licitacao_atual is not None and licitacao_atual[0] != "" and
                     licitacao <= float(licitacao_atual[1])):
                cur.execute("ROLLBACK;")
                result = {"erro": "leilaoId invalido, possiveis razoes: ou id nao existe, "
                                  "ou ja terminado, ou cancelado por um admin, ou licitacao inferior ao precoMinimo "
                                  "ou a ultima licitacao ja existente"}

            else:
                cur.execute(statement_licitacao_inserir, values_licitacao_inserir)
                data_inserida = cur.fetchone()
                if licitacao_atual is not None and licitacao_atual[0] != "":
                    values_not_licitacao = (data_inserida[0], res_str, leilao_id, "Licitação ultrapassada por alguem.",
                                            licitacao_atual[0])
                    cur.execute(statement_not_licitacao, values_not_licitacao)
                cur.execute("COMMIT;")
                result = {"sucesso": "foi inserido com sucesso"}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Listar todos os leilões em que o utilizador tenha atividade | get | GET   [*** SELO DE QUALIDADE ***]
# REQUEST (GET)  - ---
# RESPONSE       - [ {“leilaoId”: 1, “descricao”: “desc1”}, {“leilaoId”: 2, “descricao”: “desc2”} ] em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/leiloes/atividade", methods=['GET'])
def get_atividade_leiloes():
    logger.info("### GET /dbproj/leiloes/atividade ###")

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)
    if res_bool is False:
        result = {"erro": res_str}

    else:
        statement = """ SELECT d.leilao_leilao_id, d.descricao
                                FROM leilao e, leilao_descricao d
                                    WHERE e.pessoa_user_id = %s
                                        AND d.data_modificao =  (SELECT MAX(j.data_modificao) 
                                                                    FROM leilao_descricao j 
                                                                        WHERE j.leilao_leilao_id = e.leilao_id)
                                        AND d.leilao_leilao_id = e.leilao_id
                        UNION DISTINCT 
                        SELECT d.leilao_leilao_id, d.descricao
                                FROM leilao_descricao d, licitacao l 
                                    WHERE d.leilao_leilao_id = l.leilao_leilao_id
                                        AND l.pessoa_user_id = %s
                                        AND d.data_modificao =  (SELECT MAX(j.data_modificao) 
                                                                    FROM leilao_descricao j 
                                                                        WHERE j.leilao_leilao_id = d.leilao_leilao_id)
            ; """

        values = (res_str, res_str)

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            cur.execute("SET TRANSACTION READ ONLY;")

            # LOCK IMPLICITO
            # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement, values)
            rows = cur.fetchall()
            cur.execute("COMMIT;")
            result = []

            for row in rows:
                content = {"leilaoId": row[0], "descricao": row[1]}
                result.append(content)

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Consultar detalhes de um leilão | get | GET | PARAM: leilao_id      [*** SELO DE QUALIDADE ***]
# REQUEST (GET)  - ---
# RESPONSE       - {“leilaoId”: 1, “titulo”: “tit”, “descricao”: “desc1”, "artigoId": "1", "precoMinimo": 10.0,
#                   "dataInicio": "3", "dataFim": "4", "mensagens": [ { "data": "31/05/2021 15:28:00", "mensagem":
#                   "isto é uma mensagem", "userId": "123" }, ... ],
#                   "licitacoes": [ { "data": "31/05/2021 15:28:00", "valor": 15.0, "userId": "123" }, ... ] }
#                   em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/leilao/<leilao_id>", methods=['GET'])
def get_leilao(leilao_id):
    logger.info("### GET /dbproj/leilao/<leilao_id> ###")

    logger.debug(f'artigo_codigo: {leilao_id}')

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    res_bool, res_str = get_id_by_token(cur, token)
    if res_bool is False:
        result = {"erro": res_str}

    else:
        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            cur.execute("SET TRANSACTION READ ONLY;")

            # LOCK IMPLICITO
            # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(""" 
                SELECT e.leilao_id, e.artigo_codigo, e.preco_minimo, e.data_inicio, e.data_fim, d.descricao, d.titulo 
                    FROM leilao e, leilao_descricao d 
                        WHERE e.leilao_id = %s 
                            AND d.data_modificao = (SELECT MAX(j.data_modificao) 
                                                        FROM leilao_descricao j
                                                            WHERE j.leilao_leilao_id = e.leilao_id)
                            AND d.leilao_leilao_id = e.leilao_id ; """, (leilao_id,))

            info_leilao = cur.fetchone()

            if info_leilao is None or info_leilao[0] == "":
                cur.execute("ROLLBACK;")
                result = {"erro": "leilaoId invalido, possiveis razoes: id nao existe"}

            else:
                cur.execute(""" SELECT data_msg, msg, pessoa_user_id 
                                    FROM mensagem 
                                        WHERE leilao_leilao_id = %s 
                                            ORDER BY data_msg ; """, (leilao_id,))

                info_mensagem = cur.fetchall()

                cur.execute(""" SELECT data_licitacao, valor, pessoa_user_id 
                                    FROM licitacao 
                                        WHERE leilao_leilao_id = %s 
                                            ORDER BY data_licitacao ; """, (leilao_id,))

                info_licitacoes = cur.fetchall()

                cur.execute("COMMIT;")

                listinha = []
                listona = []

                for row in info_mensagem:
                    content = {'data': row[0], 'mensagem': row[1], 'userId': row[2]}
                    listinha.append(content)

                for row in info_licitacoes:
                    content = {'data': row[0], 'valor': float(row[1]), 'userId': row[2]}
                    listona.append(content)

                result = {'leilao_id': info_leilao[0], 'titulo': info_leilao[6], 'descricao': info_leilao[5],
                          'artigoId': info_leilao[1], 'precoMinimo': float(info_leilao[2]),
                          'dataInicio': info_leilao[3], 'dataFim': info_leilao[4], 'mensagens': listinha,
                          "licitacoes": listona}

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Pesquisar leilões existentes | get | GET | PARAM: keyword     [*** SELO DE QUALIDADE ***]
# REQUEST (GET)  - ---
# RESPONSE       - [ {“leilaoId”: 1, “descricao”: “desc1”}, {“leilaoId”: 2, “descricao”: “desc2”} ] em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/leiloes/<keyword>", methods=['GET'])
def pesquisa_lista_leiloes(keyword):
    logger.info("### GET /dbproj/leiloes/<keyword> ###")

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)

    if res_bool is False:
        result = {"erro": res_str}

    else:
        statement = """ SELECT d.leilao_leilao_id, d.descricao 
                            FROM leilao e, leilao_descricao d, artigo a
                                WHERE e.data_fim > CURRENT_TIMESTAMP  
                                    AND e.leilao_id = d.leilao_leilao_id
                                    AND e.is_canceled = FALSE 
                                    AND d.data_modificao =  (SELECT MAX(j.data_modificao) 
                                                                FROM leilao_descricao j 
                                                                    WHERE j.leilao_leilao_id = d.leilao_leilao_id )
                                    AND e.artigo_codigo = a.codigo
                                    AND ( UPPER(a.codigo) LIKE UPPER(%s) OR UPPER(a.descricao) LIKE UPPER(%s) )
                                    ; """

        values = (str("%" + keyword + "%"), str("%" + keyword + "%"))

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            cur.execute("SET TRANSACTION READ ONLY;")

            # LOCK IMPLICITO
            # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement, values)
            rows = cur.fetchall()
            cur.execute("COMMIT;")
            result = []

            for row in rows:
                content = {"leilaoId": row[0], "descricao": row[1]}
                result.append(content)

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Listar todos os leilões existentes | get | GET   [*** SELO DE QUALIDADE ***]
# REQUEST (GET)  - ---
# RESPONSE       - [ {“leilaoId”: 1, “descricao”: “desc1”}, {“leilaoId”: 2, “descricao”: “desc2”} ] em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/leiloes", methods=['GET'])
def get_lista_leiloes():
    logger.info("### GET /dbproj/leiloes ###")

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)
    if res_bool is False:
        result = {"erro": res_str}

    else:
        statement = """ SELECT d.leilao_leilao_id, d.descricao
                            FROM leilao e, leilao_descricao d
                                WHERE e.data_fim > CURRENT_TIMESTAMP
                                    AND e.is_canceled = FALSE
                                    AND d.data_modificao =  (SELECT MAX(j.data_modificao) 
                                                                FROM leilao_descricao j 
                                                                    WHERE j.leilao_leilao_id = d.leilao_leilao_id)
                                    AND d.leilao_leilao_id = e.leilao_id ; """

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            cur.execute("SET TRANSACTION READ ONLY;")

            # LOCK IMPLICITO
            # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement)
            rows = cur.fetchall()
            cur.execute("COMMIT;")
            result = []

            for row in rows:
                content = {"leilaoId": row[0], "descricao": row[1]}
                result.append(content)

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Criar um novo leilão | add | POST   [*** SELO DE QUALIDADE ***]
# REQUEST (POST) - { "artigoId": "0000000000001", "precoMinimo": 10.0, "titulo": "Titulo do Novo Leilão",
#   "descricao": "Descrição do Novo Leilão","dataInicio": "31/05/2021 12:00:00", "dataFim": "01/06/2021 13:00:00" }
# RESPONSE       - {“leilaoId”: novoLeilaoId} em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/leilao", methods=['POST'])
def criar_leilao():
    logger.info("### POST /dbproj/leilao ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    logger.info("---- novo leilao  ----")
    logger.debug(f'payload: {payload}')

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]

    res_bool, res_str = get_id_by_token(cur, token)
    if res_bool is False:
        result = {"erro": res_str}

    else:
        statement_leilao = """
                INSERT INTO leilao (data_inicio, data_fim, preco_minimo, artigo_codigo, pessoa_user_id) 
                    VALUES (TO_TIMESTAMP(%s, 'DD/MM/YYYY HH24:MI:SS'), 
                        TO_TIMESTAMP(%s, 'DD/MM/YYYY HH24:MI:SS'), %s, %s, %s) 
                RETURNING leilao_id ; """

        statement_leilao_descricao = """
                        INSERT INTO leilao_descricao (data_modificao, descricao, titulo, leilao_leilao_id) 
                            VALUES (CURRENT_TIMESTAMP, %s, %s, %s) ; """

        values_leilao = (payload["dataInicio"], payload["dataFim"], payload["precoMinimo"],
                         payload["artigoId"], res_str)

        try:
            cur.execute("BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
            # https://www.postgresql.org/docs/9.5/transaction-iso.html

            # LOCK IMPLICITO
            # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
            # https://www.postgresql.org/docs/9.1/sql-lock.html
            # https://www.postgresql.org/docs/9.1/explicit-locking.html

            cur.execute(statement_leilao, values_leilao)
            leilao_id = cur.fetchone()[0]
            values_leilao_descricao = (payload["descricao"], payload["titulo"], leilao_id)
            cur.execute(statement_leilao_descricao, values_leilao_descricao)
            cur.execute("COMMIT;")
            result = {"leilaoId": leilao_id}
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            cur.execute("ROLLBACK;")
            result = {"erro": str(error)}

    if conn is not None:
        conn.close()

    return jsonify(result)


# Registo do utilizador | add | POST   [*** SELO DE QUALIDADE ***]
# REQUEST (POST) - {"username": username, "email": email, "password": password}
# RESPONSE       - {"userId": novoUserId} em caso de sucesso
# RESPONSE       - {"erro" : errorCode}   em caso de erro
@app.route("/dbproj/user", methods=['POST'])
def registar_utilizador():
    logger.info("### POST /dbproj/user ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    logger.info("---- new user ----")
    logger.debug(f'payload: {payload}')

    statement = """ INSERT INTO pessoa (username, password, email) VALUES (%s, %s, %s) 
                        RETURNING user_id ; """

    values = (payload["username"], payload["password"], payload["email"])

    try:
        cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
        # https://www.postgresql.org/docs/9.5/transaction-iso.html

        # LOCK IMPLICITO
        # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
        # https://www.postgresql.org/docs/9.1/sql-lock.html
        # https://www.postgresql.org/docs/9.1/explicit-locking.html

        cur.execute(statement, values)
        user_id = cur.fetchone()[0]  # user_id
        cur.execute("COMMIT;")
        result = {"userId": user_id}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute("ROLLBACK;")
        result = {"erro": str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


# Autenticação do utilizador | update | PUT   [*** SELO DE QUALIDADE ***]
# REQUEST (PUT) - {"username": username, "password": password}
# RESPONSE      - {"authToken": authToken} em caso de sucesso
# RESPONSE      - {"erro" : AuthError}     em caso de erro
@app.route("/dbproj/user", methods=['PUT'])
def autenticar_utilizador():
    logger.info("### PUT /dbproj/user ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    cur.execute("ROLLBACK;")

    logger.info("---- authenticate user ----")
    logger.debug(f'payload: {payload}')

    statement = """
        UPDATE pessoa AS p SET (token, validade_token) = (uuid_generate_v4(), CURRENT_TIMESTAMP + INTERVAL '%s hours') 
            WHERE p.username = %s AND p.password = %s AND p.is_banido = FALSE
                RETURNING p.token; """

    values = (token_ttl, payload["username"], payload["password"])

    try:
        cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
        # https://www.postgresql.org/docs/9.5/transaction-iso.html

        # LOCK IMPLICITO
        # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
        # https://www.postgresql.org/docs/9.1/sql-lock.html
        # https://www.postgresql.org/docs/9.1/explicit-locking.html

        cur.execute(statement, values)
        auth_token = cur.fetchone()

        if auth_token is None:
            raise Exception("O userId nao existe ou foi banido.")

        auth_token = auth_token[0]  # user_id
        cur.execute("COMMIT;")
        result = {"authToken": auth_token}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute("ROLLBACK;")
        result = {"erro": str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


# ACESSO DATABASE   [*** SELO DE QUALIDADE ***]
def db_connection():
    db = psycopg2.connect(user="admin", password="admin", host="dbproj", port="5432", database="dbproj")
    return db


# Get User ID a partir do Token (verifica-o e atualiza a data do ultimo acesso)   [*** SELO DE QUALIDADE ***]
def get_id_by_token(cur, token):
    statement = """ SELECT user_id 
                        FROM pessoa 
                            WHERE token = %s 
                                AND validade_token > CURRENT_TIMESTAMP 
                                AND is_banido = False
                                FOR UPDATE; """

    values = (token,)

    try:
        cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
        # https://www.postgresql.org/docs/9.5/transaction-iso.html

        # LOCK IMPLICITO
        # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
        # https://www.postgresql.org/docs/9.1/sql-lock.html
        # https://www.postgresql.org/docs/9.1/explicit-locking.html

        cur.execute(statement, values)
        res_str = cur.fetchone()  # user_id
        if res_str is None or res_str[0] == "":
            res_bool = False
            res_str = "Token invalido"
            cur.execute("ROLLBACK;")
        else:
            res_str = res_str[0]
            res_bool = True
            cur.execute(""" UPDATE pessoa SET data_ultimo_acesso = CURRENT_TIMESTAMP WHERE user_id = %s ; """,
                        (res_str,))
            cur.execute("COMMIT;")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute("ROLLBACK;")
        res_str = str(error)
        res_bool = False

    return res_bool, res_str


# verifica se é admin   [*** SELO DE QUALIDADE ***]
def is_admin(cur, user_id):
    statement = """ SELECT is_admin FROM pessoa WHERE user_id = %s ; """

    values = (user_id,)

    try:
        cur.execute("BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;")
        # https://www.postgresql.org/docs/9.1/sql-start-transaction.html
        # https://www.postgresql.org/docs/9.5/transaction-iso.html

        cur.execute("SET TRANSACTION READ ONLY;")

        # cur.execute("LOCK ? IN ? MODE ; ")  # ESCOLHER UM
        # https://www.postgresql.org/docs/9.1/sql-lock.html
        # https://www.postgresql.org/docs/9.1/explicit-locking.html

        cur.execute(statement, values)
        res_str = cur.fetchone()  # user_id
        if res_str is None or res_str[0] == "":
            res_bool = False
            res_str = "Token invalido"
            cur.execute("ROLLBACK;")
        else:
            res_str = res_str[0]
            res_bool = True
            cur.execute("COMMIT;")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        cur.execute("ROLLBACK;")
        res_str = str(error)
        res_bool = False

    return res_bool, res_str


# Rotina gera notificações de mensagem by leilaoId (SEM COMMIT)     [*** SELO DE QUALIDADE ***]
def envia_notifs_msg(cur, data_msg, leilao_id, msg, pessoa_id):
    statement = """ 
        INSERT INTO not_msg (mensagem_data_msg, mensagem_pessoa_user_id, mensagem_leilao_leilao_id, 
                notificacao_data_not, notificacao_msg, notificacao_pessoa_user_id)
            (SELECT %s, %s ::uuid, %s ::uuid, CURRENT_TIMESTAMP, %s, l.pessoa_user_id 
                FROM licitacao l
                    WHERE l.leilao_leilao_id = %s ::uuid
                        GROUP BY l.pessoa_user_id
            UNION DISTINCT
            SELECT %s, %s ::uuid, %s ::uuid, CURRENT_TIMESTAMP, %s, e.pessoa_user_id 
                FROM leilao e
                    WHERE e.leilao_id = %s ::uuid)
        ; """

    values = (data_msg, pessoa_id, leilao_id, msg, leilao_id, data_msg, pessoa_id, leilao_id, msg, leilao_id)

    cur.execute(statement, values)


# MAIN   [*** SELO DE QUALIDADE ***]
if __name__ == "__main__":
    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    time.sleep(1)  # just to let the DB start before this print :-)

    logger.info("\n---------------------------------------------------------------\n" +
                "API Projeto Leilões Online: http://localhost:8080/dbproj\n\n")

    app.run(host="0.0.0.0", debug=True, threaded=True)
