import pytest

from mbtest.src.dao.orders_dao import OrdersDAO
from mbtest.src.dao.products_dao import ProductsDAO
from mbtest.src.helpers.customers_helper import CustomerHelper
from mbtest.src.helpers.orders_helper import OrdersHelper


@pytest.fixture()
def my_orders_smoke_setup(scope='module'):
    product_dao = ProductsDAO()
    order_helper = OrdersHelper()
    rand_product = product_dao.get_random_product_from_db(1)
    product_id = rand_product[0]["ID"]
    info = {'product_id': product_id,
            'order_helper': order_helper}
    return info

@pytest.mark.smoke
@pytest.mark.orders
@pytest.mark.O1
def test_create_paid_order_guest_user(my_orders_smoke_setup):

    orders_dao = OrdersDAO()
    order_helper = my_orders_smoke_setup['order_helper']

    customer_id = 0
    product_id = my_orders_smoke_setup['product_id']
    # make the call
    info = {"line_items": [
        {
          "product_id": product_id,
          "quantity": 1
        }
      ]}

    order_json = order_helper.create_order(info)

    # verify response
    expected_products = [{'product_id': product_id}]
    order_helper.verify_order_is_created(order_json, customer_id, expected_products)

@pytest.mark.smoke
@pytest.mark.orders
@pytest.mark.O2
def test_create_paid_order_new_created_customer(my_orders_smoke_setup):
    # create helper objects
    order_helper = my_orders_smoke_setup['order_helper']
    customer_helper = CustomerHelper()

    # make the call
    cust_info = customer_helper.create_customer()
    customer_id = cust_info['id']
    product_id = my_orders_smoke_setup['product_id']
    info = {"line_items": [
        {
            "product_id": product_id,
            "quantity": 1
        }
    ],
    "customer_id": customer_id
    }

    order_json = order_helper.create_order(info)
    # verify response
    expected_products = [{'product_id': product_id}]
    order_helper.verify_order_is_created(order_json, customer_id, expected_products)