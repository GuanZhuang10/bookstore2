import sqlite3 as sqlite
from sqlalchemy.exc import SQLAlchemyError
from be.model import error
from be.model import db_conn
from be.model.model import *

class Order(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)




    #取消订单
    def cancel_order(self, user_id: str, order_id: str, book_id: str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)

            if not self.user_order_exist(user_id, order_id):
                return 577, 'order not exist : {}'.format(order_id)
                # return error.error_non_exist_order_id(order_id)

            if not self.order_book_exist(order_id, book_id):
                return 599, 'order {} dont have this book {}'.format(order_id,book_id)


            # 查看订单有没有完成
            if self.order_finish(order_id, book_id):
                return 588, 'order finished : {}'.format(order_id)
                # return error.error_order_finish(order_id)



            print('开始修改订单的状态')
            book_order = self.sess.query(NewOrder).filter(NewOrder.order_id == order_id,NewOrder.book_id == book_id)
            book_order.status = 4
            print('订单状态更新完了')
            self.sess.commit()

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            print("{}".format(str(e)))
            return 530, "{}".format(str(e))
        return 200, "ok"



    # 查询某用户的所有订单
    def check_order(self, user_id: str):
        try:
            # 检查用户是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)


            # 先找到所有order的id
            all_orders = self.sess.query(OrderList).filter(OrderList.user_id == user_id).all()
            all_orders_list = []

            for order in all_orders:
                order_id = order.order_id
                store_id = order.store_id

                all_books_list = []
                all_books = self.sess.query(NewOrder).filter(NewOrder.order_id==order_id).all()

                for book in all_books:
                    book_id = book.book_id

                    # 根据book_id去store_book里面获取书的price
                    book_price = self.book_id2price(book_id,store_id)

                    # 根据book_id去book里面获得书的名字
                    book_title = self.book_id2title(book_id)

                    all_books_list.append({'book_id':book_id,'title':book_title,'price':book_price,'count':book.count,'status':book.status})

                all_orders_list.append({'order_id':order.order_id,'store_id':order.store_id,'total_price':order.total_price,'time':order.time,'detail':all_books_list})

        except SQLAlchemyError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            print("{}".format(str(e)))
            return 530, "{}".format(str(e))
        return 200, all_orders_list



    # 查询用户在一个时间间隔下的所有订单





    # 查询一个用户在某个商店下的所有订单


