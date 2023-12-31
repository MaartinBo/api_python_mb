import logging as logger

import pytest

from mbtest.src.dao.customers_dao import CustomersDAO
from mbtest.src.helpers.customers_helper import CustomerHelper
from mbtest.src.utilities.genericUtilities import generate_random_email_and_password
from mbtest.src.utilities.requestsUtility import RequestsUtility


@pytest.mark.customers
@pytest.mark.C1
def test_create_customer_only_email_password():
    logger.info("TEST: Create new customer with only email and password")
    rand_info = generate_random_email_and_password()
    logger.info(rand_info)
    email = rand_info['email']
    password = rand_info['password']

    # make the call
    cust_obj = CustomerHelper()
    cust_api_info = cust_obj.create_customer(email=email, password=password)

    # verify email and first name in response
    assert cust_api_info['email'] == email, f"Create customer api return wrong email. Email: {email}"
    assert cust_api_info['first_name'] == '', ("Create customer api returned value for first name but is should be "
                                               "empty.")

    # verify customer is created in database
    cust_dao = CustomersDAO()
    cust_info = cust_dao.get_customer_by_email(email)

    id_in_api = cust_api_info['id']
    id_in_db = cust_info[0]['ID']
    assert id_in_api == id_in_db, "Create customer response 'id' not same as 'ID' in database." \
                                  f"Email: {email}"

@pytest.mark.customers
@pytest.mark.C3
def test_create_customer_fail_for_existing_email():
    # get existing email from db
    cust_dao = CustomersDAO()
    existing_cust = cust_dao.get_random_customer_from_db()
    existing_email = existing_cust[0]["user_email"]

    # call the api and validate status code
    req_helper = RequestsUtility()
    payload = {"email": existing_email, "password": "Password1"}
    cust_api_info = req_helper.post(endpoint='customers', payload=payload, expected_status_code=400)

    # validate code and message from response
    assert cust_api_info['code'] == 'registration-error-email-exists', f"Create customer with" \
                                                                       f"existing user error 'code' is not correct. Expected: 'registration-error-email-exists', " \
                                                                       f"Actual: {cust_api_info['code']}"

    expected_message = 'An account is already registered with your email address.'
    assert expected_message in cust_api_info['message'], \
        f"Expected message not found in API response: {cust_api_info['message']}"
