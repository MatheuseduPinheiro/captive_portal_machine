from flask import current_app as app

class Conexao:
    def __init__(self):
        self.cursor = app.config['mysql'].connection.cursor(MySQLdb.cursors.DictCursor)
    
    def close(self):
        self.cursor.close()
    
    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        app.config['mysql'].connection.commit()
