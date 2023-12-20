import uuid
import logging
import datetime
from be.model import db_conn
from be.model import error
from be.model.model import StoreBook, User2, NewOrder, OrderList, UserStore

from apscheduler.schedulers.background import BackgroundScheduler

UNPAID = -1
PAID = 0
DELIVERING = 1
ARRIVED = 2
RECEIVED = 3
CANCELED = 4


def cancel_order(session, order_id, store_book, stock_level):
    ######################order_id上建索引???????????????????????
    # 加锁????????????????????????????????????????????????????
    session.query(NewOrder).filter(NewOrder.order_id == order_id).delete()
    session.query(OrderList).filter(OrderList.order_id == order_id).delete()
    store_book.stock_level = stock_level
    session.commit()


def check_order(session, order_id, store_book, stock_level):
    check = session.query(NewOrder).filter(NewOrder.order_id == order_id).first()
    if check.status == UNPAID:
        cancel_order(session, order_id, store_book, stock_level)


def auto_cancel(session, order_id, store_book, stock_level):
    sched = BackgroundScheduler()
    sched.add_job(check_order, args=[session, order_id, store_book, stock_level], id='check_order_paid', trigger='date',
                  run_date=datetime.datetime.now()+datetime.timedelta(seconds=30))
    sched.start()


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            total_price = 0
            for book_id, count in id_and_count:
                session = self.session
                store_book = session.query(StoreBook).filter(StoreBook.store_id == store_id).filter(
                    StoreBook.book_id == book_id).first()
                if store_book is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = store_book.stock_level
                price = store_book.price

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                total_price = total_price + price * count

                store_book.stock_level = stock_level - count

                order_new = NewOrder(book_id=book_id, order_id=uid, count=count, status=UNPAID)
                session.add(order_new)

            create_time = datetime.datetime.now()
            new_list = OrderList(order_id=uid, user_id=user_id, store_id=store_id, total_price=total_price,
                                 time=create_time)  # 北京时间？？？？？？？？？？
            session.add(new_list)
            session.commit()
            order_id = uid

            auto_cancel(session,order_id,store_book,stock_level)

        except KeyError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            print("{}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        session = self.session
        try:
            order = session.query(OrderList).filter(OrderList.order_id == order_id).first()
            if order is None:
                return error.error_invalid_order_id(order_id)
            print("----------------order get---------------")
            order_id = order.order_id
            print(order_id)
            buyer_id = order.user_id
            store_id = order.store_id
            total_price = order.total_price

            if buyer_id != user_id:
                return error.error_authorization_fail()

            print("---------------authoriztion success------------")

            buyer = session.query(User2).filter(User2.user_id == buyer_id).first()
            if buyer is None:
                return error.error_non_exist_user_id(buyer_id)

            print("---------------buyer existed------------")

            balance = buyer.balance
            if password != buyer.password:
                return error.error_authorization_fail()

            print("---------------authoriztion success------------")

            store = session.query(UserStore).filter(UserStore.store_id == store_id).first()
            if store is None:
                return error.error_non_exist_store_id(store_id)

            print("---------------store exist------------")

            seller_id = store.user_id

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            print("---------------seller existed------------")

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            print("-------------------money enough----------")

            buyer.balance = balance - total_price

            seller = session.query(User2).filter(User2.user_id == seller_id).first()
            seller.balance = seller.balance + total_price
            print("-----------------seller done,buy done-----------------")

            session.commit()

            orders = session.query(NewOrder).filter(NewOrder.order_id == order_id).all()
            for o in orders:
                o.status = PAID
                session.add(o)
            # cursor = conn.execute("DELETE FROM new_order WHERE order_id = ?", (order_id, ))
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)

            # cursor = conn.execute("DELETE FROM new_order_detail where order_id = ?", (order_id, ))
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)

            print("----------------order complete-----------")
            session.commit()



        except KeyError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        session = self.session
        try:
            user = session.query(User2).filter(User2.user_id == user_id).first()
            if user is None:
                return error.error_non_exist_user_id(user_id)

            if user.password != password:
                return error.error_authorization_fail()

            user.balance = user.balance + add_value

            session.commit()
        except KeyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            print("{}".format(str(e)))
            return 530, "{}".format(str(e))

        return 200, "ok"
