from database import db
import uuid

class TbUsuario(db.Model):
    __tablename__ = "Tb_Usuario"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Criado = db.Column(db.DateTime, nullable=False)
    Ultimo_Login = db.Column(db.DateTime, nullable=True)
    Pontuacao = db.Column(db.Integer, nullable=True)
    Nivel = db.Column(db.Integer, nullable=True)
    Vitorias = db.Column(db.Integer, nullable=True)
    Derrotas = db.Column(db.Integer, nullable=True)
    Empates = db.Column(db.Integer, nullable=True)
    Nome = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(50), unique=True, nullable=False)
    Senha = db.Column(db.String(50), nullable=False)
    Avatar = db.Column(db.String(50), nullable=True)
    User_ID = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), nullable=False, unique=True)

    def to_dict(self):
        return {
            "ID": self.ID,
            "Criado": self.Criado,
            "Ultimo_Login": self.Ultimo_Login,
            "Pontuacao": self.Pontuacao,
            "Nivel": self.Nivel,
            "Vitorias": self.Vitorias,
            "Derrotas": self.Derrotas,
            "Empates": self.Empates,
            "Nome": self.Nome,
            "Email": self.Email,
            "Senha": self.Senha,
            "Avatar": self.Avatar,
            "User_ID": self.User_ID,
        }
