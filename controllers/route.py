import MySQLdb
from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from ..models import Conexao

app = Blueprint('app', __name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Usando a classe Conexao para obter dados
        conn = Conexao()
        conn.cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = conn.cursor.fetchone()
        conn.close()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))  # Redirecionar para uma rota definida no Flask, como 'home'
        else:
            flash("Incorrect username/password!", "danger")
    
    return render_template('auth/login.html', title="Login")
