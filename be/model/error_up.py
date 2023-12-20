error_code = {
    500: 'Failed to register, the user_id: {} is duplicate!',
    501: 'Failed to unregister, the user_id: {} is not found!',
    502: 'The password is wrong!',
    503: 'The token is wrong!',
    504: 'Break in in process of commit!',
    505: 'The order_id: {} does not exist!',
    506: 'The order has been delivered!',
    507: 'The address is invalid!',
    508: 'The order has been cancelled!',
    509: 'The order has not been arrived!',
    510: 'The order has been received! ',
    511: 'The order has not paid',
    512: 'The order is not prepared for delivering!'
}


def error_exist_user_id(user_id):
    return 500, error_code[500].format(user_id)


def error_not_exist_user_id(user_id):
    return 501, error_code[501].format(user_id)


def error_wrong_password():
    return 502, error_code[502]


def error_wrong_token():
    return 503, error_code[503]


def error_break_in_commit():
    return 504, error_code[504]


def error_order_not_exist(order_id):
    return 505, error_code[505].format(order_id)


def error_order_in_delivering():
    return 506, error_code[506]


def error_invalid_address():
    return 507, error_code[507]


def error_order_cancelled():
    return 508, error_code[508]


def error_order_not_arrived():
    return 509, error_code[509]


def error_order_has_been_received():
    return 510, error_code[510]


def error_order_not_paid():
    return 511, error_code[511]


def error_order_invalid_status():
    return 512, error_code[512]
