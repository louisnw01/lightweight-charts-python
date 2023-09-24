import asyncio
import logging
import datetime as dt
import re
import json
import urllib.request
from typing import Literal, Union, List
import pandas as pd

from .chart import Chart

try:
    import websockets
except ImportError:
    websockets = None

SEC_TYPE = Literal['stocks', 'options', 'indices', 'forex', 'crypto']

ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s | [polygon.io] %(levelname)s: %(message)s', datefmt='%H:%M:%S'))
ch.setLevel(logging.DEBUG)
_log = logging.getLogger('polygon')
_log.setLevel(logging.ERROR)
_log.addHandler(ch)

api_key = ''
_tickers = {}
_set_on_load = []

_lasts = {}
_ws = {'stocks': None, 'options': None, 'indices': None, 'crypto': None, 'forex': None}
_subscription_type = {
    'stocks': ('Q', 'A'),
    'options': ('Q', 'A'),
    'indices': ('V', None),
    'forex': ('C', 'CA'),
    'crypto': ('XQ', 'XA'),
}


def _convert_timeframe(timeframe):
    spans = {
        'min': 'minute',
        'H': 'hour',
        'D': 'day',
        'W': 'week',
        'M': 'month',
    }
    try:
        multiplier = re.findall(r'\d+', timeframe)[0]
    except IndexError:
        return 1, spans[timeframe]
    timespan = spans[timeframe.replace(multiplier, '')]
    return multiplier, timespan


def _get_sec_type(ticker):
    if '/' in ticker:
        return 'forex'
    for prefix, security_type in zip(('O:', 'I:', 'C:', 'X:'), ('options', 'indices', 'forex', 'crypto')):
        if ticker.startswith(prefix):
            return security_type
    else:
        return 'stocks'


def _polygon_request(query_url):
    query_url = 'https://api.polygon.io'+query_url
    query_url += f'&apiKey={api_key}'

    request = urllib.request.Request(query_url, headers={'User-Agent': 'lightweight_charts/1.0'})
    with urllib.request.urlopen(request) as response:
        if response.status != 200:
            error = response.json()
            _log.error(f'({response.status}) Request failed: {error["error"]}')
            return
        data = json.loads(response.read())
        if 'results' not in data:
            _log.error(f'No results for {query_url}')
            return
        return data['results']


def get_bar_data(ticker: str, timeframe: str, start_date: str, end_date: str, limit: int = 5_000):
    end_date = dt.datetime.now().strftime('%Y-%m-%d') if end_date == 'now' else end_date
    mult, span = _convert_timeframe(timeframe)
    if '-' in ticker:
        ticker = ticker.replace('-', '')

    query_url = f"/v2/aggs/ticker/{ticker}/range/{mult}/{span}/{start_date}/{end_date}?limit={limit}"
    results = _polygon_request(query_url)
    if not results:
        return None

    df = pd.DataFrame(results)
    df['t'] = pd.to_datetime(df['t'], unit='ms')

    rename = {'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 't': 'time'}
    if not ticker.startswith('I:'):
        rename['v'] = 'volume'

    return df[rename.keys()].rename(columns=rename)


async def async_get_bar_data(ticker: str, timeframe: str, start_date: str, end_date: str, limit: int = 5_000):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_bar_data, ticker, timeframe, start_date, end_date, limit)


async def _send(sec_type: SEC_TYPE, action: str, params: str):
    ws = _ws[sec_type]
    while ws is None:
        await asyncio.sleep(0.05)
        ws = _ws[sec_type]
    await ws.send(json.dumps({'action': action, 'params': params}))


async def subscribe(ticker: str, sec_type: SEC_TYPE, func, args, precision=2):
    if not _ws[sec_type]:
        asyncio.create_task(_websocket_connect(sec_type))

    if sec_type in ('forex', 'crypto'):
        key = ticker[ticker.index(':')+1:]
        key = key.replace('-', '/') if sec_type == 'forex' else key
    else:
        key = ticker

    if not _lasts.get(key):
        _lasts[key] = {
            'price': 0,
            'funcs': [],
            'precision': precision
        }
        if sec_type != 'indices':
            _lasts[key]['volume'] = 0

    data = _lasts[key]

    quotes, aggs = _subscription_type[sec_type]
    await _send(sec_type, 'subscribe', f'{quotes}.{ticker}')
    await _send(sec_type, 'subscribe', f'{aggs}.{ticker}') if aggs else None

    if func in data['funcs']:
        return
    data['funcs'].append((func, args))


async def unsubscribe(func):
    for key, data in _lasts.items():
        if val := next(((f, args) for f, args in data['funcs'] if f == func), None):
            break
    else:
        return
    data['funcs'].remove(val)

    if data['funcs']:
        return
    sec_type = _get_sec_type(key)
    quotes, aggs = _subscription_type[sec_type]
    await _send(sec_type, 'unsubscribe', f'{quotes}.{key}')
    await _send(sec_type, 'unsubscribe', f'{aggs}.{key}')


async def _websocket_connect(sec_type):
    if websockets is None:
        raise ImportError('The "websockets" library was not found, and must be installed to pull live data.')
    ticker_key = {
        'stocks': 'sym',
        'options': 'sym',
        'indices': 'T',
        'forex': 'p',
        'crypto': 'pair',
    }[sec_type]
    async with websockets.connect(f'wss://socket.polygon.io/{sec_type}') as ws:
        _ws[sec_type] = ws
        await _send(sec_type, 'auth', api_key)
        while 1:
            response = await ws.recv()
            data_list: List[dict] = json.loads(response)
            for i, data in enumerate(data_list):
                if data['ev'] == 'status':
                    _log.info(f'{data["message"]}')
                    continue
                _ticker_key = {
                    'stocks': 'sym',
                    'options': 'sym',
                    'indices': 'T',
                    'forex': 'p',
                    'crypto': 'pair',
                }
                await _handle_tick(data[ticker_key], data)


async def _handle_tick(ticker, data):
    lasts = _lasts[ticker]
    sec_type = _get_sec_type(ticker)

    if data['ev'] in ('Q', 'V', 'C', 'XQ'):
        if sec_type == 'forex':
            data['bp'] = data.pop('b')
            data['ap'] = data.pop('a')
        price = (data['bp'] + data['ap']) / 2 if sec_type != 'indices' else data['val']
        if abs(price - lasts['price']) < (1/(10**lasts['precision'])):
            return
        lasts['price'] = price

        if sec_type != 'indices':
            lasts['volume'] = 0

        if 't' not in data:
            lasts['time'] = pd.to_datetime(data.pop('s'), unit='ms')
        else:
            lasts['time'] = pd.to_datetime(data['t'], unit='ms')

    elif data['ev'] in ('A', 'CA', 'XA'):
        lasts['volume'] = data['v']
        if not lasts.get('time'):
            return
    lasts['symbol'] = ticker
    for func, args in lasts['funcs']:
        func(pd.Series(lasts), *args)


class PolygonAPI:
    """
    Offers direct access to Polygon API data within all Chart objects.

    It is not designed to be initialized by the user, and should be utilised
    through the `polygon` method of `AbstractChart` (chart.polygon.<method>).
    """
    _set_on_load = []

    def __init__(self, chart):
        self._chart = chart

    def set(self, *args):
        if asyncio.get_event_loop().is_running():
            asyncio.create_task(self.async_set(*args))
            return True
        else:
            _set_on_load.append(args)
            return False

    async def async_set(self, sec_type: Literal['stocks', 'options', 'indices', 'forex', 'crypto'], ticker, timeframe,
                        start_date, end_date, limit, live):
        await unsubscribe(self._chart.update_from_tick)

        df = await async_get_bar_data(ticker, timeframe, start_date, end_date, limit)

        self._chart.set(df, render_drawings=_tickers.get(self._chart) == ticker)
        _tickers[self._chart] = ticker

        if not live:
            return True
        await subscribe(ticker, sec_type, self._chart.update_from_tick, (True,), self._chart.num_decimals)
        return True

    def stock(
            self, symbol: str, timeframe: str, start_date: str, end_date='now',
            limit: int = 5_000, live: bool = False
    ) -> bool:
        """
        Requests and displays stock data pulled from Polygon.io.\n
        :param symbol:      Ticker to request.
        :param timeframe:   Timeframe to request (1min, 5min, 2H, 1D, 1W, 2M, etc).
        :param start_date:  Start date of the data (YYYY-MM-DD).
        :param end_date:    End date of the data (YYYY-MM-DD). If left blank, this will be set to today.
        :param limit:       The limit of base aggregates queried to create the timeframe given (max 50_000).
        :param live:        If true, the data will be updated in real-time.
        """
        return self.set('stocks', symbol, timeframe, start_date, end_date, limit, live)

    def option(
            self, symbol: str, timeframe: str, start_date: str, expiration: str = None,
            right: Literal['C', 'P'] = None, strike: Union[int, float] = None,
            end_date: str = 'now', limit: int = 5_000, live: bool = False
    ) -> bool:
        """
        Requests and displays option data pulled from Polygon.io.\n
        :param symbol:      The underlying ticker to request.
        A formatted option ticker can also be given instead of using the expiration, right, and strike parameters.
        :param timeframe:   Timeframe to request (1min, 5min, 2H, 1D, 1W, 2M, etc).
        :param start_date:  Start date of the data (YYYY-MM-DD).
        :param expiration:  Expiration of the option (YYYY-MM-DD).
        :param right:       Right of the option (C, P).
        :param strike:      The strike price of the option.
        :param end_date:    End date of the data (YYYY-MM-DD). If left blank, this will be set to today.
        :param limit:       The limit of base aggregates queried to create the timeframe given (max 50_000).
        :param live:        If true, the data will be updated in real-time.
        """
        if any((expiration, right, strike)):
            expiration = dt.datetime.strptime(expiration, "%Y-%m-%d").strftime("%y%m%d")
            symbol = f'{symbol}{expiration}{right}{strike * 1000:08d}'
        return self.set('options', f'O:{symbol}', timeframe, start_date, end_date, limit, live)

    def index(
            self, symbol: str, timeframe: str, start_date: str, end_date: str = 'now',
            limit: int = 5_000, live: bool = False
    ) -> bool:
        """
        Requests and displays index data pulled from Polygon.io.\n
        :param symbol:      Ticker to request.
        :param timeframe:   Timeframe to request (1min, 5min, 2H, 1D, 1W, 2M, etc).
        :param start_date:  Start date of the data (YYYY-MM-DD).
        :param end_date:    End date of the data (YYYY-MM-DD). If left blank, this will be set to today.
        :param limit:       The limit of base aggregates queried to create the timeframe given (max 50_000).
        :param live:        If true, the data will be updated in real-time.
        """
        return self.set('indices', f'I:{symbol}', timeframe, start_date, end_date, limit, live)

    def forex(
            self, fiat_pair: str, timeframe: str, start_date: str, end_date: str = 'now',
            limit: int = 5_000, live: bool = False
    ) -> bool:
        """
        Requests and displays forex data pulled from Polygon.io.\n
        :param fiat_pair:   The fiat pair to request. (USD-CAD, GBP-JPY etc.)
        :param timeframe:   Timeframe to request (1min, 5min, 2H, 1D, 1W, 2M, etc).
        :param start_date:  Start date of the data (YYYY-MM-DD).
        :param end_date:    End date of the data (YYYY-MM-DD). If left blank, this will be set to today.
        :param limit:       The limit of base aggregates queried to create the timeframe given (max 50_000).
        :param live:        If true, the data will be updated in real-time.
        """
        return self.set('forex', f'C:{fiat_pair}', timeframe, start_date, end_date, limit, live)

    def crypto(
            self, crypto_pair: str, timeframe: str, start_date: str, end_date: str = 'now',
            limit: int = 5_000, live: bool = False
    ) -> bool:
        """
        Requests and displays crypto data pulled from Polygon.io.\n
        :param crypto_pair: The crypto pair to request. (BTC-USD, ETH-BTC etc.)
        :param timeframe:   Timeframe to request (1min, 5min, 2H, 1D, 1W, 2M, etc).
        :param start_date:  Start date of the data (YYYY-MM-DD).
        :param end_date:    End date of the data (YYYY-MM-DD). If left blank, this will be set to today.
        :param limit:       The limit of base aggregates queried to create the timeframe given (max 50_000).
        :param live:        If true, the data will be updated in real-time.
        """
        return self.set('crypto', f'X:{crypto_pair}', timeframe, start_date, end_date, limit, live)

    async def async_stock(
            self, symbol: str, timeframe: str, start_date: str, end_date: str = 'now',
            limit: int = 5_000, live: bool = False
    ) -> bool:
        return await self.async_set('stocks', symbol, timeframe, start_date, end_date, limit, live)

    async def async_option(
            self, symbol: str, timeframe: str, start_date: str, expiration: str = None,
            right: Literal['C', 'P'] = None, strike: Union[int, float] = None,
            end_date: str = 'now', limit: int = 5_000, live: bool = False
    ) -> bool:
        if any((expiration, right, strike)):
            expiration = dt.datetime.strptime(expiration, "%Y-%m-%d").strftime("%y%m%d")
            symbol = f'{symbol}{expiration}{right}{strike * 1000:08d}'
        return await self.async_set('options', f'O:{symbol}', timeframe, start_date, end_date, limit, live)

    async def async_index(
            self, symbol: str, timeframe: str, start_date: str, end_date: str = 'now',
            limit: int = 5_000, live: bool = False
    ) -> bool:
        return await self.async_set('indices', f'I:{symbol}', timeframe, start_date, end_date, limit, live)

    async def async_forex(
            self, fiat_pair: str, timeframe: str, start_date: str, end_date: str = 'now',
            limit: int = 5_000, live: bool = False
    ) -> bool:
        return await self.async_set('forex', f'C:{fiat_pair}', timeframe, start_date, end_date, limit, live)

    async def async_crypto(
            self, crypto_pair: str, timeframe: str, start_date: str, end_date: str = 'now',
            limit: int = 5_000, live: bool = False
    ) -> bool:
        return await self.async_set('crypto', f'X:{crypto_pair}', timeframe, start_date, end_date, limit, live)

    @staticmethod
    def log(info: bool):
        """
        Streams informational messages related to Polygon.io.
        """
        _log.setLevel(logging.INFO) if info else _log.setLevel(logging.ERROR)

    @staticmethod
    def api_key(key: str):
        """
        Sets the API key to be used with Polygon.io.
        """
        global api_key
        api_key = key


class PolygonChart(Chart):
    """
    A prebuilt callback chart object allowing for a standalone, plug-and-play
    experience of Polygon.io's API.

    Tickers, security types and timeframes are to be defined within the chart window.

    If using the standard `show` method, the `block` parameter must be set to True.
    When using `show_async`, either is acceptable.
    """
    def __init__(
            self, api_key: str, live: bool = False, num_bars: int = 200, end_date: str = 'now', limit: int = 5_000,
            timeframe_options: tuple = ('1min', '5min', '30min', 'D', 'W'),
            security_options: tuple = ('Stock', 'Option', 'Index', 'Forex', 'Crypto'),
            toolbox: bool = True, width: int = 800, height: int = 600, x: int = None, y: int = None,
            on_top: bool = False, maximize: bool = False, debug: bool = False
    ):
        super().__init__(width, height, x, y, on_top, maximize, debug, toolbox)

        self.num_bars = num_bars
        self.end_date = end_date
        self.limit = limit
        self.live = live
        self.win.style(
            active_background_color='rgba(91, 98, 246, 0.8)',
            muted_background_color='rgba(91, 98, 246, 0.5)'
        )
        self.polygon.api_key(api_key)
        self.events.search += self.on_search
        self.legend(True)
        self.grid(False, False)
        self.crosshair(vert_visible=False, horz_visible=False)

        self.topbar.textbox('symbol')
        self.topbar.switcher('timeframe', timeframe_options, func=self._on_timeframe_selection)
        self.topbar.switcher('security', security_options, func=self._on_security_selection)

        self.run_script(f'''
        {self.id}.search.window.style.display = "flex"
        {self.id}.search.box.focus()
        ''')

    async def _polygon(self, symbol):
        self.spinner(True)
        self.set(pd.DataFrame(), True)
        self.crosshair(vert_visible=False, horz_visible=False)

        mult, span = _convert_timeframe(self.topbar['timeframe'].value)
        delta = dt.timedelta(**{span + 's': int(mult)})
        short_delta = (delta < dt.timedelta(days=7))
        start_date = dt.datetime.now() if self.end_date == 'now' else dt.datetime.strptime(self.end_date, '%Y-%m-%d')
        remaining_bars = self.num_bars
        while remaining_bars > 0:
            start_date -= delta
            if start_date.weekday() > 4 and short_delta:  # Monday to Friday (0 to 4)
                continue
            remaining_bars -= 1
        epoch = dt.datetime.fromtimestamp(0)
        start_date = epoch if start_date < epoch else start_date
        success = await getattr(self.polygon, 'async_'+self.topbar['security'].value.lower())(
            symbol,
            timeframe=self.topbar['timeframe'].value,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=self.end_date,
            limit=self.limit,
            live=self.live
        )
        self.spinner(False)
        self.crosshair() if success else None
        return success

    async def on_search(self, chart, searched_string):
        chart.topbar['symbol'].set(searched_string if await self._polygon(searched_string) else '')

    async def _on_timeframe_selection(self, chart):
        await self._polygon(chart.topbar['symbol'].value) if chart.topbar['symbol'].value else None

    async def _on_security_selection(self, chart):
        self.precision(5 if chart.topbar['security'].value == 'Forex' else 2)
