from flask import Blueprint, request, jsonify
from services.usuario_service import UsuarioService

usuario_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

@usuario_bp.route("/login", methods=["POST"])
def login_usuario():
    data = request.json

    # Verificar se os campos obrigatórios foram enviados
    if not data or not data.get("Nome") or not data.get("Senha"):
        return jsonify({"success": False, "message": "Nome ou Senha não fornecidos"}), 400

    nome = data["Nome"]
    senha = data["Senha"]

    # Buscar usuário no banco de dados
    usuario = UsuarioService.get_by_nome(nome)
    if usuario and usuario["Senha"] == senha:
        return jsonify({
            "success": True,
            "message": "Login bem-sucedido",
            "data": {
                "User_ID": usuario["User_ID"],
                "Nome": usuario["Nome"]
            }
        }), 200
    else:
        return jsonify({"success": False, "message": "Usuário ou senha inválidos"}), 401

@usuario_bp.route("/registro", methods=["POST"])
def registro_usuario():
    data = request.json

    # Verificar se os campos obrigatórios foram enviados
    if not data or not data.get("Nome") or not data.get("Senha") or not data.get("Email"):
        return jsonify({"success": False, "message": "Nome, Email ou Senha não fornecidos"}), 400

    nome = data["Nome"]
    email = data["Email"]
    senha = data["Senha"]

    # Verificar se o email já está registrado
    usuario_existente = UsuarioService.get_by_email(email)
    if usuario_existente:
        return jsonify({"success": False, "message": "Email já registrado"}), 400

    # Criar novo usuário no banco de dados
    try:
        novo_usuario = UsuarioService.create({
            "Nome": nome,
            "Email": email,
            "Senha": senha,
            "Pontuacao": 0,
            "Nivel": 1,
            "Vitorias": 0,
            "Derrotas": 0,
            "Empates": 0
        })

        return jsonify({
            "success": True,
            "message": "Usuário registrado com sucesso",
            "data": {
                "User_ID": novo_usuario["User_ID"],
                "Nome": novo_usuario["Nome"],
                "Email": novo_usuario["Email"]
            }
        }), 201

    except Exception as e:
        print(f"Erro ao registrar usuário: {e}")
        return jsonify({"success": False, "message": "Erro ao registrar usuário"}), 500


@usuario_bp.route("/<int:user_id>", methods=["GET"])
def get_usuario(user_id):
    usuario = UsuarioService.get_by_id(user_id)
    return jsonify(usuario) if usuario else ("Usuário não encontrado", 404)

@usuario_bp.route("/", methods=["POST"])
def create_usuario():
    data = request.json
    usuario = UsuarioService.create(data)
    return jsonify(usuario), 201

@usuario_bp.route("/<int:user_id>", methods=["PUT"])
def update_usuario(user_id):
    data = request.json
    usuario = UsuarioService.update(user_id, data)
    return jsonify(usuario) if usuario else ("Usuário não encontrado", 404)

@usuario_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_usuario(user_id):
    success = UsuarioService.delete(user_id)
    return ("", 204) if success else ("Usuário não encontrado", 404)
