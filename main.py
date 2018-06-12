#!/usr/bin/env python3

import logging
import json
from config import *
from python_etrade.client import Client
from python_etrade.stocks import Stock
from algorithms import AhnyungAlgorithm, FillAlgorithm
import algorithms

json_config_file = 'config.json'


if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)

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

    alg_ahnyung = AhnyungAlgorithm()
    alg_fill = FillAlgorithm()

    order_id = config['order_id']

    for json_account in config['accounts']:
        account = client.get_account(json_account['id'])
        account.mode = json_account['mode']

        json_account['net_value'] = account.net_value
        json_account['cash_to_trade'] = account.cash_to_trade

        for json_stock in json_account['stocks']:
            json_stock['last_value'] = json_stock['value']
            stock = account.get_stock(json_stock['symbol'])
            if stock:
                json_stock['value'] = stock.value
                json_stock['count'] = stock.count
            else:
                quote = client.get_quote(json_stock['symbol'])
                json_stock['value'] = quote.ask
                json_stock['count'] = 0
                stock = Stock(quote.symbol, account, account.session)
                stock.value = quote.ask
                stock.count = 0
                account.add_empty_stock(stock)
            stock.last_value = json_stock['last_value']
            stock.last_buy_price = json_stock['last_buy_price']
            stock.last_sell_price = json_stock['last_sell_price']
            stock.last_count = json_stock['last_count']
            stock.budget = account.net_value * json_stock['trade_share']
            stock.algorithm_string = json_stock['algorithm']
            if json_stock['stance'] == 'moderate':
                stock.stance = algorithms.MODERATE
            elif json_stock['stance'] == 'aggressive':
                stock.stance = algorithms.AGGRESSIVE
            else:
                stock.stance = algorithms.CONSERVATIVE

            #execute main algorithms
            decision = 0
            if account.mode == 'setup':
                decision = alg_fill.trade_decision(stock)
            if account.mode == 'run':
                if stock.algorithm_string == 'ahnyung':
                    decision = alg_ahnyung.trade_decision(stock)

            #execute decision
            if decision != 0:
                json_stock['last_count'] = stock.count

            if decision > 0:
                stock.order(decision, order_id)
                json_stock['last_buy_price'] = stock.value
            elif decision < 0:
                stock.order(decision, order_id)
                json_stock['last_sell_price'] = stock.value

            if decision != 0:
                order_id += 1
                json_stock['count'] = stock.count
                if json_account['mode'] == 'setup':
                    json_stock['last_buy_price'] = stock.value
                    json_stock['last_sell_price'] = stock.value

        if account.mode == 'setup':
            json_account['mode'] = 'run'

    config['order_id'] = order_id

    with open(json_config_file, 'w') as outfile:
        json.dump(config, outfile, indent=2, sort_keys=False)

    logging.info('logging out')
    result = client.logout()


