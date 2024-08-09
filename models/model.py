import MySQLdb
from flask import current_app as app

class Conexao:
    def __init__(self):
        try:
            # Inicializa a conexão com o banco de dados
            self.connection = app.config['mysql'].connection
            self.cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
        except MySQLdb.OperationalError as e:
            print(f"Error initializing connection: {str(e)}")
            self.connection = None
            self.cursor = None
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def fetchall(self, query, params=()):
        if not self.connection or not self.cursor:
            raise ConnectionError("No active connection.")
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except MySQLdb.OperationalError as e:
            print(f"Error fetching data: {str(e)}")
            self.reconnect()
    
    def execute(self, query, params=()):
        if not self.connection or not self.cursor:
            raise ConnectionError("No active connection.")
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except MySQLdb.OperationalError as e:
            print(f"Error executing query: {str(e)}")
            self.reconnect()
    
    def reconnect(self):
        # Tenta reconectar ao banco de dados
        self.close()
        self.__init__()
