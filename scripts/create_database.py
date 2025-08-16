import sqlite3
import hashlib
from datetime import datetime


def create_database():
    conn = sqlite3.connect('financial_app.db')
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de fornecedores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(20),
            cnpj VARCHAR(18),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de contas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description VARCHAR(200) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            type VARCHAR(20) NOT NULL CHECK (type IN ('pagar', 'receber')),
            status VARCHAR(20) DEFAULT 'pendente' CHECK (status IN ('pendente', 'pago', 'recebido')),
            due_date DATE NOT NULL,
            supplier_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
    ''')

    # Criar usuário admin padrão
    admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash)
        VALUES ('admin', 'admin@financeiro.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9')
    ''', (admin_password,))

    # Inserir alguns fornecedores de exemplo
    suppliers_data = [
        ('Fornecedor ABC Ltda', 'contato@abc.com', '(11) 1234-5678', '12.345.678/0001-90', 'Rua das Flores, 123'),
        ('Empresa XYZ S.A.', 'vendas@xyz.com', '(11) 9876-5432', '98.765.432/0001-10', 'Av. Principal, 456'),
        ('Serviços Tech', 'info@tech.com', '(11) 5555-0000', '11.222.333/0001-44', 'Rua da Tecnologia, 789')
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO suppliers (name, email, phone, cnpj, address)
        VALUES (?, ?, ?, ?, ?)
    ''', suppliers_data)

    conn.commit()
    conn.close()
    print("Database created successfully!")


if __name__ == "__main__":
    create_database()
