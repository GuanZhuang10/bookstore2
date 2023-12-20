from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.model import *
from be.model import order



import json

bp_order = Blueprint("order", __name__, url_prefix="/order")







# 取消订单
@bp_order.route("/cancel", methods=["POST"])
def order_cancel():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    book_id: str = request.json.get("book_id")


    s = order.Order()
    code, message = s.cancel_order(user_id, order_id, book_id)
    return jsonify({"message": message}), code




# 查询订单
@bp_order.route("/check", methods=["POST"])
def order_check():
    user_id: str = request.json.get("user_id")


    s = order.Order()
    code, message = s.check_order(user_id)
    return jsonify({"message": message}), code



