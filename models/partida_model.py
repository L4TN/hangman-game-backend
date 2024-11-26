from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from database import db

class TbPartidaGame(db.Model):
    __tablename__ = "Tb_Partida_Game"

    Partida_ID = Column(Integer, primary_key=True, autoincrement=True)  # Identificador único da partida
    Jogador_1_Usuario_ID = Column(String(100), nullable=False)  # Nome do primeiro jogador
    Jogador_1_Vidas = Column(Integer, nullable=False)  # Vidas do primeiro jogador
    Jogador_2_Usuario_ID = Column(String(100), nullable=False)  # Nome do segundo jogador
    Jogador_2_Vidas = Column(Integer, nullable=False)  # Vidas do segundo jogador
    Tema_Selecionado = Column(String(100), nullable=False)  # Tema da partida
    Data_Inicio = Column(DateTime, nullable=False)  # Data e hora de início da partida
    Data_Atual = Column(DateTime, nullable=False)  # Data e hora do estado atual
    Palavra_Parcial = Column(String(255), nullable=True)  # Palavra descoberta parcialmente
    Jogador_Atual = Column(String(100), nullable=False)  # Nome do jogador atual
    Letra_Selecionada = Column(String(1), nullable=True)  # Letra selecionada na jogada
    Letra_Correta = Column(Boolean, nullable=False, default=False)  # Indicador se a letra foi acertada
    Proximo_Jogador = Column(String(100), nullable=False)  # Nome do próximo jogador
    Letras_Corretas = Column(Text, nullable=True)  # Lista de letras corretas
    Letras_Usadas = Column(Text, nullable=True)  # Lista de letras já usadas
    Efeitos = Column(Text, nullable=True)  # Efeitos da partida (JSON de efeitos)
    Palavra_Secreta = Column(String(255), nullable=True)  # Palavra secreta
    Letras_Anteriores = Column(Text, nullable=True)  # Letras anteriores jogadas
    Sessao_Status = Column(String(50), nullable=False)  # Status da sessão (Ex: 'finished', 'in_progress')

    def to_dict(self):
        return {
            "Partida_ID": self.Partida_ID,
            "Jogador_1_Usuario_ID": self.Jogador_1_Usuario_ID,
            "Jogador_1_Vidas": self.Jogador_1_Vidas,
            "Jogador_2_Usuario_ID": self.Jogador_2_Usuario_ID,
            "Jogador_2_Vidas": self.Jogador_2_Vidas,
            "Tema_Selecionado": self.Tema_Selecionado,
            "Data_Inicio": self.Data_Inicio,
            "Data_Atual": self.Data_Atual,
            "Palavra_Parcial": self.Palavra_Parcial,
            "Jogador_Atual": self.Jogador_Atual,
            "Letra_Selecionada": self.Letra_Selecionada,
            "Letra_Correta": self.Letra_Correta,
            "Proximo_Jogador": self.Proximo_Jogador,
            "Letras_Corretas": self.Letras_Corretas,
            "Letras_Usadas": self.Letras_Usadas,
            "Efeitos": self.Efeitos,
            "Palavra_Secreta": self.Palavra_Secreta,
            "Letras_Anteriores": self.Letras_Anteriores,
            "Sessao_Status": self.Sessao_Status
        }
