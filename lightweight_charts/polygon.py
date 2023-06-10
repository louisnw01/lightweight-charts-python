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
    def __init__(self, chart):
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s | [polygon.io] %(levelname)s: %(message)s', datefmt='%H:%M:%S'))
        ch.setLevel(logging.DEBUG)
        self._log = logging.getLogger('polygon')
        self._log.setLevel(logging.ERROR)
        self._log.addHandler(ch)

        self._chart = chart
        self._lasts = {}  # $$
        self._key = None
        self._using_live_data = False
        self._using_live = {'stocks': False, 'options': False, 'indices': False, 'crypto': False, 'forex': False}
        self._ws = {'stocks': None, 'options': None, 'indices': None, 'crypto': None, 'forex': None}
        self._send_q = queue.Queue()
        self._q = queue.Queue()
        self._lock = threading.Lock()

    def _subchart(self, subchart):
        return PolygonAPISubChart(self, subchart)

    def log(self, info: bool):
        self._log.setLevel(logging.INFO) if info else self._log.setLevel(logging.ERROR)

    def api_key(self, key: str): self._key = key

    def stock(self, symbol: str, timeframe: str, start_date: str, end_date='now', limit: int = 5_000, live: bool = False):
        """
        Requests and displays stock data pulled from Polygon.io.\n
        :param symbol:      Ticker to request.
        :param timeframe:   Timeframe to request (1min, 5min, 2H, 1D, 1W, 2M, etc).
        :param start_date:  Start date of the data (YYYY-MM-DD).
        :param end_date:    End date of the data (YYYY-MM-DD). If left blank, this will be set to today.
        :param limit:       The limit of base aggregates queried to create the timeframe given (max 50_000)
        :param live:        If true, the data will be updated in real-time.
        """
        return True if self._set(self._chart, 'stocks', symbol, timeframe, start_date, end_date, limit, live) else False

    def option(self, symbol: str, timeframe: str, start_date: str, expiration: str = None, right: Literal['C', 'P'] = None, strike: Union[int, float] = None,
                end_date: str = 'now', limit: int = 5_000, live: bool = False):
        if any((expiration, right, strike)):
            symbol = f'O:{symbol}{dt.datetime.strptime(expiration, "%Y-%m-%d").strftime("%y%m%d")}{right}{strike * 1000:08d}'
        return True if self._set(self._chart, 'options', symbol, timeframe, start_date, end_date, limit, live) else False

    def index(self, symbol, timeframe, start_date, end_date='now', limit: int = 5_000, live=False):
        return True if self._set(self._chart, 'indices', f'I:{symbol}', timeframe, start_date, end_date, limit, live) else False

    def forex(self, fiat_pair, timeframe, start_date, end_date='now', limit: int = 5_000, live=False):
        return True if self._set(self._chart, 'forex', f'C:{fiat_pair}', timeframe, start_date, end_date, limit, live) else False

    def crypto(self, crypto_pair, timeframe, start_date, end_date='now', limit: int = 5_000, live=False):
        return True if self._set(self._chart, 'crypto', f'X:{crypto_pair}', timeframe, start_date, end_date, limit, live) else False

    def _set(self, chart, sec_type, ticker, timeframe, start_date, end_date, limit, live):
        if requests is None:
            raise ImportError('The "requests" library was not found, and must be installed to use polygon.io.')

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

        for child in self._lasts.values():
            for subbed_chart in child['charts']:
                if subbed_chart == chart:
                    self._send_q.put(('_unsubscribe', chart, ticker))

        df = pd.DataFrame(data['results'])
        columns = ['t', 'o', 'h', 'l', 'c']
        rename = {'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 't': 'time'}
        if sec_type != 'indices':
            rename['v'] = 'volume'
            columns.append('v')
        df = df[columns].rename(columns=rename)
        df['time'] = pd.to_datetime(df['time'], unit='ms')

        chart.set(df)
        if not live:
            return True

        if not self._using_live_data:
            threading.Thread(target=asyncio.run, args=[self._thread_loop()], daemon=True).start()
            self._using_live_data = True
        with self._lock:
            if not self._ws[sec_type]:
                self._send_q.put(('_websocket_connect', self._key, sec_type))
        self._send_q.put(('_subscribe', chart, sec_type, ticker))
        return True

    async def _thread_loop(self):
        while 1:
            while self._send_q.empty():
                await asyncio.sleep(0.05)
            value = self._send_q.get()
            func, args = value[0], value[1:]
            asyncio.create_task(getattr(self, func)(*args))

    def unsubscribe(self, symbol):
        self._send_q.put(('_unsubscribe', self._chart, symbol))

    async def _subscribe(self, chart, sec_type, ticker):
        key = ticker if '.' not in ticker else ticker.split('.')[1]
        key = key if ':' not in key else key.split(':')[1]
        if not self._lasts.get(key):
            sub_type = {
                'stocks': ('Q', 'A'),
                'options': ('Q', 'A'),
                'indices': ('V', None),
                'forex': ('C', 'CA'),
                'crypto': ('XQ', 'XA'),
            }
            self._lasts[key] = {
                'sec_type': sec_type,
                'sub_type': sub_type[sec_type],
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

    async def _unsubscribe(self, chart, ticker):
        key = ticker if '.' not in ticker else ticker.split('.')[1]
        key = key if ':' not in key else key.split(':')[1]
        if chart in self._lasts[key]['charts']:
            self._lasts[key]['charts'].remove(chart)
        if self._lasts[key]['charts']:
            return
        while self._q.qsize():
            self._q.get()  # Flush the queue
        quotes, aggs = self._lasts[key]['sub_type']
        await self._send(self._lasts[key]['sec_type'], 'unsubscribe', f'{quotes}.{ticker}')
        await self._send(self._lasts[key]['sec_type'], 'unsubscribe', f'{aggs}.{ticker}')

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
        max_ticks = 20
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
                    elif data_list.index(data) < len(data_list)-max_ticks:
                        continue
                    await self._handle_tick(sec_type, data)


class PolygonAPISubChart(PolygonAPI):
    def __init__(self, polygon, subchart):
        super().__init__(subchart)
        self._set = polygon._set


class PolygonChart(Chart):
    def __init__(self, api_key: str, live: bool = False, num_bars: int = 200, limit: int = 5_000,
                 timeframe_options: tuple = ('1min', '5min', '30min', 'D', 'W'),
                 security_options: tuple = ('Stock', 'Option', 'Index', 'Forex', 'Crypto'),
                 width: int = 800, height: int = 600, x: int = None, y: int = None, on_top: bool = False, debug=False):
        super().__init__(volume_enabled=True, width=width, height=height, x=x, y=y, on_top=on_top, debug=debug,
                         api=self, topbar=True, searchbox=True)
        self.chart = self
        self.num_bars = num_bars
        self.limit = limit
        self.live = live
        self.polygon.api_key(api_key)

        self.topbar.active_background_color = 'rgb(91, 98, 246)'
        self.topbar.textbox('symbol')
        self.topbar.switcher('timeframe', self.on_timeframe_selection, *timeframe_options)
        self.topbar.switcher('security', self.on_security_selection, *security_options)
        self.legend(True)
        self.grid(False, False)
        self.crosshair(vert_visible=False, horz_visible=False)
        self.run_script(f'''
        {self.id}.search.box.style.backgroundColor = 'rgba(91, 98, 246, 0.5)'
        {self.id}.spinner.style.borderTop = '4px solid rgba(91, 98, 246, 0.8)'

        {self.id}.search.window.style.display = "block"
        {self.id}.search.box.focus()
        ''')

    def show(self):
        """
        Shows the PolygonChart window (this method will block).
        """
        asyncio.run(self.show_async(block=True))

    def _polygon(self, symbol):
        self.spinner(True)
        self.set(pd.DataFrame())
        self.crosshair(vert_visible=False, horz_visible=False)
        if self.topbar['symbol'].value and self.topbar['symbol'].value != symbol:
            self.polygon.unsubscribe(self.topbar['symbol'].value)

        mult, span = _convert_timeframe(self.topbar['timeframe'].value)
        delta = dt.timedelta(**{span + 's': int(mult)})
        short_delta = (delta < dt.timedelta(days=7))
        start_date = dt.datetime.now()
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
            limit=self.limit,
            live=self.live
        )
        self.spinner(False)
        self.crosshair(vert_visible=True, horz_visible=True) if success else None
        return True if success else False

    async def on_search(self, searched_string):
        self.topbar['symbol'].set(searched_string if self._polygon(searched_string) else '')

    async def on_timeframe_selection(self):
        self._polygon(self.topbar['symbol'].value)

    async def on_security_selection(self):
        sec_type = self.topbar['security'].value
        self.volume_enabled = False if sec_type == 'Index' else True

        precision = 5 if sec_type == 'Forex' else 2
        min_move = 1 / (10 ** precision)  # 2 -> 0.1, 5 -> 0.00005 etc.
        self.run_script(f'''
        {self.chart.id}.series.applyOptions({{
            priceFormat: {{precision: {precision}, minMove: {min_move}}}
        }})''')




