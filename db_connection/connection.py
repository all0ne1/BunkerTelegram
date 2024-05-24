import sqlite3


def get_from_db(query: str, fetch_all: bool = False):
    conn = sqlite3.connect('db_connection/bunker_telegram.db')
    cursor = conn.cursor()
    res = cursor.execute(query)
    conn.commit()
    if fetch_all:
        result = res.fetchall()
    else:
        result = res.fetchone()
    cursor.close()
    conn.close()
    return result


def delete_table(game_id: int) -> None:
    conn = sqlite3.connect('db_connection/bunker_telegram.db')
    cursor = conn.cursor()
    cursor.execute(f'DROP TABLE IF EXISTS lobby_{game_id}')
    conn.commit()
    cursor.close()
    conn.close()
