#!/usr/bin/env python3

import logging
import json
from python_etrade.client import Client
from config import *

json_config_file = 'config.json'


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    logging.info('loading account and stock configuration file : ' + json_config_file)
    with open(json_config_file) as f:
        config = json.load(f)

    logging.debug(config)

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

    account_list = []
    for json_account in config['accounts']:
        account = client.get_account(json_account['id'])
        account_list.append(account)

        json_account['net_value'] = account.net_value
        json_account['cash_to_trade'] = account.cash_to_trade

        for json_stock in json_account['stocks']:
            stock = account.get_stock(json_stock['symbol'])
            if stock:
                json_stock['value'] = stock.value
                json_stock['count'] = stock.count
            else:
                quote = client.get_quote(json_stock['symbol'])
                json_stock['value'] = quote.ask
                json_stock['count'] = 0

    with open(json_config_file, 'w') as outfile:
        json.dump(config, outfile, indent=2, sort_keys=True)

    logging.info('logging out')
    result = client.logout()


