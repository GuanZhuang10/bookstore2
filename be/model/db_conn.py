from be.model.store import get_session
from be.model.model import StoreBook, User2, UserStore, OrderList, NewOrder
from be.model.logistics import Status




class DBConn:
    def __init__(self):
        self.session = get_session()
        self.sess = get_session()

    def user_id_exist(self, user_id):
        user = self.session.query(User2).filter(User2.user_id == user_id).first()
        if user is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        book = self.session.query(StoreBook).filter(StoreBook.store_id == store_id, StoreBook.book_id == book_id).first()
        if book is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        store = self.session.query(UserStore).filter(UserStore.store_id == store_id).first()
        if store is None:
            return False
        else:
            return True

    def user_order_exist(self, user_id, order_id):
        order = self.sess.query(OrderList).filter(OrderList.user_id == user_id,OrderList.order_id == order_id).first()
        if order is None:
            return False
        else:
            return True

    # 取消订单函数

    ## 看看订单里面是否有这本书
    def order_book_exist(self,order_id, book_id):
        order_book = self.sess.query(NewOrder).filter(NewOrder.order_id == order_id, NewOrder.book_id == book_id).first()
        if order_book is None:
            return False
        else:
            return True

    ## 判断订单的状态是否还在进行
    def order_proceed(self, order_id, book_id):
        order = self.sess.query(NewOrder).filter(NewOrder.order_id == order_id, NewOrder.book_id == book_id,
                                                  NewOrder.status != Status['RECEIVED'],
                                                  NewOrder.status != Status['CANCELED']).first()
        order = self.sess.query(NewOrder).filter(NewOrder.order_id == order_id, NewOrder.book_id == book_id).first()
        print('****')
        print(order.status)
        print('****')
        if order is None:
            return False
        else:
            return True

    def order_finish(self, order_id, book_id):
        return not self.order_proceed(order_id, book_id)

    # 查询订单相关函数
    ## 根据book_id从book中获取title
    def book_id2title(self, book_id):
        # the_book = self.sess.query(Book).filter(Book.book_id == book_id).first()
        # if the_book is None:
        #     return False
        # else:
        #     return the_book.title
        return ""

    ## 根据book_id和store_id从store_book中获取price
    def book_id2price(self, book_id, store_id):
        # the_book = self.sess.query(StoreBook).filter(StoreBook.book_id == book_id,
        #                                              StoreBook.store_id == store_id).first()
        #
        # if the_book is None:
        #     return False
        # else:
        #     return the_book.price
        return 0
