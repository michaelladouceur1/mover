import requests, json, os, pprint, sys
import threading
import datetime as dt
from tdameritrade import TDClient
from tdameritrade.auth import refresh_token

# URLS
BASE_URL = 'https://paper-api.alpaca.markets'
ACCOUNT_URL = f'{BASE_URL}/v2/account'
ORDER_URL = f'{BASE_URL}/v2/orders'
POSITION_URL = f'{BASE_URL}/v2/positions'

# KEYS
API_KEY = os.environ.get('ALP_API_KEY')
SECRET_KEY = os.environ.get('ALP_SECRET_KEY')

# HEADERS
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': SECRET_KEY}

class TDAPI:
    def __init__(self):
        self.ACCOUNT_ID = self._get_account_id()
        self.REFRESH_TOKEN = self._get_refresh_token()
        self.API_KEY = self._get_api_key()
        self.ACCESS_TOKEN = refresh_token(self.REFRESH_TOKEN,self.API_KEY)['access_token']
        self.client = TDClient(access_token=self.ACCESS_TOKEN)

    def _get_account_id(self):
        return os.environ.get('TD_BROKER_ID')

    def _get_refresh_token(self):
        return os.environ.get('TD_REFRESH_TOKEN')

    def _get_api_key(self):
        return os.environ.get('TD_API_KEY')

    def get_movers(self, index, direction='up', change_type='percent'):
        return self.client.movers(index, direction, change_type)

class Account:
    def __init__(self, refresh_rate=5, entry_time=[8,30]):
        # Account data
        self.account = self.account()
        self.account_number = self.account_number()
        self.buying_power = self.buying_power()
        self.equity = self.equity()

        # Trade parameters
        self.entry_time = dt.time(*entry_time)
        self.max_cap_perc = 0.2
        self.max_cap_alloc = self.buying_power*self.max_cap_perc
        self.profit_limit = 0.02
        self.loss_limit = 0.01

        # TDA Client
        self.tda = TDAPI()
        self.indexes = ['$COMPX', '$SPX.X']

        # Timer settings
        self._timer = threading.Event()
        self.ref_rate = refresh_rate
        # self.timer(_timer=self._timer, ref_rate=self.ref_rate)

    # CHANGE TO DECORATOR #
    def timer(self, _timer, ref_rate):
        if not _timer.is_set():
            print('TIMED')
            threading.Timer(ref_rate, self.timer, [_timer, ref_rate]).start()
            self.run()
    
    def account(self):
        r = requests.get(ACCOUNT_URL, headers=HEADERS)
        return json.loads(r.content)

    def account_number(self):
        return self.account['account_number']

    def buying_power(self):
        return float(self.account['buying_power'])

    def equity(self):
        return float(self.account['equity'])

    def order(self, symbol, qty, side, type, time_in_force, limit_price):
        data = {
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': type,
            'time_in_force': time_in_force,
            'limit_price': limit_price
        }

        r = requests.post(ORDER_URL, json=data, headers=HEADERS)

        return json.loads(r.content)

    def _confirm_entry(func):
        def inner(self):
            time = dt.datetime.now().time()
            if time > self.entry_time:
                return func(self)
        return inner

    @_confirm_entry
    def run(self):
        print('RUN')

    def strategy(self):
        movers = []
        for idx in self.indexes:
            movers.extend(self.tda.get_movers(idx))

        movers = sorted(movers, key=lambda k: k['change'], reverse=True)

        for i in movers:
            sym = i['symbol']
            target_price = i['last']
            if target_price < self.buying_power:
                qty = round(self.max_cap_alloc/target_price)
                self.order(sym,qty,'buy','limit','day',target_price)
            


acc = Account()
print(acc.max_cap_alloc)
# print(acc.account)
# print(acc.account_number)
# print(acc.buying_power)
# print(acc.equity)
# print('\n\n')
# tda = TDAPI()
# print(tda.get_movers('$COMPX'))