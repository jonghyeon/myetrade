#!/usr/bin/env python3

import logging
from python_etrade.client import Client
from config import *


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    client = Client()
    result = client.login(etrade_consumer_key,
                          etrade_consumer_secret,
                          etrade_username,
                          etrade_passwd)
    if not result:
        logging.error('login failed')
        exit(-1)
    logging.info('logged in')

    result = client.renew_connection()
    if not result:
        logging.error('renew failed')
        exit(-1)
    logging.info('renew success')

    result = client.logout()


