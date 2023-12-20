import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
import uuid


class TestNewOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_new_order_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_new_order_store_id_{}".format(str(uuid.uuid1()))

        self.buyer_id = "test_new_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id

        # 注册一个新买家
        self.buyer = register_new_buyer(self.buyer_id, self.password)


        '''
        添加一个商家
        给商家添加一个商店
        '''
        self.gen_book = GenBook(self.seller_id, self.store_id)
        yield





    # 创建一些订单， 然后马上取消
    # def tes



    def test_ok(self):

        '''

        下单,先给商家的商店加一点书，然后购买
        '''

        ok, buy_book_id_list = self.gen_book.gen(non_exist_book_id=False, low_stock_level=False)  #[id,count]
        assert ok
        code_0, order_id = self.buyer.new_order(self.store_id, buy_book_id_list)  #得到一个订单号


        # 取消
        code = self.buyer.order_check()
        assert code == 200