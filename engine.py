import asyncio
import websockets
import json
import random
from datetime import datetime, timedelta
import os

# Cache global para armazenar o estado das sessões
session_cache = {}

# Lista de jogadores esperando para entrar no jogo
waiting_players = []

# Dicionário de temas e palavras associadas
themes = {
    0: ["xerife", "bangue", "banco"],
    1: ["cadeia", "prisioneiro", "cowboy"],
    2: ["cavalo", "vaca", "poeira"],
    3: ["deserto", "oeste"]
}


class GameSession:
    def __init__(self, player1, player2, session_id):
        self.players = [player1, player2]
        self.session_id = session_id
        self.current_player_index = 0  # 0 ou 1
        self.lives = [5, 5]  # Vidas de cada jogador
        self.used_letters = []  # Letras já tentadas
        self.start_time = datetime.now()
        self.time_limit = timedelta(seconds=180)  # 3 minutos
        self.game_over = False

        # Seleciona um tema e uma palavra aleatória
        self.theme = random.choice(list(themes.keys()))
        self.word = random.choice(themes[self.theme])
        self.partial_word = ["_" for _ in self.word]

        # Poderes de cada jogador
        self.powers = {
            0: {"hint": 1, "heal": 1, "attack": 1, "confuse": 1},
            1: {"hint": 1, "heal": 1, "attack": 1, "confuse": 1}
        }

        # Estado das conexões dos jogadores
        self.connected = [True, True]

    def save_to_cache(self):
        """Salva o estado atual no cache global."""
        session_cache[self.session_id] = {
            "current_player_index": self.current_player_index,
            "lives": self.lives,
            "used_letters": self.used_letters,
            "start_time": self.start_time.isoformat(),
            "time_limit": self.time_limit.total_seconds(),
            "game_over": self.game_over,
            "theme": self.theme,
            "word": self.word,
            "partial_word": self.partial_word,
            "powers": self.powers,
        }

    def load_from_cache(self):
        """Restaura o estado do cache para a sessão atual."""
        state = session_cache.get(self.session_id)
        if state:
            self.current_player_index = state["current_player_index"]
            self.lives = state["lives"]
            self.used_letters = state["used_letters"]
            self.start_time = datetime.fromisoformat(state["start_time"])
            self.time_limit = timedelta(seconds=state["time_limit"])
            self.game_over = state["game_over"]
            self.theme = state["theme"]
            self.word = state["word"]
            self.partial_word = state["partial_word"]
            self.powers = state["powers"]

    async def start(self):
        try:
            # Envia o estado inicial do jogo para ambos os jogadores
            self.save_to_cache()  # Salva o estado no cache
            await self.send_game_state()

            # Inicia o controle de tempo
            asyncio.create_task(self.check_time_limit())

            # Inicia a escuta dos jogadores
            await asyncio.gather(
                self.handle_player(self.players[0], 0),
                self.handle_player(self.players[1], 1)
            )
        except Exception as e:
            print(f"Exceção no método start: {e}")

    async def send_game_state(self):
        """Envia o estado atual do jogo para ambos os jogadores e salva no cache."""
        game_state = {
            "type": "game_state",
            "theme": self.theme,
            "word": " ".join(self.partial_word),  # Palavra parcialmente revelada
            "full_word": self.word,  # Palavra completa
            "used_letters": self.used_letters,
            "lives": self.lives,
            "current_player": self.current_player_index,
            "time_left": int((self.time_limit - (datetime.now() - self.start_time)).total_seconds()),
            "powers": self.powers
        }
        self.save_to_cache()  # Salva o estado no cache sempre que ele muda
        
        #salva self.players no cache
        
        for index, player in enumerate(self.players):
            if self.connected[index]:
                game_state["player_index"] = index
                try:
                    await player.send(json.dumps(game_state))
                except websockets.exceptions.ConnectionClosed:
                    self.connected[index] = False
                    print(f"Não foi possível enviar o estado do jogo para o jogador {index}, conexão fechada.")

    async def handle_player(self, websocket, player_index):
        try:
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "guess":
                    await self.handle_guess(player_index, data["letter"])
                elif data["type"] == "use_power":
                    await self.handle_power(player_index, data["power"])
                else:
                    # Mensagem desconhecida
                    pass
        except websockets.exceptions.ConnectionClosed:
            # Trata a desconexão do jogador
            self.connected[player_index] = False
            print(f"Jogador {player_index} desconectou.")
            self.save_to_cache()  # Salva o estado no cache
            if not self.game_over:
                await self.end_game(winner_index=1 - player_index, reason="Oponente desconectado")

    async def handle_guess(self, player_index, letter):
        if player_index != self.current_player_index:
            await self.send_error(player_index, "Não é o seu turno.")
            return

        if self.game_over:
            return

        letter = letter.lower()

        if letter in self.used_letters:
            await self.send_error(player_index, "Letra já utilizada.")
            return

        self.used_letters.append(letter)

        if letter in self.word:
            for idx, l in enumerate(self.word):
                if l == letter:
                    self.partial_word[idx] = letter

            if "_" not in self.partial_word:
                await self.end_game(winner_index=player_index, reason="Palavra adivinhada")
            else:
                # Alterna o turno
                self.current_player_index = 1 - self.current_player_index
                await self.send_game_state()
        else:
            self.lives[player_index] -= 1
            if self.lives[player_index] <= 0:
                await self.end_game(winner_index=1 - player_index, reason="Sem vidas.")
            else:
                # Alterna o turno
                self.current_player_index = 1 - self.current_player_index
                await self.send_game_state()

    async def handle_power(self, player_index, power):
        if self.powers[player_index][power] <= 0:
            await self.send_error(player_index, "Poder esgotado")
            return

        if power == "hint":
            available_letters = [l for l in set(self.word) if l not in self.used_letters]
            if available_letters:
                hint_letter = random.choice(available_letters)
                self.powers[player_index]["hint"] -= 1
                await self.handle_guess(player_index, hint_letter)
            else:
                await self.send_error(player_index, "Nenhuma letra para revelar")
        elif power == "heal":
            if self.lives[player_index] < 5:
                self.lives[player_index] += 1
                self.powers[player_index]["heal"] -= 1
                await self.send_game_state()
            else:
                await self.send_error(player_index, "Vidas já estão completas")
        elif power == "attack":
            opponent_index = 1 - player_index
            self.lives[opponent_index] -= 1
            self.powers[player_index]["attack"] -= 1
            if self.lives[opponent_index] <= 0:
                await self.end_game(winner_index=player_index, reason="Oponente sem vidas")
            else:
                await self.send_game_state()
        elif power == "confuse":
            opponent_index = 1 - player_index
            self.powers[player_index]["confuse"] -= 1
            if self.connected[opponent_index]:
                try:
                    await self.players[opponent_index].send(json.dumps({"type": "confuse"}))
                except websockets.exceptions.ConnectionClosed:
                    self.connected[opponent_index] = False
                    print(f"Não foi possível enviar 'confuse' para o jogador {opponent_index}, conexão fechada.")
            await self.send_game_state()
        else:
            await self.send_error(player_index, "Poder desconhecido")

    async def send_error(self, player_index, message):
        if self.connected[player_index]:
            try:
                await self.players[player_index].send(json.dumps({"type": "error", "message": message}))
            except websockets.exceptions.ConnectionClosed:
                self.connected[player_index] = False
                print(f"Não foi possível enviar erro para o jogador {player_index}, conexão fechada.")

    async def end_game(self, winner_index, reason):
        self.game_over = True
        game_result = {
            "type": "game_over",
            "winner": winner_index,
            "reason": reason,
            "full_word": self.word,  # Inclui a palavra completa
            "time_left": int((self.time_limit - (datetime.now() - self.start_time)).total_seconds())
        }
        for index, player in enumerate(self.players):
            if self.connected[index]:
                try:
                    await player.send(json.dumps(game_result))
                except websockets.exceptions.ConnectionClosed:
                    self.connected[index] = False
                    print(f"Não foi possível enviar resultado do jogo para o jogador {index}, conexão fechada.")

        # Fecha as conexões
        for index, player in enumerate(self.players):
            try:
                await player.close()
            except Exception as e:
                print(f"Erro ao fechar conexão com o jogador {index}: {e}")

    async def check_time_limit(self):
        while not self.game_over:
            await asyncio.sleep(1)
            if datetime.now() - self.start_time > self.time_limit:
                await self.end_game(winner_index=None, reason="Tempo esgotado")
                break

async def handle_connection(websocket):
    print(f"Novo jogador conectado: {websocket.remote_address}")
    try:
        greeting = await websocket.recv()
        player_data = json.loads(greeting)
        player_id = player_data["player_id"]
        session_id = player_data["session_id"]

        # Cria uma nova sessão ou adiciona o jogador à fila
        waiting_players.append((websocket, player_id, session_id))
        player_index = len(waiting_players) - 1  # 0 para o primeiro jogador, 1 para o segundo

        if len(waiting_players) >= 2:
            (player1, player1_id, session1_id), (player2, player2_id, session2_id) = waiting_players[:2]
            del waiting_players[:2]
            game_session = GameSession(player1, player2, session1_id)
            await game_session.start()
        else:
            # Envia a mensagem de espera incluindo o número do jogador
            await websocket.send(json.dumps({
                "type": "wait",
                "message": f"Aguardando outro jogador. Você é o jogador {player_index + 1}",
                "player_index": player_index
            }))
            await keep_connection_alive(websocket)
    except websockets.exceptions.ConnectionClosed:
        print(f"Jogador {websocket.remote_address} desconectou.")
    except Exception as e:
        print(f"Exceção na conexão com {websocket.remote_address}: {e}")

    print(f"Novo jogador conectado: {websocket.remote_address}")
    try:
        greeting = await websocket.recv()
        player_data = json.loads(greeting)
        player_id = player_data["player_id"]
        session_id = player_data["session_id"]

        # Cria uma nova sessão ou adiciona o jogador à fila
        waiting_players.append((websocket, player_id, session_id))
 
        if len(waiting_players) >= 2:
            (player1, player1_id, session1_id), (player2, player2_id, session2_id) = waiting_players[:2]
            del waiting_players[:2]
            game_session = GameSession(player1, player2, session1_id)
            await game_session.start()
        else:
            await websocket.send(json.dumps({"type": "wait", "message": "Aguardando outro jogador"}))
            await keep_connection_alive(websocket)
    except websockets.exceptions.ConnectionClosed:
        print(f"Jogador {websocket.remote_address} desconectou.")
    except Exception as e:
        print(f"Exceção na conexão com {websocket.remote_address}: {e}")


async def keep_connection_alive(websocket):
    try:
        while True:
            await asyncio.sleep(10)
    except websockets.exceptions.ConnectionClosed:
        print(f"Conexão com {websocket.remote_address} foi fechada.")
    except Exception as e:
        print(f"Exceção ao manter conexão com {websocket.remote_address}: {e}")

async def start_server():
    is_render = "RENDER" in os.environ

    # Configura o host e a porta com base no ambiente
    port = int(os.environ.get("PORT", 6789))  # Porta definida no Render ou 6789 localmente
    host = "0.0.0.0" if is_render else "localhost"

    async with websockets.serve(handle_connection, host):
        print(f"Servidor WebSocket rodando em ws://{host}:{port}")
        await asyncio.Future()  # Mantém o servidor rodando


if __name__ == "__main__":
    asyncio.run(start_server())
