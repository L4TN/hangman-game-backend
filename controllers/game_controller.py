from flask import Blueprint, request, jsonify
from database import db
from models.fila_model import TbFila
from models.partida_model import TbPartidaGame
from sqlalchemy import and_, or_

# Criação do Blueprint para a controller `game`
game_bp = Blueprint("game", __name__, url_prefix="/game")

@game_bp.route("/start", methods=["POST"])
def start_game():
    data = request.json

    # Validação de campos obrigatórios
    tema_id = data.get("Tema_ID")
    nome = data.get("Nome")
    user_id = data.get("User_ID")

    if tema_id is None or not nome or not user_id:
        return jsonify({"success": False, "message": "User_ID, Tema_ID e Nome são obrigatórios"}), 400

    # Verifica se o jogador já está em uma partida para o mesmo Tema_ID
    partida_existente = TbPartidaGame.query.filter(
        and_(
            TbPartidaGame.Tema_Selecionado == tema_id,
            or_(
                TbPartidaGame.Jogador_1_Usuario_ID == user_id,
                TbPartidaGame.Jogador_2_Usuario_ID == user_id
            ),
            TbPartidaGame.Sessao_Status == "in_progress"
        )
    ).first()

    if partida_existente:
        return jsonify({
            "success": True,
            "message": "O jogador já está em uma partida em andamento neste tema, retomando partida..."
        }), 200

    # Verifica se o Nome já está na fila
    jogador_na_fila = TbFila.query.filter(
        and_(
            TbFila.Nome == nome,
            TbFila.Tema_ID == tema_id,
            TbFila.Status == "Aguardando"
        )
    ).first()

    if jogador_na_fila:
        return jsonify({
            "success": False,
            "message": "Este jogador já está na fila para este tema."
        }), 400

    # Adiciona o jogador à fila
    nova_fila = TbFila(User_ID=user_id, Nome=nome, Status="Aguardando", Tema_ID=tema_id)
    db.session.add(nova_fila)
    db.session.commit()

    # Busca jogadores disponíveis na fila para o mesmo Tema_ID
    jogadores_disponiveis = TbFila.query.filter(
        and_(
            TbFila.Tema_ID == tema_id,
            TbFila.Status == "Aguardando",
            TbFila.User_ID != user_id  # Ignora o próprio jogador
        )
    ).all()

    # Se encontrar outro jogador, cria uma nova partida
    if jogadores_disponiveis:
        outro_jogador = jogadores_disponiveis[0]

        # Atualiza status dos jogadores na fila para "Jogando"
        outro_jogador.Status = "Jogando"
        nova_fila.Status = "Jogando"

        # Cria uma nova partida
        nova_partida = TbPartidaGame(
            Jogador_1_Usuario_ID=nova_fila.User_ID,
            Jogador_1_Vidas=5,  # Número inicial de vidas
            Jogador_2_Usuario_ID=outro_jogador.User_ID,
            Jogador_2_Vidas=5,  # Número inicial de vidas
            Tema_Selecionado=tema_id,
            Data_Inicio=db.func.now(),
            Data_Atual=db.func.now(),
            Sessao_Status="in_progress"
        )
        db.session.add(nova_partida)

        # Limpa todos os registros de TbFila
        db.session.query(TbFila).delete()
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Partida criada com sucesso",
            "partida": {
                "Partida_ID": nova_partida.Partida_ID,
                "Jogador_1_Usuario_ID": nova_partida.Jogador_1_Usuario_ID,
                "Jogador_2_Usuario_ID": nova_partida.Jogador_2_Usuario_ID,
                "Tema_Selecionado": nova_partida.Tema_Selecionado,
                "Sessao_Status": nova_partida.Sessao_Status
            }
        }), 201

    return jsonify({
        "success": True,
        "message": "Jogador adicionado à fila. Aguardando oponente...",
        "data": {
            "ID": nova_fila.ID,
            "User_ID": nova_fila.User_ID,
            "Tema_ID": nova_fila.Tema_ID,
            "Nome": nova_fila.Nome,
            "Status": nova_fila.Status
        }
    }), 201
    data = request.json

    # Validação de campos obrigatórios
    tema_id = data.get("Tema_ID")
    nome = data.get("Nome")
    user_id = data.get("User_ID")  # Recebe User_ID do frontend ou autenticação

    if tema_id is None or not nome or not user_id:
        return jsonify({"success": False, "message": "User_ID, Tema_ID e Nome são obrigatórios"}), 400

    # Verifica se o jogador já está em uma partida para o mesmo Tema_ID
    partida_existente = TbPartidaGame.query.filter(
        and_(
            TbPartidaGame.Tema_Selecionado == tema_id,
            or_(
                TbPartidaGame.Jogador_1_Usuario_ID == user_id,
                TbPartidaGame.Jogador_2_Usuario_ID == user_id
            ),
            TbPartidaGame.Sessao_Status == "in_progress"
        )
    ).first()

    if partida_existente:
        return jsonify({
            "success": True,
            "message": "O jogador já está em uma partida em andamento neste tema, retomando partida..."
        }), 200

    # Verifica se o jogador já está na fila para o mesmo Tema_ID
    jogador_na_fila = TbFila.query.filter(
        and_(
            TbFila.Nome == nome,
            TbFila.Tema_ID == tema_id,
            TbFila.Status == "Aguardando"
        )
    ).first()

    if jogador_na_fila:
        return jsonify({
            "success": False,
            "message": "Este jogador já está na fila para este tema."
        }), 400

    # Adiciona o jogador à fila
    nova_fila = TbFila(User_ID=user_id, Nome=nome, Status="Aguardando", Tema_ID=tema_id)
    db.session.add(nova_fila)
    db.session.commit()

    # Busca jogadores disponíveis na fila para o mesmo Tema_ID
    jogadores_disponiveis = TbFila.query.filter(
        and_(
            TbFila.Tema_ID == tema_id,
            TbFila.Status == "Aguardando",
            TbFila.User_ID != user_id  # Ignora o próprio jogador
        )
    ).all()

    # Se encontrar outro jogador, cria uma nova partida
    if jogadores_disponiveis:
        outro_jogador = jogadores_disponiveis[0]

        # Atualiza status dos jogadores na fila para "Jogando"
        outro_jogador.Status = "Jogando"
        nova_fila.Status = "Jogando"

        # Cria uma nova partida
        nova_partida = TbPartidaGame(
            Jogador_1_Usuario_ID=nova_fila.User_ID,
            Jogador_1_Vidas=5,  # Número inicial de vidas
            Jogador_2_Usuario_ID=outro_jogador.User_ID,
            Jogador_2_Vidas=5,  # Número inicial de vidas
            Tema_Selecionado=tema_id,
            Data_Inicio=db.func.now(),
            Data_Atual=db.func.now(),
            Sessao_Status="in_progress"
        )
        db.session.add(nova_partida)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Partida criada com sucesso",
            "partida": {
                "Partida_ID": nova_partida.Partida_ID,
                "Jogador_1_Usuario_ID": nova_partida.Jogador_1_Usuario_ID,
                "Jogador_2_Usuario_ID": nova_partida.Jogador_2_Usuario_ID,
                "Tema_Selecionado": nova_partida.Tema_Selecionado,
                "Sessao_Status": nova_partida.Sessao_Status
            }
        }), 201

    return jsonify({
        "success": True,
        "message": "Jogador adicionado à fila. Aguardando oponente...",
        "data": {
            "ID": nova_fila.ID,
            "User_ID": nova_fila.User_ID,
            "Tema_ID": nova_fila.Tema_ID,
            "Nome": nova_fila.Nome,
            "Status": nova_fila.Status
        }
    }), 201
