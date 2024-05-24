from collections import deque
import random

from configs.player import Player
from db_connection.connection import get_from_db


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
        self.players_for_game_over = 0
        self.bunker_stats = self.fetch_and_shuffle_bunker_stat()
        self.cataclysm = self.get_cataclysm_from_db()
        self.bunker_stat_revealed = False
        self.revote_done = False

    def get_one_bunker_stat(self):
        return self.bunker_stats.pop()[0]

    def get_cataclysm(self):
        return self.cataclysm

    @staticmethod
    def get_cataclysm_from_db():
        count = get_from_db("SELECT COUNT(*) FROM cataclysm_cards")[0] - 1
        query = f"SELECT cataclysm FROM cataclysm_cards WHERE ID = {random.randint(0, count)}"
        return get_from_db(query)[0]

    @staticmethod
    def fetch_and_shuffle_bunker_stat() -> deque:
        query = "SELECT bunker FROM bunker_cards"
        bunker_stat_list = get_from_db(query, fetch_all=True)
        random.shuffle(bunker_stat_list)
        limited_bunker_stat_list = bunker_stat_list[:5]
        bunker_stat_queue = deque(limited_bunker_stat_list)
        return bunker_stat_queue

    def print_survivors(self):
        from configs.config import id_to_nick
        survivors = ""
        for player_id in self.players:
            survivors += " " + (id_to_nick.get(player_id))
        return survivors

    def set_players_for_game_over(self, num):
        self.players_for_game_over = num

    def reset_votes_for_kick(self):
        self.votes_for_players = {}

    def add_player_stats(self, player_id):
        self.player_stats[player_id] = Player(game_id=self.game_id)

    def reset_speaker_index(self):
        self.cur_speaker_index = 0

    def get_player_stats(self, key) -> Player:
        return self.player_stats.get(key)

    def get_speaker_index(self):
        return self.cur_speaker_index

    def next_speaker_index(self):
        self.cur_speaker_index += 1

    def set_speaker(self, speaker_id):
        self.speaker = speaker_id

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

    def set_game_id(self, game_id):
        self.game_id = game_id

    def get_game_id(self, game_id):
        self.game_id = game_id

    def next_round(self):
        self.bunker_stat_revealed = False
        self.round += 1
