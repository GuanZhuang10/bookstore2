import pytest

from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import  register_new_buyer
from be.model.store import get_session
from be.model.model import NewOrder
import uuid
import time

class TestAutoCancel:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_payment_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_payment_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_payment_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert code == 200

        time.sleep(40)
        yield

    def test_ok(self):
        session = get_session()
        check = session.query(NewOrder).filter(NewOrder.order_id == self.order_id).first()
        assert check is None