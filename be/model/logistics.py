import datetime

from sqlalchemy import exc

from be.model.model import *
from be.model import error_up
from be.model.store import get_session
import random
from apscheduler.schedulers.background import BackgroundScheduler

# new definition of status
Status = {
    'UNPAID': -1,
    'PAID': 0,
    'DELIVERING': 1,
    'ARRIVED': 2,
    'RECEIVED': 3,
    'CANCELED': 4,
}
Auto = 5


class Logistics:
    def __init__(self):
        self.session = get_session()

    def __check_password(self, db_password, password):
        return db_password == password

    def change_address(self, user_id, order_id, password, NewAddress):
        user = self.session.query(User2).filter(User2.user_id == user_id).one_or_none()
        order = self.session.query(OrderList).filter(OrderList.order_id == order_id).one_or_none()
        if NewAddress is None:
            return error_up.error_invalid_address()
        if self.__check_password(user.password, password) is False:
            return error_up.error_wrong_password()
        elif order is None:
            return error_up.error_order_not_exist(order_id)
        else:
            new_orders = self.session.query(NewOrder).filter(NewOrder.order_id == order.order_id).all()
            for new_order in new_orders:
                status = new_order.status
                if status == Status['DELIVERING']:
                    return error_up.error_order_in_delivering()
                elif status == Status['CANCELED']:
                    return error_up.error_order_cancelled()
                elif status == Status['RECEIVED']:
                    return error_up.error_order_has_been_received()
            try:
                order.address = NewAddress
                self.session.add(order)
                self.session.commit()
            except exc.IntegrityError:
                self.session.rollback()
                return error_up.error_break_in_commit()
            return 200, 'Successfully change the address!'

    def order_arrived(self, order_id):
        print('----------------------------arrived---------')
        new_orders = self.session.query(NewOrder).filter(NewOrder.order_id == order_id).all()
        try:
            for new_order in new_orders:
                if new_order.status == Status['DELIVERING']:
                    new_order.status = Status['ARRIVED']
                    print('----------------------------arrived---------')
                    self.session.add(new_order)
            self.session.commit()
        except:
            self.session.rollback()
        return 200, 'Order Successfully arrived!'

    def start_deliver(self, order_id):
        order = self.session.query(OrderList).filter(OrderList.order_id == order_id).one_or_none()
        if order is None:
            return error_up.error_order_not_exist(order_id)
        new_orders = self.session.query(NewOrder).filter(NewOrder.order_id == order.order_id).all()
        cancel_num = 0
        try:
            sched = BackgroundScheduler()
            for new_order in new_orders:
                status = new_order.status

                if status == Status['UNPAID']:
                    return error_up.error_order_not_paid()

                elif status == Status['RECEIVED']:
                    return error_up.error_order_has_been_received()

                elif status == Status['CANCELED']:
                    cancel_num += 1

                elif status == Status['PAID']:
                    new_order.status = Status['DELIVERING']
                    print('----deliver--------')
                    self.session.add(new_order)
            self.session.commit()
            print('--------prepare to arrive------')
            job_id = 'arrived_{}'.format(order.order_id)
            sched.add_job(self.order_arrived, args=[order_id], id=job_id,
                          trigger='date',
                          run_date=datetime.datetime.now() + datetime.timedelta(
                              seconds=3))
            sched.start()
        except:
            self.session.rollback()
        if cancel_num == len(new_orders):
            return error_up.error_order_cancelled()
        elif cancel_num == 0:
            return 200, 'Successfully deliver the order!'
        else:
            return 200, 'Some of the books have been cancelled! The rest are successfully delivered!'

    def confirm_receipt(self, user_id, password, order_id):
        user = self.session.query(User2).filter(User2.user_id == user_id).one_or_none()
        if self.__check_password(user.password, password) is False:
            return error_up.error_wrong_password()

        order = self.session.query(OrderList).filter(OrderList.order_id == order_id).one_or_none()
        if order is None:
            return error_up.error_order_not_exist(order_id)

        new_orders = self.session.query(NewOrder).filter(NewOrder.order_id == order.order_id).all()
        try:
            print("----------confirm---------")
            for new_order in new_orders:
                status = new_order.status

                if status < Status['ARRIVED']:
                    return error_up.error_order_not_arrived()

                elif status == Status['CANCELED']:
                    continue

                else:
                    new_order.status = Status['RECEIVED']
                    self.session.add(new_order)
            self.session.commit()
        except:
            self.session.rollback()
        return 200, 'Successfully confirm the receipt of the order!'
