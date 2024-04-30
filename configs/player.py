from db_connection import connection
import random


class Player:
    def __init__(self,game_id):
        self.pr_count = connection.get_from_db("SELECT COUNT(Profession) FROM cards")[0]
        self.health_count = connection.get_from_db("SELECT COUNT(Health) FROM cards")[0]
        self.hobby_count = connection.get_from_db("SELECT COUNT(Hobby) FROM cards")[0]
        self.items_count = connection.get_from_db("SELECT COUNT(Items) FROM cards")[0]
        self.fact_count = connection.get_from_db("SELECT COUNT(Fact) FROM cards")[0]
        self.gender = connection.get_from_db(f"SELECT Gender FROM lobby_{game_id} WHERE ID = {random.randint(0, 100)}")[0]
        self.age = connection.get_from_db(f"SELECT Age FROM lobby_{game_id} WHERE ID = {random.randint(0, 100)}")[0]
        self.profession = connection.get_from_db(f"SELECT Profession FROM lobby_{game_id}"
                                                 f" WHERE ID = {random.randint(0, self.pr_count)}")[0]
        self.health = connection.get_from_db(f"SELECT Health FROM lobby_{game_id} "
                                             f"WHERE ID = {random.randint(0, self.health_count)}")[0]
        self.hobby = connection.get_from_db(f"SELECT Hobby FROM lobby_{game_id} "
                                            f"WHERE ID = {random.randint(0, self.hobby_count)}")[0]
        self.items = connection.get_from_db(f"SELECT Items FROM lobby_{game_id} "
                                            f"WHERE ID = {random.randint(0, self.items_count)}")[0]
        self.fact = connection.get_from_db(f"SELECT Fact FROM lobby_{game_id} "
                                           f"WHERE ID = {random.randint(0, self.fact_count)}")[0]

    def show_cards(self) -> str:
        stats = (f"Профессия: {self.profession},\n возраст: {self.age},\n пол: {self.gender},\n"
                 f"здоровье: {self.health},\n хобби: {self.hobby},\n предмет: {self.items},\n"
                 f"факт: {self.fact}")
        return stats
