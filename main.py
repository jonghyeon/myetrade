#!/usr/bin/env python3

import logging
import json
from config import *
from python_etrade.client import Client
from python_etrade.stocks import Stock
from algorithms import AhnyungAlgorithm, FillAlgorithm
import algorithms

json_config_file = 'config.json'
LOG_FORMAT = '%(asctime)-15s %(message)s'


def load_json_account(json_account, account):
    account.mode = json_account['mode']


def store_json_account(json_account, account):
    json_account['mode'] = account.mode
    json_account['net_value'] = account.net_value
    json_account['cash_to_trade'] = account.cash_to_trade


def load_json_stock(json_stock, stock):
    stock.last_sell_price = json_stock['last_sell_price']
    stock.last_buy_price = json_stock['last_buy_price']
    stock.last_value = json_stock['last_value']
    stock.last_count = json_stock['last_count']
    stock.budget = stock.account.net_value * json_stock['trade_share']
    stock.algorithm_string = json_stock['algorithm']
    if json_stock['stance'] == 'moderate':
        stock.stance = algorithms.MODERATE
    elif json_stock['stance'] == 'aggressive':
        stock.stance = algorithms.AGGRESSIVE
    else:
        stock.stance = algorithms.CONSERVATIVE


def store_json_stock(json_stock, stock):
    json_stock['last_sell_price'] = stock.last_sell_price
    json_stock['last_buy_price'] = stock.last_buy_price
    json_stock['last_value'] = stock.last_value
    json_stock['last_count'] = stock.last_count
    json_stock['count'] = stock.count
    json_stock['value'] = stock.value


if __name__ == '__main__':
    logging.basicConfig(filename='etrade.log', format=LOG_FORMAT, level=logging.INFO)

    logging.debug('loading account and stock configuration file : ' + json_config_file)
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
    logging.debug('logged in')

    alg_ahnyung = AhnyungAlgorithm()
    alg_fill = FillAlgorithm()

    order_id = config['order_id']

    for json_account in config['accounts']:
        account = client.get_account(json_account['id'])
        load_json_account(json_account, account)

        for json_stock in json_account['stocks']:
            stock = account.get_stock(json_stock['symbol'])
            if not stock:
                quote = client.get_quote(json_stock['symbol'])
                stock = Stock(quote.symbol, account, account.session)
                stock.value = quote.ask
                stock.count = 0
                account.add_empty_stock(stock)

            load_json_stock(json_stock, stock)

            #execute main algorithms
            decision = 0
            if account.mode == 'setup':
                decision = alg_fill.trade_decision(stock)
            if account.mode == 'run':
                if stock.algorithm_string == 'ahnyung':
                    decision = alg_ahnyung.trade_decision(stock)

            #execute decision
            if decision != 0:
                stock.last_count = stock.count

            if decision > 0:
                stock.market_order(decision, order_id)
            elif decision < 0:
                stock.market_order(decision, order_id)

            if decision != 0:
                order_id += 1
                if account.mode == 'setup':
                    stock.last_buy_price = stock.value
                    stock.last_sell_price = stock.value

            store_json_stock(json_stock, stock)

        if account.mode == 'setup':
            account.mode = 'run'

        store_json_account(json_account, account)

    config['order_id'] = order_id

    with open(json_config_file, 'w') as outfile:
        json.dump(config, outfile, indent=2, sort_keys=False)

    result = client.logout()
    logging.debug('logged out')


