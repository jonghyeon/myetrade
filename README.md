etrade
======

This is root directory for personal trading system

contents of configuration file : config.py
* etrade_consumer_key : from E*TRADE
* etrade_consumer_secret : from E*TRADE
* etrade_username : E*TRADE web access username
* etrade_passwd : E*TRADE web access password

Target Implementation :
* two or three simple trading algorithms
* maintain ticker list through JSON or XML

JSON format : <br/>
{\
  "accounts": [\
    {\
      "cash_to_trade": 1000000055.98,\
      "id": "account_number",\
      "net_value": 100000000000000,\
      "stocks": [\
        {\
          "count": 260000000000,\
          "last_sell_price": 0.0,\
          "net_purchase_share": 0.5,\
          "symbol": "AAPL",\
          "value": 4971.98\
        },\
        {\
          "count": 0,\
          "last_sell_price": 0.0,\
          "net_purchase_share": 0.5,\
          "symbol": "MSFT",\
          "value": 101.5\
        }\
      ]\
    }\
]\
}\
