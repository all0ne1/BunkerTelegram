class Lobby:
    def __init__(self):
        self.players = []
        self.game_id = 0
    def add_player(self, player):
        self.players.append(player)

    def get_game_id(self):
        return self.game_id