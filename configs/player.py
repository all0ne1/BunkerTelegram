from db_connection.connection import get_from_db
from collections import deque
import random


class Player:
    def __init__(self, game_id):
        self.game_id = game_id
        self.stat_names = {"profession", "health", "hobby", "items", "fact"}
        self.professions_queue = self.fetch_and_shuffle_stat("profession")
        self.health_queue = self.fetch_and_shuffle_stat("health")
        self.hobby_queue = self.fetch_and_shuffle_stat("hobby")
        self.items_queue = self.fetch_and_shuffle_stat("items")
        self.fact_queue = self.fetch_and_shuffle_stat("fact")

        self.age = f"Возраст: {random.randint(18, 118)}"
        self.gender = random.choice(["Мужской", "Женский"])
        self.profession = self.professions_queue.pop()
        self.health = self.health_queue.pop()
        self.hobby = self.hobby_queue.pop()
        self.items = self.items_queue.pop()
        self.fact = self.fact_queue.pop()
        self.shown_cards = set()

    @staticmethod
    def fetch_and_shuffle_stat(stat_name: str) -> deque:
        count = get_from_db(f"SELECT COUNT(*) FROM {stat_name}_cards")[0] - 1
        query = f"SELECT {stat_name} FROM {stat_name}_cards WHERE ID = {random.randint(0, count)}"
        stat_list = get_from_db(query)
        stat_queue = deque(stat_list)
        random.shuffle(stat_queue)
        return stat_queue

    def show_cards(self) -> str:
        stats = (f"Профессия: {self.profession},\n возраст: {self.age},\n пол: {self.gender},\n"
                 f"здоровье: {self.health},\n хобби: {self.hobby},\n предмет: {self.items},\n"
                 f"факт: {self.fact}")
        return stats

    def add_shown_card(self, card) -> None:
        self.shown_cards.add(card)
