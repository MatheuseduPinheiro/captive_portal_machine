from flask import Blueprint, current_app, flash, render_template, request, redirect, session, url_for
import re
import hashlib
import os
import time

import joblib
import numpy as np
from PIL import Image

app_blueprint = Blueprint('app', __name__)

UPLOAD_FOLDER = 'uploads'
UPLOAD_TEMPORARY_FOLDER = 'uploads_temporary_folder'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Carregar o modelo de reconhecimento facial
model = joblib.load('modelo_reconhecimento_facial.pkl')

def allowed_file(filename):
    """Verifica se o formato do arquivo é permitido."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    """Função para preprocessar a imagem para o modelo."""
    with Image.open(image_path) as img:
        img = img.convert('L')  # Converte para grayscale
        img = img.resize((47, 62))  # Redimensiona para o tamanho usado no treinamento
        img_array = np.array(img, dtype='float32').flatten()  # Achata a imagem
        img_array = img_array / 255.0  # Normaliza
    return img_array

def bubble_sort_images(image_list, image_data):
    """Algoritmo Bubble Sort para ordenar as imagens por similaridade."""
    n = len(image_list)
    for i in range(n):
        for j in range(0, n-i-1):
            img_data1 = preprocess_image(image_list[j])
            img_data2 = preprocess_image(image_list[j+1])
            # Compare similaridade
            similarity1 = np.linalg.norm(img_data1 - image_data)
            similarity2 = np.linalg.norm(img_data2 - image_data)
            if similarity1 > similarity2:
                image_list[j], image_list[j+1] = image_list[j+1], image_list[j]
    return image_list

def clean_temporary_folder():
    """Remove imagens antigas da pasta temporária após 10 minutos."""
    current_time = time.time()
    for filename in os.listdir(UPLOAD_TEMPORARY_FOLDER):
        file_path = os.path.join(UPLOAD_TEMPORARY_FOLDER, filename)
        file_creation_time = os.path.getmtime(file_path)
        if (current_time - file_creation_time) > 600:  # 600 segundos = 10 minutos
            os.remove(file_path)

@app_blueprint.route('/')
@app_blueprint.route('/portalogin/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        image = request.files.get('image')

        if image:
            # Verificar se a imagem tem um formato permitido
            if not allowed_file(image.filename):
                flash("Invalid file format. Only JPEG and PNG images are allowed!", "danger")
                return render_template('login.html', title="Login")

            # Salvar a imagem temporariamente para processamento
            if not os.path.exists(UPLOAD_TEMPORARY_FOLDER):
                os.makedirs(UPLOAD_TEMPORARY_FOLDER)

            # Calcular o hash da imagem
            image_data = image.read()
            image_hash = hashlib.sha256(image_data).hexdigest()

            # Criar o caminho completo do arquivo com o hash
            temp_image_filename = f"{image_hash}{os.path.splitext(image.filename)[1]}"
            temp_image_path = os.path.join(UPLOAD_TEMPORARY_FOLDER, temp_image_filename)

            # Salvar a imagem com o nome baseado no hash
            with open(temp_image_path, 'wb') as f:
                f.write(image_data)

            # Processar a imagem enviada pelo usuário
            user_image_data = preprocess_image(temp_image_path)

            # Listar imagens da pasta 'uploads'
            images = [os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
            if not images:
                flash("No registered images found for comparison.", "warning")
                return render_template('login.html', title="Login")

            # Ordenar imagens usando Bubble Sort
            images = bubble_sort_images(images, user_image_data)

            # Comparar a imagem com as imagens mais semelhantes
            match_found = False
            for file_path in images:
                saved_image_data = preprocess_image(file_path)

                # Prever usando o modelo
                prediction = model.predict([saved_image_data])
                user_prediction = model.predict([user_image_data])
                if prediction == user_prediction:
                    match_found = True
                    break

            # Remover a imagem temporária
            os.remove(temp_image_path)

            if match_found:
                # Se a imagem corresponde, permita o login
                session['loggedin'] = True
                return redirect("https://google.com")  # Redirecionar para a página desejada
            else:
                flash("Face não reconhecida, tente novamente.", "danger")
        else:
            flash("Por favor, insira uma imagem!", "warning")

    # Limpar imagens antigas da pasta temporária
    clean_temporary_folder()

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
                image_data = image.read()  # Ler os dados da imagem
                image_hash = hashlib.sha256(image_data).hexdigest()

                # Salvar a imagem na pasta 'uploads'
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
