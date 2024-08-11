import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_mysqldb import MySQL
import os

UPLOAD_FOLDER = 'uploads'

def create_app():
    app = Flask(__name__)

    # Configurações da aplicação
    app.secret_key = '1a2b3c4d5e6d7g8h9i10'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'captiveportal_machine'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Inicializa o MySQL
    mysql = MySQL(app)
    app.mysql = mysql

    # Importa e registra o blueprint
    from controllers.route import app_blueprint
    app.register_blueprint(app_blueprint, url_prefix='/')

    # Verifica e cria o diretório de uploads, se não existir
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='192.168.15.11', port=5000, debug=True)

