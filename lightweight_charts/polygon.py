import asyncio
import logging
import datetime as dt
import threading
import queue
import json
import ssl
from typing import Literal, Union, List
import pandas as pd

from lightweight_charts.util import _convert_timeframe
from lightweight_charts import Chart

try:
    import requests
except ImportError:
    requests = None
try:
    import websockets
except ImportError:
    websockets = None


class PolygonAPI:
    """
    Offers direct access to Polygon API data within all Chart objects.

    It is not designed to be initialized by the user, and should be utilised
    through the `polygon` method of `LWC` (chart.polygon.<method>).
    """
    def __init__(self, chart):
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s | [polygon.io] %(levelname)s: %(message)s', datefmt='%H:%M:%S'))
        ch.setLevel(logging.DEBUG)
        self._log = logging.getLogger('polygon')
        self._log.setLevel(logging.ERROR)
        self._log.addHandler(ch)

        self.max_ticks_per_response = 20

        self._chart = chart
        self._lasts = {}
        self._key = None

        self._ws_q = queue.Queue()
        self._q = queue.Queue()
        self._lock = threading.Lock()

        self._using_live_data = False
        self._using_live = {'stocks': False, 'options': False, 'indices': False, 'crypto': False, 'forex': False}
        self._ws = {'stocks': None, 'options': None, 'indices': None, 'crypto': None, 'forex': None}
        self._tickers = {}


    def log(self, info: bool):
        """
        Streams informational messages related to Polygon.io.
        """
        self._log.setLevel(logging.INFO) if info else self._log.setLevel(logging.ERROR)

    def api_key(self, key: str):
        """
        Sets the API key to be used with Polygon.io.
        """
        self._key = key

    def stock(self, symbol: str, timeframe: str, start_date: str, end_date='now', limit: int = 5_000, live: bool = False):
        """
        Requests and displays stock data pulled from Polygon.io.\n
        :param symbol:      Ticker to request.
        :param timeframe:   Timeframe to request (1min, 5min, 2H, 1D, 1W, 2M, etc).
        :param start_date:  Start date of the data (YYYY-MM-DD).
        :param end_date:    End date of the data (YYYY-MM-DD). If left blank, this will be set to today.
        :param limit:       The limit of base aggregates queried to create the timeframe given (max 50_000).
        :param live:        If true, the data will be updated in real-time.
        """
        return self._set(self._chart, 'stocks', symbol, timeframe, start_date, end_date, limit, live)

    def option(self, symbol: str, timeframe: str, start_date: str, expiration: str = None, right: Literal['C', 'P'] = None, strike: Union[int, float] = None,
                end_date: str = 'now', limit: int = 5_000, live: bool = False):
        """
        Requests and displays option data pulled from Polygon.io.\n
        :param symbol:      The underlying ticker to request. A formatted option ticker can also be given instead of using the expiration, right, and strike parameters.
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
            symbol = f'{symbol}{dt.datetime.strptime(expiration, "%Y-%m-%d").strftime("%y%m%d")}{right}{strike * 1000:08d}'
        return self._set(self._chart, 'options', f'O:{symbol}', timeframe, start_date, end_date, limit, live)

    def index(self, symbol, timeframe, start_date, end_date='now', limit: int = 5_000, live=False):
        """
        Requests and displays index data pulled from Polygon.io.\n
        :param symbol:      Ticker to request.
        :param timeframe:   Timeframe to request (1min, 5min, 2H, 1D, 1W, 2M, etc).
        :param start_date:  Start date of the data (YYYY-MM-DD).
        :param end_date:    End date of the data (YYYY-MM-DD). If left blank, this will be set to today.
        :param limit:       The limit of base aggregates queried to create the timeframe given (max 50_000).
        :param live:        If true, the data will be updated in real-time.
        """
        return self._set(self._chart, 'indices', f'I:{symbol}', timeframe, start_date, end_date, limit, live)

    def forex(self, fiat_pair, timeframe, start_date, end_date='now', limit: int = 5_000, live=False):
        """
        Requests and displays forex data pulled from Polygon.io.\n
        :param fiat_pair:   The fiat pair to request. (USD-CAD, GBP-JPY etc.)
        :param timeframe:   Timeframe to request (1min, 5min, 2H, 1D, 1W, 2M, etc).
        :param start_date:  Start date of the data (YYYY-MM-DD).
        :param end_date:    End date of the data (YYYY-MM-DD). If left blank, this will be set to today.
        :param limit:       The limit of base aggregates queried to create the timeframe given (max 50_000).
        :param live:        If true, the data will be updated in real-time.
        """
        return self._set(self._chart, 'forex', f'C:{fiat_pair}', timeframe, start_date, end_date, limit, live)

    def crypto(self, crypto_pair, timeframe, start_date, end_date='now', limit: int = 5_000, live=False):
        """
        Requests and displays crypto data pulled from Polygon.io.\n
        :param crypto_pair: The crypto pair to request. (BTC-USD, ETH-BTC etc.)
        :param timeframe:   Timeframe to request (1min, 5min, 2H, 1D, 1W, 2M, etc).
        :param start_date:  Start date of the data (YYYY-MM-DD).
        :param end_date:    End date of the data (YYYY-MM-DD). If left blank, this will be set to today.
        :param limit:       The limit of base aggregates queried to create the timeframe given (max 50_000).
        :param live:        If true, the data will be updated in real-time.
        """
        return self._set(self._chart, 'crypto', f'X:{crypto_pair}', timeframe, start_date, end_date, limit, live)

    def _set(self, chart, sec_type, ticker, timeframe, start_date, end_date, limit, live):
        if requests is None:
            raise ImportError('The "requests" library was not found, and must be installed to use polygon.io.')

        self._ws_q.put(('_unsubscribe', chart))
        end_date = dt.datetime.now().strftime('%Y-%m-%d') if end_date == 'now' else end_date
        mult, span = _convert_timeframe(timeframe)

        query_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker.replace('-', '')}/range/{mult}/{span}/{start_date}/{end_date}?limit={limit}&apiKey={self._key}"
        response = requests.get(query_url, headers={'User-Agent': 'lightweight_charts/1.0'})
        if response.status_code != 200:
            error = response.json()
            self._log.error(f'({response.status_code}) Request failed: {error["error"]}')
            return
        data = response.json()
        if 'results' not in data:
            self._log.error(f'No results for "{ticker}" ({sec_type})')
            return

        df = pd.DataFrame(data['results'])
        columns = ['t', 'o', 'h', 'l', 'c']
        rename = {'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 't': 'time'}
        if sec_type != 'indices':
            rename['v'] = 'volume'
            columns.append('v')
        df = df[columns].rename(columns=rename)
        df['time'] = pd.to_datetime(df['time'], unit='ms')

        chart.set(df, render_drawings=self._tickers.get(chart) == ticker)
        self._tickers[chart] = ticker

        if not live:
            return True
        if not self._using_live_data:
            threading.Thread(target=asyncio.run, args=[self._thread_loop()], daemon=True).start()
            self._using_live_data = True
        with self._lock:
            if not self._ws[sec_type]:
                self._ws_q.put(('_websocket_connect', self._key, sec_type))
        self._ws_q.put(('_subscribe', chart, ticker, sec_type))
        return True

    async def _thread_loop(self):
        while 1:
            while self._ws_q.empty():
                await asyncio.sleep(0.05)
            value = self._ws_q.get()
            func, args = value[0], value[1:]
            asyncio.create_task(getattr(self, func)(*args))

    async def _subscribe(self, chart, ticker, sec_type):
        key = ticker if ':' not in ticker else ticker.split(':')[1]
        if not self._lasts.get(key):
            self._lasts[key] = {
                'ticker': ticker,
                'sec_type': sec_type,
                'sub_type': {
                    'stocks': ('Q', 'A'),
                    'options': ('Q', 'A'),
                    'indices': ('V', None),
                    'forex': ('C', 'CA'),
                    'crypto': ('XQ', 'XA'),
                }[sec_type],
                'price': chart._last_bar['close'],
                'charts': [],
            }
        quotes, aggs = self._lasts[key]['sub_type']
        await self._send(self._lasts[key]['sec_type'], 'subscribe', f'{quotes}.{ticker}')
        await self._send(self._lasts[key]['sec_type'], 'subscribe', f'{aggs}.{ticker}') if aggs else None

        if sec_type != 'indices':
            self._lasts[key]['volume'] = chart._last_bar['volume']
        if chart in self._lasts[key]['charts']:
            return
        self._lasts[key]['charts'].append(chart)

    async def _unsubscribe(self, chart):
        for data in self._lasts.values():
            if chart in data['charts']:
                break
        else:
            return
        if chart in data['charts']:
            data['charts'].remove(chart)
        if data['charts']:
            return

        while self._q.qsize():
            self._q.get()  # Flush the queue
        quotes, aggs = data['sub_type']
        await self._send(data['sec_type'], 'unsubscribe', f'{quotes}.{data["ticker"]}')
        await self._send(data['sec_type'], 'unsubscribe', f'{aggs}.{data["ticker"]}')

    async def _send(self, sec_type, action, params):
        while 1:
            with self._lock:
                ws = self._ws[sec_type]
            if ws:
                break
            await asyncio.sleep(0.1)
        await ws.send(json.dumps({'action': action, 'params': params}))

    async def _handle_tick(self, sec_type, data):
        data['ticker_key'] = {
            'stocks': 'sym',
            'options': 'sym',
            'indices': 'T',
            'forex': 'p',
            'crypto': 'pair',
        }[sec_type]
        key = data[data['ticker_key']].replace('/', '-')
        if ':' in key:
            key = key[key.index(':')+1:]
        data['t'] = pd.to_datetime(data.pop('s'), unit='ms') if 't' not in data else pd.to_datetime(data['t'], unit='ms')

        if data['ev'] in ('Q', 'V', 'C', 'XQ'):
            self._lasts[key]['time'] = data['t']
            if sec_type == 'forex':
                data['bp'] = data.pop('b')
                data['ap'] = data.pop('a')
            self._lasts[key]['price'] = (data['bp']+data['ap'])/2 if sec_type != 'indices' else data['val']
            self._lasts[key]['volume'] = 0
        elif data['ev'] in ('A', 'CA', 'XA'):
            self._lasts[key]['volume'] = data['v']
            if not self._lasts[key].get('time'):
                return
        for chart in self._lasts[key]['charts']:
            self._q.put((chart.update_from_tick, pd.Series(self._lasts[key]), True))

    async def _websocket_connect(self, api_key, sec_type):
        if websockets is None:
            raise ImportError('The "websockets" library was not found, and must be installed to pull live data.')
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        async with websockets.connect(f'wss://socket.polygon.io/{sec_type}', ssl=ssl_context) as ws:
            with self._lock:
                self._ws[sec_type] = ws
            await self._send(sec_type, 'auth', api_key)
            while 1:
                response = await ws.recv()
                data_list: List[dict] = json.loads(response)
                for i, data in enumerate(data_list):
                    if data['ev'] == 'status':
                        self._log.info(f'{data["message"]}')
                        continue
                    elif data_list.index(data) < len(data_list)-self.max_ticks_per_response:
                        continue
                    await self._handle_tick(sec_type, data)

    def _subchart(self, subchart):
        return PolygonAPISubChart(self, subchart)


class PolygonAPISubChart(PolygonAPI):
    def __init__(self, polygon, subchart):
        super().__init__(subchart)
        self._set = polygon._set


class PolygonChart(Chart):
    """
    A prebuilt callback chart object allowing for a standalone and plug-and-play
    experience of Polygon.io's API.

    Tickers, security types and timeframes are to be defined within the chart window.

    If using the standard `show` method, the `block` parameter must be set to True.
    When using `show_async`, either is acceptable.
    """
    def __init__(self, api_key: str, live: bool = False, num_bars: int = 200, end_date: str = 'now', limit: int = 5_000,
                 timeframe_options: tuple = ('1min', '5min', '30min', 'D', 'W'),
                 security_options: tuple = ('Stock', 'Option', 'Index', 'Forex', 'Crypto'),
                 toolbox: bool = True, width: int = 800, height: int = 600, x: int = None, y: int = None,
                 on_top: bool = False, maximize: bool = False, debug: bool = False):
        super().__init__(volume_enabled=True, width=width, height=height, x=x, y=y, on_top=on_top, maximize=maximize, debug=debug,
                         api=self, topbar=True, searchbox=True, toolbox=toolbox)
        self.chart = self
        self.num_bars = num_bars
        self.end_date = end_date
        self.limit = limit
        self.live = live
        self.polygon.api_key(api_key)

        self.topbar.active_background_color = 'rgb(91, 98, 246)'
        self.topbar.textbox('symbol')
        self.topbar.switcher('timeframe', self._on_timeframe_selection, *timeframe_options)
        self.topbar.switcher('security', self._on_security_selection, *security_options)
        self.legend(True)
        self.grid(False, False)
        self.crosshair(vert_visible=False, horz_visible=False)
        self.run_script(f'''
        {self.id}.search.box.style.backgroundColor = 'rgba(91, 98, 246, 0.5)'
        {self.id}.spinner.style.borderTop = '4px solid rgba(91, 98, 246, 0.8)'

        {self.id}.search.window.style.display = "flex"
        {self.id}.search.box.focus()
        
        //let polyLogo = document.createElement('div')
        //polyLogo.innerHTML = '<svg><g transform="scale(0.9)"><path d="M17.9821362,6 L24,12.1195009 L22.9236698,13.5060353 L17.9524621,27 L14.9907916,17.5798557 L12,12.0454987 L17.9821362,6 Z M21.437,15.304 L18.3670383,19.1065035 L18.367,23.637 L21.437,15.304 Z M18.203,7.335 L15.763,17.462 L17.595,23.287 L17.5955435,18.8249858 L22.963,12.176 L18.203,7.335 Z M17.297,7.799 L12.9564162,12.1857947 L15.228,16.389 L17.297,7.799 Z" fill="#FFFFFF"></path></g></svg>'
        //polyLogo.style.position = 'absolute'
        //polyLogo.style.width = '28px'
        //polyLogo.style.zIndex = 10000
        //polyLogo.style.right = '18px'
        //polyLogo.style.top = '-1px'
        //{self.id}.wrapper.appendChild(polyLogo)
        ''')

    def _polygon(self, symbol):
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
        success = getattr(self.polygon, self.topbar['security'].value.lower())(
            symbol,
            timeframe=self.topbar['timeframe'].value,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=self.end_date,
            limit=self.limit,
            live=self.live
        )
        self.spinner(False)
        self.crosshair(vert_visible=True, horz_visible=True) if success else None
        return success

    async def on_search(self, searched_string): self.topbar['symbol'].set(searched_string if self._polygon(searched_string) else '')

    async def _on_timeframe_selection(self):
        self._polygon(self.topbar['symbol'].value) if self.topbar['symbol'].value else None

    async def _on_security_selection(self):
        sec_type = self.topbar['security'].value
        self.volume_enabled = False if sec_type == 'Index' else True

        precision = 5 if sec_type == 'Forex' else 2
        min_move = 1 / (10 ** precision)  # 2 -> 0.1, 5 -> 0.00005 etc.
        self.run_script(f'''
        {self.chart.id}.series.applyOptions({{
            priceFormat: {{precision: {precision}, minMove: {min_move}}}
        }})''')
