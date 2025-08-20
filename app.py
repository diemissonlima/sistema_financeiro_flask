import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import locale
from decimal import Decimal
from models import database
from scripts import utils
from datetime import date, datetime


app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
database.criar_database()
locale.setlocale(locale.LC_ALL, "pt-BR.UTF-8")


def hash_password(password):
    return generate_password_hash(password)


def atualizar_parcela_vencida():
    conn = database.get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE contas_pagar SET status = 'Vencida' "
                           "WHERE status = 'Pendente' AND data_vencimento < CURDATE()")

            conn.commit()

    except pymysql.MySQLError as error:
        print(f"Erro ao atualizar parcela vencida: {error}")


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = database.obter_usuario(username)

        if user:
            if check_password_hash(user['senha'], password):
                session['user_id'] = user['id']
                session['username'] = user['nome']
                flash('Login realizado com sucesso!', 'success')

                atualizar_parcela_vencida()
                database.atualizar_juros()
                return redirect(url_for('dashboard'))
            else:
                flash('Senha inválida!', 'error')
        else:
            flash('Usuário não encontrado!', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('As senhas não coincidem!', 'error')
            return render_template('register.html')

        database.criar_usuario({
            "nome": username,
            "email": email,
            "senha": hash_password(password),
            "data_cadastro": date.today()
        })

        flash('Usuario cadastrado com sucesso', 'sucesso')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = database.get_connection()

    with conn.cursor() as cursor:
        cursor.execute('SELECT SUM(valor_a_receber) as valor_pagar FROM contas_pagar '
                       f'WHERE id_usuario = {session["user_id"]} AND status IN ("Pendente", "Parcial", "Vencida")')

        total_pagar = cursor.fetchone()

        cursor.execute('SELECT SUM(valor_parcela) - SUM(valor_pago) AS total FROM contas_receber '
                       f'WHERE id_usuario = {session["user_id"]} AND status IN ("Pendente", "Parcial")')

        total_receber = cursor.fetchone()

        if total_receber['total'] is None:
            total_receber['total'] = 0

        cursor.execute(f'SELECT COUNT(*) as count FROM fornecedores WHERE id_usuario = {session["user_id"]}')

        total_suppliers = cursor.fetchone()

        cursor.execute('SELECT contas_pagar.descricao, contas_pagar.valor_parcela, contas_pagar.data_vencimento,'
                       'fornecedores.razao_social, contas_pagar.`status`, contas_pagar.tipo_conta '
                       'FROM contas_pagar '
                       'INNER JOIN fornecedores '
                       f'ON contas_pagar.id_fornecedor=fornecedores.codigo WHERE contas_pagar.id_usuario = {session["user_id"]} '
                       'ORDER BY contas_pagar.id DESC LIMIT 5')

        contas_pagar = cursor.fetchall()

        cursor.execute('SELECT contas_receber.descricao, contas_receber.valor_parcela, contas_receber.data_vencimento,'
                       'fornecedores.razao_social, contas_receber.`status`, contas_receber.tipo_conta '
                       'FROM contas_receber '
                       'INNER JOIN fornecedores '
                       f'ON contas_receber.id_fornecedor=fornecedores.codigo WHERE contas_receber.id_usuario = {session["user_id"]} '
                       'ORDER BY contas_receber.id DESC LIMIT 5')

        contas_receber = cursor.fetchall()

        for conta in contas_pagar:
            conta['valor_parcela'] = locale.currency(conta['valor_parcela'], grouping=True, symbol=True)

        for conta in contas_receber:
            conta['valor_parcela'] = locale.currency(conta['valor_parcela'], grouping=True, symbol=True)

        contas_recentes_pagar = contas_pagar[:]
        contas_recentes_receber = contas_receber[:]

    return render_template('dashboard.html',
                           total_pagar=locale.currency(total_pagar['valor_pagar'], grouping=True, symbol=True),
                           total_receber=locale.currency(total_receber['total'], grouping=True, symbol=True),
                           total_suppliers=total_suppliers['count'],
                           contas_recentes_pagar=contas_recentes_pagar,
                           contas_recentes_receber=contas_recentes_receber)


@app.route('/suppliers')
def suppliers():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    fornecedores = database.obter_fornecedores()

    for fornecedor in fornecedores:
        data_formatada = fornecedor['data_cadastro'].strftime('%d/%m/%Y')
        fornecedor['data_cadastro'] = data_formatada

    return render_template('suppliers.html', suppliers=fornecedores)


@app.route('/suppliers/new', methods=['GET', 'POST'])
def new_supplier():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        fornecedor = {
            'data_cadastro': date.today(),
            'razao_social': request.form['name'],
            'nome_fantasia': request.form['fantasia'],
            'email': request.form['email'],
            'telefone': request.form['phone'],
            'celular': request.form['celular'],
            'cnpj': request.form['cnpj'],
            'cpf': '',
            'endereco': request.form['endereco'],
            'numero': request.form['numero'],
            'bairro': request.form['bairro'],
            'cep': request.form['cep'],
            'municipio': request.form['municipio'],
            'estado': request.form['estado']
        }

        database.criar_fornecedor(fornecedor)

        flash('Fornecedor cadastrado com sucesso!', 'success')
        return redirect(url_for('suppliers'))

    return render_template('new_supplier.html')


@app.route('/accounts')
def accounts():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    database.atualizar_juros()

    contas = database.obter_contas_pagar('todos', 'contas_pagar')

    total_pago = 0
    total_a_pagar = 0
    for conta in contas:
        total_pago += Decimal(conta['valor_pago'])
        total_a_pagar += Decimal(conta['valor_a_receber'])

        conta['valor_parcela'] = locale.currency(conta['valor_parcela'], grouping=True, symbol=True)
        conta['valor_pago'] = locale.currency(conta['valor_pago'], grouping=True, symbol=True)
        conta['juros'] = locale.currency(conta['juros'], grouping=True, symbol=True)
        conta['juros_pago'] = locale.currency(conta['juros_pago'], grouping=True, symbol=True)

    return render_template('accounts.html', contas=contas,
                           total_pago=locale.currency(total_pago, grouping=True, symbol=True),
                           total_a_pagar=locale.currency(total_a_pagar, grouping=True, symbol=True))


@app.route('/accounts_receive')
def accounts_receive():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    contas = database.obter_contas_pagar('todos', 'contas_receber')

    total_a_receber = 0
    total_recebido = 0
    for conta in contas:
        total_a_receber += Decimal(conta['valor_parcela'])
        total_recebido += Decimal(conta['valor_pago'])

        conta['valor_parcela'] = locale.currency(conta['valor_parcela'], grouping=True, symbol=True)
        conta['valor_pago'] = locale.currency(conta['valor_pago'], grouping=True, symbol=True)

    return render_template('accounts_receive.html', contas=contas,
                           total_a_receber=locale.currency(total_a_receber - total_recebido, grouping=True, symbol=True),
                           total_recebido=locale.currency(total_recebido, grouping=True, symbol=True))


@app.route('/accounts/new', methods=['GET', 'POST'])
def new_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        account_type = request.form['type']
        data_lancamento = request.form['data_lancamento']
        supplier_id = request.form['fornecedor_id']

        parcelas = []
        for i in range(0, 100):
            numero = request.form.get(f'parcelas[{i}][numero]')
            valor = request.form.get(f'parcelas[{i}][valor]')
            vencimento = request.form.get(f'parcelas[{i}][vencimento]')

            if numero and valor and vencimento:
                parcelas.append({
                    "numero": int(numero),
                    "valor": float(valor),
                    "vencimento": vencimento  # ou converta para datetime
                })

        lista_contas = []
        if len(parcelas) != 0:
            for conta in parcelas:
                lista_contas.append({
                    'id_usuario': session['user_id'],
                    'descricao': description,
                    'valor': amount,
                    'data_lancamento': data_lancamento,
                    'data_vencimento': conta['vencimento'],
                    'juros': 0.0,
                    'id_fornecedor': supplier_id,
                    'numero_parcela': conta['numero'],
                    'valor_parcela': conta['valor'],
                    'tipo_conta': account_type
                })

        conn = database.get_connection()

        with conn.cursor() as cursor:
            data_atual = date.today()

            for conta in lista_contas:
                status_conta = 'Pendente'
                data_vencimento = datetime.strptime(conta['data_vencimento'], "%Y-%m-%d").date()

                if data_vencimento < data_atual:
                    status_conta = 'Vencida'

                    conta['juros'] = float(utils.calcular_juros(conta['valor_parcela'], data_vencimento))

                valor_a_receber = conta['valor_parcela'] + conta['juros']

                query = (
                    f'INSERT INTO contas_{account_type} (id_usuario, descricao, valor, data_lancamento, data_vencimento, '
                    'juros, status, id_fornecedor, numero_parcela, valor_parcela, valor_a_receber, tipo_conta)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                )

                data = conta['id_usuario'], conta['descricao'], conta['valor'], conta['data_lancamento'], \
                    conta['data_vencimento'], conta['juros'], status_conta, conta['id_fornecedor'], \
                    conta['numero_parcela'], conta['valor_parcela'], valor_a_receber, conta['tipo_conta']

                cursor.execute(query, data)
                conn.commit()

        flash('Lançamento cadastrado com sucesso!', 'success')

        if account_type == 'pagar':
            return redirect(url_for('accounts'))
        else:
            return redirect(url_for('accounts_receive'))

    fornecedores = database.obter_fornecedores()

    return render_template('new_account.html', suppliers=fornecedores)


@app.route('/accounts/<int:account_id>/pay/<tipo_conta>', methods=['POST', 'GET'])
def pay_account(account_id, tipo_conta):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    data_atual = date.today()

    conta = []
    if account_id:
        if tipo_conta == 'pagar':
            conta = database.obter_contas_pagar('unico', id_conta=account_id, tabela='contas_pagar')
        elif tipo_conta == 'receber':
            conta = database.obter_contas_pagar('unico', id_conta=account_id, tabela='contas_receber')

    if request.method == 'POST':
        tipo_pagamento = request.form['tipo_pagamento']
        data_recebimento = request.form['data_recebimento']
        valor_parcela = request.form['valor_parcela'].replace(',', '.')
        desconto = request.form['valor_desconto'].replace(',', '.')
        multa = request.form['valor_multa'].replace(',', '.')
        juros = request.form['valor_juros'].replace(',', '.')
        juros_pago = conta[0]['juros_pago']
        recebido = request.form['valor_recebido'].replace(',', '.')
        saldo = request.form['valor_saldo'].replace(',', '.')
        observacao = request.form['observacao']

        conta[0]['valor_pago'] += Decimal(recebido)
        conta[0]['valor_a_receber'] -= Decimal(recebido)

        if conta[0]['valor_a_receber'] == 0:
            conta[0]['status'] = 'Pago'
        elif conta[0]['valor_a_receber'] > 0:
            conta[0]['status'] = 'Parcial'

        if float(recebido) >= float(juros):
            recebido = float(recebido) - float(juros)
            conta[0]['juros_pago'] += Decimal(juros)
            juros = 0.0

        conn = database.get_connection()
        with conn.cursor() as cursor:
            query = (f"INSERT INTO contas_{tipo_conta}_recebimento (id_contas_{tipo_conta}, data_recebimento, descricao_pagamento, "
                     "observacao, valor_parcela, desconto, multa, juros, recebido, total_a_receber) "
                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

            data = account_id, data_recebimento, tipo_pagamento, observacao, conta[0]['valor_parcela'], float(desconto), \
                float(multa), float(juros), float(recebido), float(saldo)

            cursor.execute(query, data)
            conn.commit()

            query = (f"UPDATE contas_{tipo_conta} SET valor_pago = %s, status = %s, juros = %s, juros_pago = %s, "
                     f"valor_a_receber = %s WHERE id = %s")

            data = float(conta[0]['valor_pago']), conta[0]['status'], juros, float(conta[0]['juros_pago']), saldo, account_id

            cursor.execute(query, data)
            conn.commit()

        flash("Conta baixada com sucesso", "sucesso")
        if tipo_conta == 'pagar':
            return redirect(url_for('accounts'))
        else:
            return redirect(url_for('accounts_receive'))

    return render_template('pay_account.html', account=conta[0], tipo_conta=tipo_conta, data_atual=data_atual)


@app.route('/get_supplier_data/<cnpj>', methods=['GET'])
def get_supplier_data(cnpj):
    try:
        # remove qualquer caractere que nao seja numero
        cnpj = ''.join(filter(str.isdigit, cnpj))

        # faz a requisicao
        response = requests.get(f"https://www.receitaws.com.br/v1/cnpj/{cnpj}")

        # verifica se a requisicao foi bem sucedida
        if response.status_code != 200:
            return jsonify({'error': 'Erro ao consultar CNPJ'}), response.status_code

        data = response.json()

        return jsonify(data)

    except Exception as e:
        print(f"Erro ao consultar CNPJ: {e}")
        return jsonify({"error": "Erro interno do servidor."}), 500


@app.route('/get_account_info/<account_type>/<account_id>', methods=['GET'])
def get_account_info(account_type, account_id):
    detalhes_conta = {
        'tipo_conta': account_type,
        'id da conta': account_id
    }

    return jsonify(detalhes_conta)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='192.168.100.156', port=5000, debug=True)
