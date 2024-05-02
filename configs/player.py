from db_connection.connection import get_from_db
from collections import deque
import random


class Player:
    def __init__(self, game_id):
        # Assuming each stat queue has been fetched and stored somewhere accessible
        self.game_id = game_id
        self.initialize_stat_queues()
        self.stat_names = {"profession", "health", "hobby", "items", "fact"}
        for names in self.stat_names:
            self.fetch_and_shuffle_stat(names)
        self.age = random.randint(18,118)
        self.gender = random.choice(["Мужской","Женский"])
        self.profession = professions_queue.pop()
        self.health = health_queue.pop()
        self.hobby = hobby_queue.pop()
        self.items = items_queue.pop()
        self.fact = fact_queue.pop()
        self.shown_cards = set()
    @staticmethod
    def initialize_stat_queues():
        global professions_queue, health_queue, hobby_queue, items_queue, fact_queue
        professions_queue = Player.fetch_and_shuffle_stat(stat_name="profession")
        health_queue = Player.fetch_and_shuffle_stat(stat_name="health")
        hobby_queue = Player.fetch_and_shuffle_stat(stat_name="hobby")
        items_queue = Player.fetch_and_shuffle_stat(stat_name="items")
        fact_queue = Player.fetch_and_shuffle_stat(stat_name="fact")

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
