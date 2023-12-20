import pytest

from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid

import requests
from urllib.parse import urljoin
from fe import conf

class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.url = urljoin(conf.URL, "search")
        self.seller_id = "test_add_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)

        code = self.seller.create_store(self.store_id)
        assert code == 200
        book_db = book.BookDB()
        self.search_book = book_db.get_book_info(11,1)[0]
        self.seller.add_book(self.store_id, 0, self.search_book)
        yield

    def test_ok_overall(self):
        overall_keyword = self.search_book.title
        json = {
            "num_page": 1,
            "overall_keyword": overall_keyword
        }
        r = requests.post(self.url, json=json)
        assert r.status_code == 200
        json = {
            "num_page": 1,
            "overall_keyword": overall_keyword,
            "search_target": self.store_id
        }
        r = requests.post(self.url, json=json)
        assert r.status_code == 200

    def test_error_store_overall(self):
        overall_keyword = self.search_book.title
        json = {
            "num_page": 1,
            "overall_keyword": overall_keyword,
            "search_target": self.store_id+"_x"
        }
        r = requests.post(self.url, json=json)
        assert r.status_code != 200

    def test_ok_specific(self):
        title_keyword = self.search_book.title
        author_keyword = self.search_book.author
        json = {
            "num_page": 1,
            "title_keyword": title_keyword,
            "author_keyword": author_keyword,
        }
        r = requests.post(self.url, json=json)
        assert r.status_code == 200

        json = {
            "num_page": 1,
            "title_keyword": title_keyword,
            "author_keyword": author_keyword,
            "search_target": self.store_id
        }
        r = requests.post(self.url, json=json)
        assert r.status_code == 200

    def test_error_store_specific(self):
        title_keyword = self.search_book.title
        author_keyword = self.search_book.author
        json = {
            "num_page": 1,
            "title_keyword": title_keyword,
            "author_keyword": author_keyword,
            "search_target": self.store_id+"_x"
        }
        r = requests.post(self.url, json=json)
        assert r.status_code != 200






