import jwt
import time
import logging
import sqlite3 as sqlite

import psycopg2

from be.model import error
from be.model import db_conn


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded


def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT into \"user\"(user_id, password, balance, token, terminal) "
                "VALUES (%s, %s, %s, %s, %s);",
                (user_id, password, 0, token, terminal),
            )
            self.conn.commit()
        except psycopg2.Error:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT token FROM user WHERE user_id=%s", (user_id,))
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return error.error_authorization_fail()
        db_token = row[0]
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT password FROM user WHERE user_id=%s", (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()

        if row is None:
            return error.error_authorization_fail()

        if password != row[0]:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        cursor = None
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE user set token= %s , terminal = %s where user_id = %s",
                (token, terminal, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_authorization_fail() + ("",)
            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""

        finally:
            if cursor:
                cursor.close()

        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        curses = None
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE user SET token = %s, terminal = %s WHERE user_id=%s",
                (dummy_token, terminal, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_authorization_fail()

            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        cursor = None
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            cursor = self.conn.cursor()
            cursor.execute("DELETE from user where user_id=%s", (user_id,))
            if cursor.rowcount == 1:
                self.conn.commit()
            else:
                return error.error_authorization_fail()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        cursor = None
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE user set password = %s, token= %s , terminal = %s where user_id = %s",
                (new_password, token, terminal, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_authorization_fail()

            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def search_book(self, search_query, search_scopes):
        cursor = None
        try:
            query = ""
            params = []

            if search_scopes:
                if 'title' in search_scopes:
                    query += "title LIKE %s OR "
                    params.append(f"%{search_query}%")

                if 'content' in search_scopes:
                    query += "content LIKE %s OR "
                    params.append(f"%{search_query}%")

                if params:
                    query = query.rstrip(" OR ")

                if 'tags' in search_scopes:
                    query += "tags LIKE %s OR "
                    params.append(f"%{search_query}%")

                if 'book_intro' in search_scopes:
                    query += "book_intro LIKE %s OR "
                    params.append(f"%{search_query}%")
            cursor = self.conn.cursor()

            if not query and search_query:
                query = "title LIKE %s OR tags LIKE %s OR book_intro LIKE %s OR content LIKE %s"
                params = [f"%{search_query}%" for _ in range(4)]
            if not search_scopes and not search_query:
                return 200, {"titles": 'titles', "num": '100'}

            cursor.execute(f"SELECT COUNT(*) FROM store WHERE {query}", tuple(params))
            total_results = cursor.fetchone()[0]

            cursor.execute(f"SELECT title FROM store WHERE {query}", tuple(params))
            book_titles = [book[0] for book in cursor.fetchall()]

            if total_results == 0:
                return 404, "Not Found"
            else:
                return 200, {"titles": book_titles, "num": total_results}
        finally:
            cursor.close()
