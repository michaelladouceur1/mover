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
    def __init__(self, refresh_rate=5, entry_time=[23,30]):
        # Account data
        self.account = self.account()

        # Position data
        self.positions = self.positions()

        # Order data
        self.orders = self.orders()

        # Trade parameters
        self.entry_time = dt.time(*entry_time)
        self.max_cap_perc = 0.2
        self.max_cap_alloc = self.buying_power*self.max_cap_perc
        self.profit_limit = 0.10
        self.loss_limit = -0.02

        # TDA Client
        self.tda = TDAPI()
        self.indexes = ['$COMPX', '$SPX.X']

        # Timer settings
        self._timer = threading.Event()
        self.ref_rate = refresh_rate
        # self.timer(_timer=self._timer, ref_rate=self.ref_rate)

    def log_trade(self, action, sym, qty, type, target_price=None):
        with open(f'{action}.txt', 'a') as f:
            f.write(f'{action}: ({sym}, {qty}, {type}, {target_price})')


    # CHANGE TO DECORATOR #
    def timer(self, _timer, ref_rate):
        if not _timer.is_set():
            print(f'Timer called at {dt.datetime.now().time()}')
            threading.Timer(ref_rate, self.timer, [_timer, ref_rate]).start()
            self.account = self.account()
            self.positions = self.positions()
            self.orders = self.orders()
            self.run()
    

    # Account functions
    def account(self):
        r = requests.get(ACCOUNT_URL, headers=HEADERS)
        return json.loads(r.content)

    @property
    def account_number(self):
        return self.account['account_number']

    @property
    def buying_power(self):
        return float(self.account['buying_power'])

    @property
    def equity(self):
        return float(self.account['equity'])


    # Position functions
    def positions(self):
        r = requests.get(POSITION_URL, headers=HEADERS)
        return json.loads(r.content)

    @property
    def position_symbols(self):
        syms = []
        for i in self.positions:
            syms.append(i['symbol'])
        return syms

    @property
    def position_asset_ids(self):
        ids = []
        for i in self.positions:
            ids.append(i['asset_id'])
        return ids


    # Order functions
    def orders(self):
        r = requests.get(ORDER_URL, headers=HEADERS)
        return json.loads(r.content)

    @property
    def order_asset_ids(self):
        ids = []
        for i in self.orders:
            ids.append(i['asset_id'])
        return ids


    def order(self, symbol, qty, side, type, time_in_force, limit_price=None):
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

        # Buy movers
        for i in movers:
            sym = i['symbol']
            target_price = i['last']
            if (target_price < self.buying_power) and (i not in self.position_symbols):
                qty = round(self.max_cap_alloc/target_price)
                self.order(sym,qty,'buy','limit','day',target_price)
                self.log_trade('buy',sym,qty,'limit',target_price)

        # Sell movers
        for i in self.positions:
            if float(i['unrealized_plpc']) < self.loss_limit:
                self.order(i['asset_id'],i['qty'],'sell','market','day')
                self.log_trade('sell',i['symbol'],i['qty'],'market')
            elif 
            


acc = Account()
print(acc.equity)

# tda = TDAPI()
# print(tda.get_movers('$COMPX'))