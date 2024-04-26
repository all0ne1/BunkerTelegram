class Lobby:
    def __init__(self):
        self.players = []
        self.game_id = 0
        self.host = 0
        self.round = 0
        self.state = None
    def add_player(self, player):
        self.players.append(player)

    def make_host(self, host):
        self.host = host

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state
    def get_game_id(self):
        return self.game_id