import json
import os

from mbtest.src.dao.orders_dao import OrdersDAO
from mbtest.src.utilities.wooAPIUtility import WooAPIUtility


class OrdersHelper(object):

    def __init__(self):
        self.cur_file_dir = os.path.dirname(os.path.realpath(__file__))
        self.woo_helper = WooAPIUtility()

    def create_order(self, additional_args=None):

        payload_template = os.path.join(self.cur_file_dir, '..', 'data', 'create_order_payload.json')

        with open(payload_template) as f:
            payload = json.load(f)

        # if user adds more info to payload, then update it
        if additional_args:
            assert isinstance(additional_args, dict), f"Parameter 'additional_args' must be a dictionary by found {type(additional_args)}"
            payload.update(additional_args)

        rs_api = self.woo_helper.post('orders', params=payload, expected_status_code=201)

        return rs_api

    @staticmethod
    def verify_order_is_created(order_json, exp_cust_id, exp_products):
        orders_dao = OrdersDAO()

        # verify response
        assert order_json, f"Create order response is empty."
        assert order_json['customer_id'] == exp_cust_id, "Create order with given customer id returned" \
                                                         f"bad customer. Expected customer_id={exp_cust_id}" \
                                                         f", but got {order_json['customer_id']}"

        assert len(order_json['line_items']) == len(exp_products), f"Expected {len(exp_products)} item in order but" \
                                                   f" found '{len(order_json['line_tems'])}'" \
                                                   f"Order_id: {order_json['order_id']}."


        # verify db
        order_id = order_json['id']
        line_info = orders_dao.get_order_lines_by_order_id(order_id)
        assert line_info, f"Create order, line item not found in DB. Order id: {order_id}"

        line_items = [i for i in line_info if i['order_item_type'] == 'line_item']
        assert len(line_items) == 1, f"Expected 1 line item but found {len(line_items)} Order id{order_id}"

        # get list of products ids in the response
        api_product_ids = [i['product_id'] for i in order_json['line_items']]

        for product in exp_products:
            assert product['product_id'] in api_product_ids, f"Create order does not have at least 1 expected product in DB" \
                                                             f"Product id: {product['product_id']}, order id: {order_id}"

    def call_update_an_order(self, order_id, payload):
        return self.woo_helper.put(f'orders/{order_id}', params=payload)

    def call_retrieve_an_order(self, order_id):
        return self.woo_helper.get(f"orders/{order_id}")