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

    # Habilitar CORS para múltiplas origens
    CORS(app, resources={
        r"/*": {"origins": [
            "http://localhost:3000",  # Origem local
            "http://127.0.0.1:5500",  # Origem alternativa local
            "https://lively-beach-0a427280f.5.azurestaticapps.net"  # Origem de produção
        ]}
    }, supports_credentials=True)

    # Adiciona cabeçalhos extras para CORS (opcional)
    @app.after_request
    def add_cors_headers(response):
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:5500",
            "https://lively-beach-0a427280f.5.azurestaticapps.net"
        ]
        if request.origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = request.origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "3600"  # Cache para preflight
        return response

    # Middleware para validar Content-Type
    @app.before_request
    def validate_json():
        """Valida se o Content-Type é application/json para métodos POST e PUT."""
        if request.method in ["POST", "PUT"] and not request.is_json:
            return jsonify({"success": False, "message": "Content-Type deve ser application/json"}), 415

    # Inicializar o banco de dados e migrações
    db.init_app(app)
    Migrate(app, db)

    # Registrar Blueprints
    register_blueprints(app)

    return app

def run_flask():
    """Função para rodar o Flask."""
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)  # Configuração padrão para produção

def run_engine_in_thread():
    """Executa o WebSocket em uma thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server())

if __name__ == "__main__":
    # Evita iniciar o servidor WebSocket várias vezes
    if threading.active_count() == 1:  # Certifica que nenhuma outra thread foi iniciada
        engine_thread = threading.Thread(
            target=run_engine_in_thread, daemon=True)
        engine_thread.start()

    # Executa o Flask no processo principal
    run_flask()