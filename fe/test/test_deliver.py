from time import sleep

import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.logistics import Logistics, Auto
from fe.access.book import Book

import uuid


class TestDeliver:
    seller_id: str
    buyer_id: str
    password: str
    order_id: str
    store_id: str
    OldAddress: str
    NewAddress: str
    buyer: Buyer

    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_logistics_buyer_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_logistics_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        self.OldAddress = "test_logistics_OldAddress_{}".format(str(uuid.uuid1()))
        self.NewAddress = "test_logistics_NewAddress_{}".format(str(uuid.uuid1()))

        # create a buyer
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        self.seller_id = "test_logistics_seller_id_{}".format(str(uuid.uuid1()))

        # create new order
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        self.buy_book_info_list = gen_book.buy_book_info_list
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert 200 == 200

        # lo
        self.logistics = Logistics(self.seller_id, self.buyer_id, self.password, self.order_id)
        self.total_price = 0
        for item in self.buy_book_info_list:
            book: Book = item[0]
            num = item[1]
            self.total_price = self.total_price + book.price * num
        yield

    def test_book_status_unpaid(self):
        code = self.logistics.start_deliver(self.order_id)
        assert code != 200

    def test_ok(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.logistics.start_deliver(self.order_id)
        assert code == 200

    def test_book_status_received(self):
        code = self.buyer.add_funds(self.total_price)
        assert code == 200
        code = self.buyer.payment(self.order_id)
        assert code == 200
        code = self.logistics.start_deliver(self.order_id)
        assert code == 200
        sleep(6)
        code = self.logistics.confirm_receipt(self.password, self.order_id)
        assert code == 200
        code = self.logistics.start_deliver(self.order_id)
        assert code != 200

    def test_wrong_order_id(self):
        self.order_id = None
        code = self.logistics.start_deliver(self.order_id)
        assert code != 200
