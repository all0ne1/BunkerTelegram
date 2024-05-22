import queue

from configs.player import Player
class Lobby:
    def __init__(self):
        self.players = []
        self.game_id = 0
        self.host = 0
        self.round = 0
        self.speaker = 0
        self.cur_speaker_index = 0
        self.state = None
        self.player_stats = {}
        self.votes_for_players = {}


    def reset_votes_for_kick(self):
        self.votes_for_players = {}

    def add_player_stats(self,id):
        self.player_stats[id] = Player(game_id=self.game_id)

    def reset_speaker_index(self):
        self.cur_speaker_index = 0

    def get_player_stats(self,key) -> Player:
        return self.player_stats.get(key)

    def get_speaker_index(self):
        return self.cur_speaker_index

    def next_speaker_index(self):
        self.cur_speaker_index += 1

    def add_player(self, player):
        self.players.append(player)

    def make_host(self, host):
        self.host = host

    def get_host(self):
        return self.host

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def get_round(self):
        return self.round

    def get_speaker(self):
        return self.speaker

    def set_speaker(self, speaker):
        self.speaker = speaker

    def set_game_id(self,game_id):
        self.game_id = game_id

    def get_game_id(self,game_id):
        self.game_id = game_id
    def next_round(self):
        self.round += 1