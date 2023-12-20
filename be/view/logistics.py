from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.logistics import Logistics

bp_logistics = Blueprint("logistics", __name__, url_prefix="/logistics")


@bp_logistics.route('/address', methods=['POST'])
def change_address():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    print(password)
    order_id = request.json.get("order_id", "")
    NewAddress = request.json.get("NewAddress", "")
    logistics = Logistics()
    code, message = logistics.change_address(user_id,  order_id, password, NewAddress)
    return jsonify({"message": message}), code


@bp_logistics.route('/deliver', methods=['POST'])
def start_deliver():
    order_id = request.json.get("order_id", "")
    logistics = Logistics()
    code, message = logistics.start_deliver(order_id)
    return jsonify({"message": message}), code


@bp_logistics.route('/confirm', methods=["POST"])
def confirm_receipt():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    order_id = request.json.get("order_id", "")
    logistics = Logistics()
    code, message = logistics.confirm_receipt(user_id, password, order_id)
    return jsonify({"message": message}), code

