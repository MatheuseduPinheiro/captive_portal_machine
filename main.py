import os
from flask import Flask
from controllers.route import app as app_blueprint
from flask_mysqldb import MySQL

UPLOAD_FOLDER = 'uploads'  # Definido corretamente aqui

def create_app():
    app = Flask(__name__)

    app.secret_key = '1a2b3c4d5e6d7g8h9i10'
    
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'captiveportal_machine'
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    mysql = MySQL(app)
    app.config['mysql'] = mysql

    app.register_blueprint(app_blueprint, url_prefix='/')

    # Verificar se o diretório de uploads existe, e se não, criar
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='192.168.15.11', port=5000, debug=True)
