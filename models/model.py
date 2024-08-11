import pymysql 
from flask import current_app

class Conexao:
    def __init__(self, mysql_connection):
        self.connection = mysql_connection
        self.cursor = self.connection.cursor(dictionary=True)

    def close(self):
        # Fechar o cursor e a conexão se existirem
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()

    def fetchall(self, query, params=()):
        if not self.connection or not self.cursor:
            raise ConnectionError("No active connection.")
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"Error fetching data: {str(e)}")
            self.reconnect()

    def execute(self, query, params=()):
        if not self.connection or not self.cursor:
            raise ConnectionError("No active connection.")
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except pymysql.MySQLError as e:
            print(f"Error executing query: {str(e)}")
            self.reconnect()

    def reconnect(self):
        # Fechar o cursor e a conexão existentes
        self.close()
        # Recriar a conexão com a configuração atual
        self.connection = current_app.get_db_connection()
        self.cursor = self.connection.cursor(dictionary=True)
