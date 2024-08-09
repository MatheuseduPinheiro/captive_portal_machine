from flask import Flask
from controllers.route import app as routes_blueprint
from flask_mysqldb import MySQL

def create_app():
    app = Flask(__name__)

    # Configurações do MySQL
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''  # Substitua pela sua senha do banco de dados.
    app.config['MYSQL_DB'] = 'loginapp'

    mysql = MySQL(app)
    app.config['mysql'] = mysql

    # Registra os blueprints
    app.register_blueprint(routes_blueprint)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
