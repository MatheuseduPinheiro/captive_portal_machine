from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from models.model import Conexao
import re
import hashlib

# Definindo o blueprint como 'app'
app = Blueprint('app', __name__)

@app.route('/')
@app.route('/portalogin/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Hash da senha para verificar com o banco de dados
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Usando a classe Conexao para obter dados
        conn = Conexao()
        cursor = conn.cursor

        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, hashed_password))
        account = cursor.fetchone()
        conn.close()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect('https://www.google.com')

        else:
            flash("Incorrect username/password!", "danger")
    
    return render_template('login.html', title="Login")

@app.route('/portalogin/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            # Verificar se os campos não estão vazios
            if not username or not password or not email:
                flash("All fields are required!", "danger")
                return render_template('register.html', title="Register")

            # Verificar o formato do email
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash("Invalid email address!", "danger")
                return render_template('register.html', title="Register")

            # Verificar o formato do nome de usuário
            if not re.match(r'[A-Za-z0-9]+', username):
                flash("Username must contain only characters and numbers!", "danger")
                return render_template('register.html', title="Register")

            # Hash da senha para segurança
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Usar a classe Conexao para gerenciar a conexão
            conn = Conexao()
            cursor = conn.cursor

            try:
                # Verificar se o nome de usuário ou email já está em uso
                cursor.execute('SELECT * FROM accounts WHERE username = %s OR email = %s', (username, email))
                existing_user = cursor.fetchone()

                if existing_user:
                    flash("Username or email already exists!", "danger")
                else:
                    # Inserir novo usuário no banco de dados
                    cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)', (username, hashed_password, email))
                    conn.connection.commit()  # Commit usando a conexão, não o cursor
                    flash("Registration successful! You can now log in.", "success")
                    return redirect(url_for('app.login'))  # Corrigido para referenciar a rota do blueprint

            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")

            finally:
                conn.close()

    return render_template('register.html', title="Register")

