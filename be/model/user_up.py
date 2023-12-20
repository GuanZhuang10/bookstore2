from datetime import datetime

import jwt
from sqlalchemy import Column, String, exc, Float
# from model.db_conn import  DBConn
from sqlalchemy.ext.declarative import declarative_base
import time
from be.model import error_up
from be.model.model import *

jwt_key = 'upupup'


def jwt_encode(user_id, terminal):
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=jwt_key,
        algorithm="HS256",
    )
    return encoded.decode("utf-8")


def jwt_decode(encoded_token):
    try:
        decoded = jwt.decode(encoded_token, key=jwt_key, algorithms="HS256")
        return decoded
    except jwt.ExpiredSignatureError:
        return None

from be.model.store import get_session


token_lifetime = 3600  # 3600 second


class User:

    def __init__(self):
        # self.session = DBConn.session
        self.session = get_session()
        self.token_lifetime = 3600

    def __check_password(self, true_password, input_password):
        # return bcrypt.check_password_hash(true_password, input_password)
        return true_password == input_password

    def __check_token(self, db_token, input_token):
        try:
            jwt_text = jwt_decode(encoded_token=db_token)
            login_time = jwt_text['timestamp']
            if db_token != input_token:
                return False
            if login_time is not None:
                now = time.time()
                if 0 <= now - login_time < self.token_lifetime:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            return False

    def register(self, user_id: str, password: str):
        if self.session.query(User2).filter(User2.user_id == user_id).one_or_none():
            return error_up.error_exist_user_id(user_id)
        else:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            user = User2()
            user.user_id = user_id
            # hashpass = bcrypt.generate_password_hash(password.encode('utf-8')).decode('utf-8')  # want a string instead of a byte
            hashpass = password
            user.password = hashpass
            user.token = token
            user.balance = 0
            try:
                self.session.add(user)
                self.session.commit()
            except exc.IntegrityError:
                self.session.rollback()
                return error_up.error_exist_user_id(user_id)
            return 200, "Register successfully!"

    def unregister(self, user_id, password):
        user = self.session.query(User2).filter(User2.user_id == user_id).one_or_none()
        if user is None or self.__check_password(user.password, password) is False:
            return 401, 'user_id: {} not exist, or password is wrong'.format(user_id)
        else:
            self.session.delete(user)
            try :
             self.session.commit()
            except:
                self.rollback()
            return 200, 'Successfully unregister!'

    def login(self, user_id, password, terminal):
        user = self.session.query(User2).filter(User2.user_id == user_id).one_or_none()
        if user is None or self.__check_password(user.password, password) is False:
            return 401, 'user_id not exist, or password is wrong', ""
        token = jwt_encode(user_id, terminal)
        user.token = token
        self.session.add(user)
        self.session.commit()
        # self.session.close()
        return 200, 'Successfully login!', token

    def change_password(self, user_id, old_password, new_password):
        user = self.session.query(User2).filter(User2.user_id == user_id).one_or_none()
        if user is None or self.__check_password(user.password, old_password) is False:
            return 401, 'Change password failed!'
        user.password = new_password
        self.session.add(user)
        self.session.commit()
        # self.session.close()
        return 200, 'Successfully change password!'

    def logout(self, user_id, token):
        user = self.session.query(User2).filter(User2.user_id == user_id).one_or_none()
        if user is None or self.__check_token(user.token, token) is False:
            return 401, 'Wrong user_id, password or invalid token! '
        # update token to None
        user.token = None
        try:
            self.session.add(user)
            self.session.commit()
        except exc.IntegrityError:
            self.session.rollback()
            return error_up.error_break_in_commit()
        return 200, 'Successfully log out!'
