import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid




'''
 修改了

fe.access.buyer




'''
class TestNewOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_order_cancel_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_order_cancel_store_id_{}".format(str(uuid.uuid1()))

        self.buyer_id = "test_order_cancel_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id

        # 注册一个新买家
        self.buyer = register_new_buyer(self.buyer_id, self.password)


        # 在商家的一些店里面， 加一些书
        self.gen_book = GenBook(self.seller_id, self.store_id)
        yield





    # 创建一些订单， 然后马上取消
    def test_no_order(self):
        code = self.buyer.order_cancel('@', '^')
        assert code != 200

    def test_ok(self):
        # 创建书， 下单
        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False) #列表里面是(book_id, count)
        assert ok
        code_0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)  #得到一个订单号
        # print('code_0 is :'+ str(code_0))

        # 取消
        book_id = buy_book_id_list[0][0]


        code = self.buyer.order_cancel(order_id,book_id)
        assert code == 200