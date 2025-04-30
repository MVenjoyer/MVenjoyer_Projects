import sqlite3


def init_db():
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            username TEXT
        )
    ''')
    c.execute('''
            CREATE TABLE IF NOT EXISTS film_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                request TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
    c.execute('''
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    film_name TEXT,
                    request_count INTEGER DEFAULT 0,
                    UNIQUE(user_id, film_name),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );
            ''')
    conn.commit()
    conn.close()


async def add_user(user_id: int, full_name: str, username: str):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO users (user_id, full_name, username)
        VALUES (?, ?, ?)
    ''', (user_id, full_name, username))
    conn.commit()
    conn.close()


async def add_hist(user_id: int, request: str):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO film_history (user_id, request)
        VALUES (?,?)
    ''', (user_id, request))
    conn.commit()
    conn.close()


async def add_stat(user_id: int, film_name: str):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''
       INSERT INTO stats (user_id, film_name, request_count)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, film_name)
            DO UPDATE SET request_count = request_count + 1
        ''', (user_id, film_name))
    conn.commit()
    conn.close()


async def get_stats(user_id: int):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''
        SELECT film_name , request_count FROM stats WHERE user_id = ?
    ''', (user_id,))
    result = c.fetchall()
    conn.close()
    return result


async def get_hist(user_id: int):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''
        SELECT timestamp , request FROM film_history WHERE user_id = ? ORDER BY timestamp DESC
    ''', (user_id,))
    result = c.fetchmany(10)
    conn.close()
    return result


async def get_user(user_id: int):
    conn = sqlite3.connect('bot_database.db')
    c = conn.cursor()
    c.execute('''
        SELECT full_name, username FROM users WHERE user_id = ?
    ''', (user_id,))
    result = c.fetchone()
    conn.close()
    return result
