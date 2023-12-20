import requests
from urllib.parse import urljoin
from fe.access.auth import Auth
from fe.access.buyer import Buyer
from fe import conf
Auto = 5
class Logistics:
    def __init__(self, seller_id, buyer_id, password, order_id):
        self.url_prefix = urljoin(conf.URL, "logistics/")
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.password = password
        self.terminal = "my terminal"
        self.order_id = order_id
        self.auth = Auth(conf.URL)
        print('Lo:', self.password)
        code, self.token = self.auth.login(self.buyer_id, self.password, self.terminal)
        assert code == 200

    def change_address(self, buyer_id, password, NewAddress):
        json = {"user_id": buyer_id, "order_id": self.order_id,
                "NewAddress": NewAddress,
                "password": password}
        url = urljoin(self.url_prefix, "address")
        headers = {"token": self.token}
        print("Ac: ", password)
        r = requests.post(url, headers=headers, json=json)
        print(r.text)
        return r.status_code

    def start_deliver(self, order_id):
        json = {"order_id": order_id}
        url = urljoin(self.url_prefix, "deliver")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def confirm_receipt(self, password, order_id):
        json = {"user_id": self.buyer_id, "password": password,
                "order_id": order_id}
        url = urljoin(self.url_prefix, "confirm")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def cancel_order(self, order_id, book_id):
        json = {'user_id': self.buyer_id, 'order_id': order_id, 'book_id': book_id}
        url = 'http://127.0.0.1:5000/order/cancel'
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code


