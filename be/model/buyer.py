from datetime import datetime, timedelta

import psycopg2
import json
import logging
import uuid
from be.model import db_conn
from be.model import error

class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        cursor = None
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT book_id, stock_level, book_info FROM store "
                    "WHERE store_id = %s AND book_id = %s;",
                    (store_id, book_id),
                )
                row = cursor.fetchone()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = row[1]
                book_info = row[2]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor.execute(
                    "UPDATE store set stock_level = stock_level - %s "
                    "WHERE store_id = %s and book_id = %s and stock_level >= %s; ",
                    (count, store_id, book_id, count),
                )
                if cursor.rowcount == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor.execute(
                    "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                    "VALUES(%s, %s, %s, %s);",
                    (uid, book_id, count, price),
                )

            # cursor.execute(
            #     "INSERT INTO new_order(order_id, store_id, user_id) "
            #     "VALUES(%s, %s, %s);",
            #     (uid, store_id, user_id),
            # )
            # self.conn.commit()
            order_id = uid
            now_time = datetime.utcnow()
            cursor.execute(
                "INSERT INTO new_order(order_id, store_id, user_id, book_status, order_time) "
                "VALUES(%s, %s, %s, 2, %s);",
                (uid, store_id, user_id, now_time),
            )
            self.conn.commit()

        finally:
            if cursor:
                cursor.close()
        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT order_id, store_id, user_id, book_status, order_time FROM new_order WHERE order_id = %s",
                (order_id,),
            )
            # cursor.execute(
            #     "SELECT order_id, store_id, user_id FROM new_order WHERE order_id = %s",
            #     (order_id,),
            # )
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[2]
            store_id = row[1]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            cursor.execute(
                "SELECT balance, password FROM \"user\" WHERE user_id = %s;", (buyer_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor.execute(
                "SELECT store_id, user_id FROM user_store WHERE store_id = %s;",
                (store_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            cursor.execute(
                "SELECT book_id, count, price FROM new_order_detail WHERE order_id = %s;",
                (order_id,),
            )
            total_price = 0
            for row in cursor:
                count = row[1]
                price = row[2]
                total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            cursor.execute(
                "UPDATE \"user\" SET balance = balance - %s "
                "WHERE user_id = %s AND balance >= %s",
                (total_price, buyer_id, total_price),
            )

            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)

            cursor.execute(
                "UPDATE \"user\" set balance = balance + %s "
                "WHERE user_id = %s",
                (total_price, buyer_id),
            )

            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(buyer_id)

            cursor.execute(
                "DELETE FROM new_order WHERE order_id = %s", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            cursor.execute(
                "DELETE FROM new_order_detail where order_id = %s", (order_id,)
            )
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            cursor.execute(
                "INSERT INTO new_order_paid (order_id, user_id, store_id, book_status, price) "
                "VALUES (%s, %s, %s, 1, %s)",
                (order_id, buyer_id, store_id, total_price),
            )

            self.conn.commit()

        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT password  from \"user\" where user_id=%s", (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor.execute(
                "UPDATE \"user\" SET balance = balance + %s WHERE user_id = %s",
                (add_value, user_id),
            )
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()

        finally:
            if cursor:
                cursor.close()
        return 200, "ok"

    def order_cancel(self, user_id: str, order_id: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT order_id, store_id, user_id, book_status, order_time FROM new_order WHERE order_id = %s",
                (order_id,),
            )
            new_order_result = cursor.fetchone()

            if new_order_result is not None:
                order_id, store_id, buyer_id, book_status, order_time = new_order_result
                if buyer_id != user_id:
                    return error.error_authorization_fail()

                cursor.execute("DELETE FROM new_order WHERE order_id = %s", (order_id,))
            else:
                cursor.execute(
                    "SELECT order_id, store_id, user_id, book_status, price FROM new_order_paid WHERE order_id = %s",
                    (order_id,)
                )
                new_order_paid_result = cursor.fetchone()
                if new_order_paid_result:
                    order_id, store_id, buyer_id, book_status, price = new_order_paid_result
                    if buyer_id != user_id:
                        return error.error_authorization_fail()

                    cursor.execute(
                        "UPDATE \"user\" SET balance = balance + %s WHERE user_id = %s",
                        (price, buyer_id)
                    )
                    cursor.execute(
                        "UPDATE \"user\" SET balance = balance - %s WHERE user_id = %s",
                        (price, store_id)
                    )
                    cursor.execute("DELETE FROM new_order_paid WHERE order_id = %s", (order_id,))

                else:
                    return error.error_invalid_order_id(order_id)

                cursor.execute(
                    "SELECT book_id, count FROM new_order_detail WHERE order_id = %s",
                    (order_id,)
                )
                orders_result = cursor.fetchall()
                for order_result in orders_result:
                    book_id, count = order_result
                    cursor.execute(
                        "UPDATE store SET stock_level = stock_level + %s WHERE store_id = %s AND book_id = %s",
                        (count, store_id, book_id)
                    )
            return 200, "ok"
        finally:
            cursor.close()

    def history_order(self, user_id: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT order_id, store_id, user_id, book_status, order_time FROM new_order WHERE user_id = %s",
                (user_id,),
            )
            new_orders_result = cursor.fetchall()
            if new_orders_result:
                for new_order_result in new_orders_result:
                    order_id = new_order_result[0]
                    cursor.execute(
                        "SELECT book_id, count, price FROM new_order_detail WHERE order_id = %s",
                        (order_id,)
                    )

                    new_order_details_result = cursor.fetchall()
                    if new_order_details_result:
                        return error.error_invalid_order_id(order_id)

            cursor.execute(
                "SELECT order_id, store_id, user_id, book_status, price FROM new_order_paid WHERE user_id = %s",
                (user_id,)
            )

            new_orders_paid_row = cursor.fetchall()
            if not new_orders_paid_row:
                return error.error_invalid_order_id(order_id)
            return 200, "ok"


            if new_orders_paid_row:
                for new_order_paid_rows in new_orders_paid_row:
                    order_id = new_order_paid_rows[0]
                    cursor.execute(
                        "SELECT book_id, count, price FROM new_order_detail WHERE order_id = %s",
                        (order_id,)
                    )
        except Exception as e:
            return 500, "Internal Server Error"
        finally:
            cursor.close()

    def order_status(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            timeout_datetime = datetime.now() - timedelta(seconds=5)

            cursor.execute("DELETE FROM new_order WHERE order_time <= %s", (timeout_datetime,))
            return 200, "ok"
        finally:
            cursor.close()

    def receive_book(self, user_id: str, order_id: str) -> (int, str):
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM new_order_paid WHERE order_id = %s", (order_id,))
            row = cursor.fetchone()

            if row is None:
                return error.error_invalid_order_id(order_id)

            buyer_id = row["user_id"]
            books_status = row["book_status"]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            if books_status == 1:
                return error.error_book_has_not_sent()

            if books_status == 2:
                return error.error_not_paid_book()

            if books_status == 3:
                return error.error_book_has_received()

            cursor.execute("UPDATE new_order_paid SET book_status = 3 WHERE order_id = %s", (order_id,))
            self.conn.commit()

            return 200, "ok"

        finally:
            if cursor:
                cursor.close()