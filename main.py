from flask import Flask
from controllers.route import app as app_blueprint
from flask_mysqldb import MySQL

def create_app():
    app = Flask(__name__)

    app.secret_key = '1a2b3c4d5e6d7g8h9i10'
    
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'captiveportal_machine'

    mysql = MySQL(app)
    app.config['mysql'] = mysql

    app.register_blueprint(app_blueprint, url_prefix='/')  # Registrando o blueprint com o prefixo correto

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='192.168.15.11', port=5000, debug=True)
