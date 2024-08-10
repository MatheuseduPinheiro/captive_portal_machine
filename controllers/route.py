from flask import Blueprint, get_flashed_messages, render_template, request, redirect, session, url_for, flash
from models.model import Conexao
import re
import hashlib
import os
from werkzeug.utils import secure_filename

# Definindo o blueprint como 'app'
app = Blueprint('app', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/portalogin/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']

            # Hash da senha para verificar com o banco de dados
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Usando a classe Conexao para obter dados
            conn = Conexao()
            cursor = conn.cursor

            # Execute a consulta para verificar se o nome de usuário e senha estão corretos
            cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, hashed_password))
            account = cursor.fetchone()
            conn.close()

            if account:
                # Se as credenciais estiverem corretas, configure a sessão e redirecione
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect("https://google.com")  # Redirecione para a rota protegida ou homepage
            else:
                # Se as credenciais estiverem incorretas, exiba uma mensagem de erro
                flash("Incorrect username or password!", "danger")
        else:
            # Se não houver nome de usuário ou senha no formulário
            flash("Please enter both username and password!", "warning")

    return render_template('login.html', title="Login")


@app.route('/portalogin/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form and 'email' in request.form and 'image' in request.files:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            image = request.files['image']

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

            # Verificar e salvar a imagem
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                image.save(filepath)
                image_path = filename  # Armazena apenas o nome do arquivo
            else:
                flash("Invalid file format. Only JPEG and JPG images are allowed!", "danger")
                return render_template('register.html', title="Register")  # Retorna o template com a mensagem de erro

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
                    cursor.execute('INSERT INTO accounts (username, password, email, image_path) VALUES (%s, %s, %s, %s)', (username, hashed_password, email, image_path))
                    conn.connection.commit()  # Commit usando a conexão, não o cursor
                    flash("Registration successful! You can now log in.", "success")
                    return redirect(url_for('app.login'))

            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")

            finally:
                conn.close()

    return render_template('register.html', title="Register")
