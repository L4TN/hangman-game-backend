import os
import threading
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
from blueprints import register_blueprints
from flask_migrate import Migrate
from engine import start_server

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Habilitar CORS apenas para a origem confiável
    
    CORS(app, resources={
        r"/*": {
            "origins": [
                "https://hangman-game-frontend.onrender.com",  # Frontend na Render
                "http://127.0.0.1:3000",  # Endereço local padrão para React ou outro frontend local
                "http://localhost:3000",   # Alternativa para localhost
                "http://127.0.0.1:5500",   # Adicionado endereço local (porta 5500)
            ]
        }
    })

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
