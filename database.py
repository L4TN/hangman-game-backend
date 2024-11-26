from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from tenacity import retry, stop_after_attempt, wait_fixed

db = SQLAlchemy()

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))  # Tenta 5 vezes, esperando 2 segundos entre tentativas
def connect_db(app):
    try:
        db.init_app(app)
        with app.app_context():
            # Testa a conexão com o banco
            db.engine.execute("SELECT 1")
        print("Conexão com o banco de dados estabelecida com sucesso.")
    except OperationalError as e:
        print("Erro ao conectar ao banco de dados. Tentando novamente...")
        raise e  # Levanta a exceção para ativar o retry
