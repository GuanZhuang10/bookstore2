import pytest

from fe.access.buyer import Buyer
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.logistics import Logistics
from be.model.store import get_session
from be.model.model import NewOrder
from be.model.logistics import Status

import uuid


class TestAddress:
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
        # self.session = get_session()
        self.buyer_id = "test_logistics_buyer_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_logistics_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id
        self.NewAddress = "test_logistics_NewAddress_{}".format(str(uuid.uuid1()))

        # create a buyer
        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        self.seller_id = "test_logistics_seller_id_{}".format(str(uuid.uuid1()))

        # create new order
        gen_book = GenBook(self.seller_id, self.store_id)
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=5)
        code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
        assert 200 == 200

        # lo
        self.logistics = Logistics(self.seller_id, self.buyer_id, self.password, self.order_id)
        yield

    def test_ok(self):
        session = get_session()
        new_orders = session.query(NewOrder).filter(NewOrder.order_id == self.order_id).all()
        for new_order in new_orders:
            new_order.status = Status['UNPAID']
            session.add(new_order)
            session.commit()
        code = self.logistics.change_address(self.buyer_id, self.password, self.NewAddress)
        assert code == 200

    def test_wrong_user_id(self):
        code = self.logistics.change_address(self.buyer_id+"_x", self.password, self.NewAddress)
        assert code != 200

    def test_book_status_delivering(self):
        session = get_session()
        new_orders = session.query(NewOrder).filter(NewOrder.order_id == self.order_id).all()
        for new_order in new_orders:
            new_order.status = Status['DELIVERING']
            session.add(new_order)
            session.commit()
        code = self.logistics.change_address(self.buyer_id, self.password, self.NewAddress)
        assert code != 200

    def test_book_status_cancelled(self):
        session = get_session()
        new_orders = session.query(NewOrder).filter(NewOrder.order_id == self.order_id).all()
        for new_order in new_orders:
            new_order.status = Status['CANCELED']
            session.add(new_order)
            session.commit()
        code = self.logistics.change_address(self.buyer_id, self.password, self.NewAddress)
        assert code != 200

    def test_book_status_received(self):
        session = get_session()
        new_orders = session.query(NewOrder).filter(NewOrder.order_id == self.order_id).all()
        for new_order in new_orders:
            new_order.status = Status['RECEIVED']
            session.add(new_order)
            session.commit()
        code = self.logistics.change_address(self.buyer_id, self.password, self.NewAddress)
        assert code != 200

    def test_wrong_password(self):
        code = self.logistics.change_address(self.buyer_id, self.password + "_x", self.NewAddress)
        assert code != 200

    def test_invalid_newaddress(self):
        self.NewAddress = None
        code = self.logistics.change_address(self.buyer_id, self.password, self.NewAddress)
        assert code != 200


