from database import db

class TbFila(db.Model):
    __tablename__ = "Tb_Fila"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    User_ID = db.Column(db.String(36), nullable=True)  # UNIQUEIDENTIFIER no banco, opcional
    Status = db.Column(db.String(50), nullable=True, default="Aguardando")
    Tema_ID = db.Column(db.Integer, nullable=True)  # Campo nullable
    Nome = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "ID": self.ID,
            "User_ID": self.User_ID,
            "Status": self.Status,
            "Tema_ID": self.Tema_ID,
            "Nome": self.Nome,
        }
