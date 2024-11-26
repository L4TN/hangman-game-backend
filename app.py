import os
import threading
import asyncio
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
from blueprints import register_blueprints
from flask_migrate import Migrate
from engine import start_server

def install_odbc_driver():
    """Instala o ODBC Driver 18 para SQL Server."""
    try:
        print("Atualizando pacotes e instalando dependências...")
        # Atualizar pacotes e instalar curl e gnupg
        subprocess.run("apt-get update && apt-get install -y curl gnupg", shell=True, check=True)

        print("Adicionando chave e repositório do Microsoft ODBC Driver...")
        # Adicionar a chave pública e o repositório da Microsoft
        subprocess.run(
            "curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -",
            shell=True, check=True
        )
        subprocess.run(
            "curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list",
            shell=True, check=True
        )

        print("Instalando ODBC Driver 18 e dependências...")
        # Instalar o ODBC Driver 18 e dependências
        subprocess.run(
            "apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev",
            shell=True, check=True
        )
        print("Instalação do ODBC Driver concluída com sucesso!")

    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar o ODBC Driver: {e}")
        raise

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Habilitar CORS apenas para a origem confiável
    CORS(app, resources={
        r"/*": {"origins": ["https://hangman-game-frontend.onrender.com"]}
    }, supports_credentials=True)

    # Middleware para validar Content-Type
    @app.before_request
    def validate_json():
        if request.method in ["POST", "PUT"] and not request.is_json:
            return jsonify({"success": False, "message": "Content-Type deve ser application/json"}), 415

    # Inicializar banco de dados e migrações
    db.init_app(app)
    Migrate(app, db)

    # Registrar Blueprints
    register_blueprints(app)

    return app

def run_engine_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())

# Instalar o driver ODBC antes de iniciar o servidor
install_odbc_driver()

# Criação da aplicação global
app = create_app()

# Iniciar o WebSocket em uma thread separada
if threading.active_count() == 1:
    engine_thread = threading.Thread(
        target=run_engine_in_thread, daemon=True)
    engine_thread.start()

# Configuração para rodar no OnRender
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
