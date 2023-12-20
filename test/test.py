import requests
import json
import jwt
import time



from be.model.helper import get_sess
from be.model.helper import session,User


headers = {'Content-Type': 'application/json'}

def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.decode("utf-8")

def jwt_decode(encoded_token:str, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


if __name__ == '__main__':
    # res=session.query(User).filter(User.user_id==2).first()
    # if res==None:
    #     print(res)

    ## 创建用户
    # data = {'user_id':200,'password':2}
    # url = 'http://127.0.0.1:5000/auth/register'
    # r = requests.post(url=url,headers = headers,data=json.dumps(data))

    # # 添加商店
    # data = {'store_id':200,'user_id':2}
    # url = 'http://127.0.0.1:5000/seller/create_store'
    # r = requests.post(url=url,headers = headers,data=json.dumps(data))


    # # 为商店添加新的书本
    # data = {'store_id': 100, 'user_id': 2, 'book_info':{'id':'100'},'stock_level':10}
    # url = 'http://127.0.0.1:5000/seller/add_book'
    # r = requests.post(url=url, headers=headers, data=json.dumps(data))

    # # 将商店中的书的库存增加一点
    # data = {'store_id': 100, 'user_id': 5, 'book_id':100,'add_stock_level':7}
    # url = 'http://127.0.0.1:5000/seller/add_stock_level'
    # r = requests.post(url=url, headers=headers, data=json.dumps(data))

    data = {''}
    print(r)
    print(r.status_code)
    print('----')
    print(r.text)
    print('****')
    print(r.content)