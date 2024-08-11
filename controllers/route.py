from flask import Blueprint, current_app, flash, render_template, request, redirect, session, url_for
import re
import hashlib
import os

app_blueprint = Blueprint('app', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app_blueprint.route('/')
@app_blueprint.route('/portalogin/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            # Hash da senha para verificar com o banco de dados
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Usando a conexão com o banco de dados
            cursor = current_app.mysql.connection.cursor()

            try:
                cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, hashed_password))
                account = cursor.fetchone()

                if account:
                    # Se as credenciais estiverem corretas, configure a sessão e redirecione
                    session['loggedin'] = True
                    session['id'] = account[0]
                    session['username'] = account[1]
                    return redirect("https://google.com")  # Redirecione para a rota protegida ou homepage
                else:
                    # Se as credenciais estiverem incorretas, exiba uma mensagem de erro
                    flash("Incorrect username or password!", "danger")
            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")
            finally:
                cursor.close()
        else:
            # Se não houver nome de usuário ou senha no formulário
            flash("Please enter both username and password!", "warning")

    return render_template('login.html', title="Login")

@app_blueprint.route('/portalogin/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        image = request.files.get('image')

        if username and password and email and image:
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
                image_data = image.read()
                image_hash = hashlib.sha256(image_data).hexdigest()

                filename = f"{image_hash}{os.path.splitext(image.filename)[1]}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)

                with open(filepath, 'wb') as f:
                    f.write(image_data)

                image = image_hash
            else:
                flash("Invalid file format. Only JPEG and PNG images are allowed!", "danger")
                return render_template('register.html', title="Register")

            # Hash da senha para segurança
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Usar a conexão com o banco de dados
            cursor = current_app.mysql.connection.cursor()

            try:
                cursor.execute('SELECT * FROM accounts WHERE username = %s OR email = %s', (username, email))
                existing_user = cursor.fetchone()

                if existing_user:
                    flash("Username or email already exists!", "danger")
                else:
                    cursor.execute('INSERT INTO accounts (username, password, email, image) VALUES (%s, %s, %s, %s)', (username, hashed_password, email, image))
                    current_app.mysql.connection.commit()
                    flash("Registration successful! You can now log in.", "success")
                    return redirect(url_for('app.login'))

            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")

            finally:
                cursor.close()
        else:
            flash("All fields are required!", "danger")

    return render_template('register.html', title="Register")
