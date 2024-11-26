from models.usuario_model import TbUsuario
from database import db
from datetime import datetime

class UsuarioService:
    @staticmethod
    def get_by_nome(nome):
        usuario = TbUsuario.query.filter_by(Nome=nome).first()
        if usuario:
            return {
                "User_ID": usuario.User_ID,
                "Nome": usuario.Nome,
                "Senha": usuario.Senha
            }
        return None
    
    @staticmethod
    def get_all():
        usuarios = TbUsuario.query.all()
        return [u.to_dict() for u in usuarios]

    @staticmethod
    def get_by_id(user_id):
        usuario = TbUsuario.query.get(user_id)
        return usuario.to_dict() if usuario else None

    @staticmethod
    def create(data):
        usuario = TbUsuario(
            Criado=datetime.utcnow(),
            Ultimo_Login=None,
            Pontuacao=data.get("Pontuacao", 0),
            Nivel=data.get("Nivel", 0),
            Vitorias=data.get("Vitorias", 0),
            Derrotas=data.get("Derrotas", 0),
            Empates=data.get("Empates", 0),
            Nome=data["Nome"],
            Email=data["Email"],
            Senha=data["Senha"],
            Avatar=data.get("Avatar"),
        )
        db.session.add(usuario)
        db.session.commit()
        return usuario.to_dict()

    @staticmethod
    def update(user_id, data):
        usuario = TbUsuario.query.get(user_id)
        if not usuario:
            return None
        usuario.Pontuacao = data.get("Pontuacao", usuario.Pontuacao)
        usuario.Nivel = data.get("Nivel", usuario.Nivel)
        usuario.Vitorias = data.get("Vitorias", usuario.Vitorias)
        usuario.Derrotas = data.get("Derrotas", usuario.Derrotas)
        usuario.Empates = data.get("Empates", usuario.Empates)
        usuario.Nome = data.get("Nome", usuario.Nome)
        usuario.Email = data.get("Email", usuario.Email)
        usuario.Senha = data.get("Senha", usuario.Senha)
        usuario.Avatar = data.get("Avatar", usuario.Avatar)
        usuario.Ultimo_Login = data.get("Ultimo_Login", usuario.Ultimo_Login)
        db.session.commit()
        return usuario.to_dict()

    @staticmethod
    def delete(user_id):
        usuario = TbUsuario.query.get(user_id)
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_by_email(email):
        usuario = TbUsuario.query.filter_by(Email=email).first()
        return usuario.to_dict() if usuario else None
