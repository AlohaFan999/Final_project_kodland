import sqlite3
from config import DATABASE


class DatabaseManager:
    def __init__(self, database):
        self.database = database

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                    request_id INTEGER PRIMARY KEY,
                    question TEXT,
                    status_id INTEGER,
                    moder_id INTEGER,
                    user_id INTEGER,
                    FOREIGN KEY(status_id) REFERENCES statuses(status_id),
                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                    FOREIGN KEY(moder_id) REFERENCES moders(moder_id)
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS statuses (
                    status_id INTEGER PRIMARY KEY,
                    name TEXT
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS moders (
                    moder_id INTEGER PRIMARY KEY,
                    name TEXT,
                    nickname TEXT
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS message (
                    message_id INTEGER PRIMARY KEY,
                    request_id INTEGER,
                    user_id INTEGER,
                    text TEXT,
                    FOREIGN KEY(request_id) REFERENCES requests(request_id),
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prepared_questions (
                    question_id INTEGER PRIMARY KEY,
                    text TEXT,
                    answer TEXT
                )
                """
            )

    def add_request(self, user_id, text):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(
            """
                INSERT INTO requests (question, status_id, user_id) VALUES (?, 0, ?)
            """,(text, user_id))

            conn.commit()


    def get_last_request(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
            """
                SELECT request_id FROM requests WHERE user_id = ? ORDER BY request_id DESC LIMIT 1
            """, (user_id,))
            request_id = cur.fetchone()
            return request_id

    def update_request(self, request_id, moder_id):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(
            """
                UPDATE requests SET status_id = 1, moder_id = ? WHERE request_id = ?
            """,(moder_id, request_id))

            conn.commit()

    def get_request(self, request_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
            """
                SELECT moder_id, user_id FROM requests WHERE request_id = ? LIMIT 1
            """, (request_id,))
            result = cur.fetchone()
            return result

    def add_message(self, request_id, user_id, text):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute(
            """
                INSERT INTO message (request_id, user_id, text) VALUES (?, ?, ?)
            """,(request_id, user_id, text))

            conn.commit()

    def get_all_text(self, request_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
            """
                SELECT user_id, text FROM message WHERE request_id = ? ORDER BY message_id
            """, (request_id,))
            result = cur.fetchall()
            return result

    def get_prep_questions(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(
            """
               SELECT text, answer FROM prepared_questions
            """)
            questions = cur.fetchall()
            return questions


    def add_statuses(self):
        users_data = [('Вопрос принят модератором',), ('Модератор решает вопрос с пользователем',), ('Вопрос успешно решен',), ('Ответ на вопрос найти невозможно',)]
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany("INSERT INTO statuses (name) VALUES (?)", users_data)


    def add_questions(self):
        questions = [
            ('По прошествии 3 минут, деньги все еще не пришли, что делать?', 'С вашими деньгами все в порядке, обновите страничку, проверьте сетевое подключение или просто подождите еще чуток :)'),
            ('Боюсь оставлять личные данные на сайте, можно ли обойтись без этого?', 'К сожалению перевод денег на ваш аккаунт Steam ведется только при помощи логина, а в случае возникновения ошибки контактировать с вами придется по средствам вашей электронной почты, поэтому подобные меры обязательны')
            ]
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany("INSERT INTO prepared_questions (text, answer) VALUES (?, ?)", questions)





#db = DatabaseManager(DATABASE)
#db.create_tables()
#db.add_statuses()
#db.add_questions()
#a = db.get_prep_questions()
#print(a)
