import pymysql
from flask import session
from pymysql import cursors
from scripts import utils
from decimal import Decimal


def get_connection():
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='1234',
        charset='utf8mb4',
        database='sistema_financeiro',
        cursorclass=pymysql.cursors.DictCursor
    )

    return conn


def criar_database():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            sql_create_contas_pagar = """
            CREATE TABLE IF NOT EXISTS contas_pagar (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT(10),
                descricao VARCHAR(255) NOT NULL,
                valor DECIMAL(10, 2) NOT NULL,
                data_lancamento DATE NOT NULL,
                data_vencimento DATE NOT NULL,
                status ENUM('Pendente', 'Pago', 'Parcial', 'Vencida', 'Inativa') DEFAULT 'Pendente',
                id_fornecedor INT NOT NULL,
                numero_parcela INT(10) NOT NULL,
                data_pagamento DATE NULL,
                valor_parcela DECIMAL(10, 2) NOT NULL,
                desconto DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
                multa DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
                juros DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
                valor_pago DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
                valor_a_receber DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
                tipo_conta VARCHAR(50) NOT NULL DEFAULT 'pagar',
                FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(codigo),
                FOREIGN KEY (id_usuario) REFERENCES usuario(id)
            );
            """

            sql_create_fornecedores = """
            CREATE TABLE IF NOT EXISTS fornecedores (
                codigo INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT(10),
                data_cadastro DATE NOT NULL,
                razao_social VARCHAR(150) NOT NULL,
                nome_fantasia VARCHAR(150),
                cpf VARCHAR(14) DEFAULT NULL,
                cnpj VARCHAR(18) DEFAULT NULL,
                rg VARCHAR(20),
                inscricao_estadual VARCHAR(20),
                endereco VARCHAR(150),
                numero VARCHAR(10),
                bairro VARCHAR(100),
                municipio VARCHAR(100),
                estado VARCHAR(2),
                pais VARCHAR(50) DEFAULT 'Brasil',
                cep VARCHAR(12),
                telefone VARCHAR(50),
                celular VARCHAR(20),
                email VARCHAR(100),
                status_cadastral ENUM('Ativo', 'Inativo') DEFAULT 'Ativo',
                FOREIGN KEY (id_usuario) REFERENCES usuario(id)
            );
            """

            sql_create_contas_pagar_recebimento = """
            CREATE TABLE IF NOT EXISTS contas_pagar_recebimento (
                id INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_contas_pagar INT(10) NOT NULL,
                data_recebimento DATE NOT NULL,
                descricao_pagamento VARCHAR(50) NOT NULL,
                observacao VARCHAR(250) NULL DEFAULT NULL,
                valor_parcela FLOAT(10,4) NULL DEFAULT NULL,
                desconto FLOAT(10,4) NULL DEFAULT NULL,
                multa FLOAT(10,4) NULL DEFAULT NULL,
                juros FLOAT(10,4) NULL DEFAULT NULL,
                recebido FLOAT(10,4) NULL DEFAULT NULL,
                total_a_receber FLOAT(10,4) NULL DEFAULT NULL,
                FOREIGN KEY (id_contas_pagar) REFERENCES contas_pagar(id)
            );"""

            sql_create_contas_receber = """
            CREATE TABLE IF NOT EXISTS contas_receber (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT(10),
                descricao VARCHAR(255) NOT NULL,
                valor DECIMAL(10, 2) NOT NULL,
                data_lancamento DATE NOT NULL,
                data_vencimento DATE NOT NULL,
                status ENUM('Pendente', 'Pago', 'Parcial', 'Vencida', 'Inativa') DEFAULT 'Pendente',
                id_fornecedor INT NOT NULL,
                numero_parcela INT(10) NOT NULL,
                data_pagamento DATE NULL,
                valor_parcela DECIMAL(10, 2) NOT NULL,
                desconto DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
                multa DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
                juros DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
                valor_pago DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
                tipo_conta VARCHAR(50) NOT NULL DEFAULT 'receber',
                FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(codigo),
                FOREIGN KEY (id_usuario) REFERENCES usuario(id)
                );
                """

            sql_create_contas_receber_recebimento = """
                CREATE TABLE IF NOT EXISTS contas_receber_recebimento (
                id INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_contas_receber INT(10) NOT NULL,
                data_recebimento DATE NOT NULL,
                descricao_pagamento VARCHAR(50) NOT NULL,
                observacao VARCHAR(250) NULL DEFAULT NULL,
                valor_parcela FLOAT(10,4) NULL DEFAULT NULL,
                desconto FLOAT(10,4) NULL DEFAULT NULL,
                multa FLOAT(10,4) NULL DEFAULT NULL,
                juros FLOAT(10,4) NULL DEFAULT NULL,
                recebido FLOAT(10,4) NULL DEFAULT NULL,
                total_a_receber FLOAT(10,4) NULL DEFAULT NULL,
                FOREIGN KEY (id_contas_receber) REFERENCES contas_receber(id)
            );
            """

            sql_create_usuario = """
                CREATE TABLE IF NOT EXISTS usuario (
                id INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                senha VARCHAR(255) NOT NULL,
                data_cadastro DATE NOT NULL,
                status ENUM('Ativo', 'Inativo') NULL DEFAULT 'Ativo'
            );
            """

            cursor.execute(sql_create_usuario)
            cursor.execute(sql_create_fornecedores)
            cursor.execute(sql_create_contas_pagar)
            cursor.execute(sql_create_contas_pagar_recebimento)
            cursor.execute(sql_create_contas_receber)
            cursor.execute(sql_create_contas_receber_recebimento)
            conn.commit()
    finally:
        conn.close()


def criar_usuario(usuario):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            query = ("INSERT INTO usuario (nome, email, senha, data_cadastro) "
                     "VALUES (%s, %s, %s, %s)")

            data = usuario["nome"], usuario["email"], usuario["senha"], usuario["data_cadastro"]

            cursor.execute(query, data)
            conn.commit()

    except pymysql.MySQLError as error:
        print(f"Erro ao cadastrar usuario: {error}")


def criar_fornecedor(fornecedor):
    conn = get_connection()

    if len(fornecedor["cnpj"]) != 14:
        fornecedor["cpf"] = fornecedor["cnpj"]
        fornecedor["cnpj"] = ""

    try:
        with conn.cursor() as cursor:

            query = ("INSERT INTO fornecedores (id_usuario, data_cadastro, razao_social, nome_fantasia, cpf, cnpj, "
                     "endereco, numero, bairro, municipio, estado, cep, telefone, celular, email)"
                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

            data = session["user_id"], fornecedor["data_cadastro"], fornecedor["razao_social"], \
                fornecedor["nome_fantasia"], fornecedor["cpf"], fornecedor["cnpj"], fornecedor["endereco"], \
                fornecedor["numero"], fornecedor["bairro"], fornecedor["municipio"], fornecedor["estado"], \
                fornecedor["cep"], fornecedor["telefone"], fornecedor["celular"], fornecedor["email"]

            cursor.execute(query, data)
            conn.commit()

    except pymysql.MySQLError as error:
        print(f"erro ao inserir fornecedor: {error}")


def obter_usuario(nome):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM usuario WHERE nome = %s"

            data = nome

            cursor.execute(query, data)
            usuario = cursor.fetchone()

            if usuario:
                return usuario
            else:
                return None

    except pymysql.MySQLError as error:
        print(f"Erro ao obter usuario: {error}")
        return None


def obter_fornecedores():
    conn = get_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(f"SELECT * FROM fornecedores WHERE id_usuario = {session['user_id']}")

            lista_fornecedores = cursor.fetchall()

            return lista_fornecedores

    except pymysql.MySQLError as error:
        print(f"erro ao recuperar dados dos fornecedores: {error}")

        return None


def obter_contas_pagar(tipo_consulta, tabela='', id_conta=0, id_fornecedor=0):
    conn = get_connection()

    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            if tipo_consulta == "todos":
                if tabela == "contas_pagar":
                    cursor.execute(
                        "SELECT contas_pagar.id, fornecedores.codigo AS id_fornecedor, fornecedores.razao_social, "
                        "contas_pagar.descricao, contas_pagar.valor, contas_pagar.data_lancamento, contas_pagar.data_vencimento, "
                        "contas_pagar.`status`, contas_pagar.valor_pago, contas_pagar.valor_parcela, contas_pagar.numero_parcela,"
                        "contas_pagar.multa, contas_pagar.juros, contas_pagar.juros_pago, contas_pagar.desconto, "
                        "contas_pagar.tipo_conta, contas_pagar.valor_a_receber "
                        "FROM contas_pagar INNER JOIN fornecedores ON fornecedores.codigo=contas_pagar.id_fornecedor "
                        f"WHERE contas_pagar.id_usuario = {session['user_id']} "
                        "ORDER BY contas_pagar.data_vencimento"
                    )
                elif tabela == "contas_receber":
                    cursor.execute(
                        "SELECT contas_receber.id, fornecedores.codigo AS id_fornecedor, fornecedores.razao_social, "
                        "contas_receber.descricao, contas_receber.valor, contas_receber.data_lancamento, "
                        "contas_receber.data_vencimento, "
                        "contas_receber.`status`, contas_receber.valor_pago, contas_receber.valor_parcela, "
                        "contas_receber.numero_parcela,"
                        "contas_receber.multa, contas_receber.juros, contas_receber.desconto, contas_receber.tipo_conta "
                        "FROM contas_receber INNER JOIN fornecedores ON fornecedores.codigo=contas_receber.id_fornecedor "
                        f"WHERE contas_receber.id_usuario = {session['user_id']} "
                        "ORDER BY contas_receber.data_vencimento"
                    )

                lista_conta = cursor.fetchall()

            elif tipo_consulta == "unico":
                if tabela == 'contas_pagar':
                    query = ("SELECT cp.id, cp.valor, cp.data_vencimento, cp.data_lancamento, cp.numero_parcela, "
                             "cp.valor_parcela, cp.valor_pago, cp.valor_a_receber, cp.tipo_conta, cp.status, "
                             "cp.desconto, cp.multa, cp.juros, cp.juros_pago, f.codigo AS id_fornecedor, f.razao_social "
                             "FROM contas_pagar AS cp "
                             "INNER JOIN fornecedores AS f "
                             "ON cp.id_fornecedor = f.codigo "
                             "WHERE cp.id = %s")

                elif tabela == 'contas_receber':
                    query = ("SELECT cr.id, cr.valor, cr.data_vencimento, cr.data_lancamento, cr.numero_parcela, "
                             "cr.valor_parcela, cr.valor_pago, cr.valor_parcela - cr.valor_pago AS valor_a_receber,"
                             "cr.tipo_conta, cr.status, cr.desconto, cr.multa, cr.juros, "
                             "f.codigo AS id_fornecedor, f.razao_social "
                             "FROM contas_receber AS cr "
                             "INNER JOIN fornecedores AS f "
                             "ON cr.id_fornecedor = f.codigo "
                             "WHERE cr.id = %s")

                data = id_conta

                cursor.execute(query, data)
                lista_conta = cursor.fetchall()

            elif tipo_consulta == "fornecedor":
                query = ("SELECT "
                         "cp.id AS id_conta, "
                         "cp.valor,"
                         "cp.data_vencimento,"
                         "cp.data_lancamento, "
                         "cp.numero_parcela, "
                         "cp.valor_parcela, "
                         "cp.valor_pago,"
                         "cp.valor_parcela - cp.valor_pago AS valor_a_receber,"
                         "f.codigo AS id_fornecedor,"
                         "f.razao_social "
                         "FROM contas_pagar AS cp "
                         "INNER JOIN fornecedores AS f "
                         "ON cp.id_fornecedor = f.codigo "
                         "WHERE cp.id_fornecedor = %s AND cp.status IN ('Pendente', 'Parcial', 'Vencida')")

                data = id_fornecedor

                cursor.execute(query, data)
                lista_conta = cursor.fetchall()

            return lista_conta

    except pymysql.MySQLError as error:
        print(f"erro ao recuperar dados: {error}")

        return None


def atualizar_juros():
    conn = get_connection()

    lista_contas = obter_contas_pagar('todos', 'contas_pagar')

    with conn.cursor() as cursor:
        for conta in lista_contas:
            juros = 0
            if conta['status'] in ['Parcial', 'Vencida']:
                juros = utils.calcular_juros(conta['valor_parcela'], conta['data_vencimento'])

            if juros:
                lista_baixa = consultar_baixa(conta['id'])

                if lista_baixa:
                    ultima_baixa = lista_baixa[-1]

                    juros = utils.calcular_juros(conta['valor_a_receber'], ultima_baixa['data_recebimento'])

                    total_parcela = Decimal(conta['valor_a_receber']) + Decimal(juros)

                    query = 'UPDATE contas_pagar SET juros = %s, valor_a_receber = %s WHERE id = %s'

                    data = juros, total_parcela, conta['id']

                    cursor.execute(query, data)
                    conn.commit()


def consultar_baixa(id_contas_pagar):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            query = "SELECT * FROM contas_pagar_recebimento WHERE id_contas_pagar = %s"

            data = id_contas_pagar

            cursor.execute(query, data)
            if cursor.rowcount > 0:
                lista_baixas = cursor.fetchall()

                return lista_baixas

            return None

    except pymysql.MySQLError as error:
        print(f'Erro ao consultar baixa: {error}')
        return None
