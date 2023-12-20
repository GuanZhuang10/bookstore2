import sys
# sys.path.append('C:\\Users\\24850\\OneDrive - stu.ecnu.edu.cn\\github\\bookstore')

import requests
import threading
from urllib.parse import urljoin
from be import serve
from fe import conf
import time


thread: threading.Thread = None


def run_backend():
    # rewrite this if rewrite backend
    serve.be_run()
    # app.run()

def pytest_configure(config):
    global thread
    print("frontend begin test")
    thread = threading.Thread(target=run_backend)
    thread.start()
    time.sleep(10)


def pytest_unconfigure(config):
    url = urljoin(conf.URL, "shutdown")
    requests.get(url)
    thread.join()
    print("frontend end test")
