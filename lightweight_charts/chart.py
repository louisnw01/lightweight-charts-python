import asyncio
import webview
import multiprocessing as mp

from lightweight_charts.js import LWC, CALLBACK_SCRIPT, TopBar


class CallbackAPI:
    def __init__(self, emit): self.emit = emit

    def callback(self, message: str):
        messages = message.split('__')
        name, chart_id = messages[:2]
        args = messages[2:]
        self.emit.put((name, chart_id, *args))


class PyWV:
    def __init__(self, q, exit, loaded, html, width, height, x, y, on_top, debug, emit):
        self.queue = q
        self.exit = exit
        self.loaded = loaded
        self.debug = debug
        js_api = CallbackAPI(emit)
        self.webview = webview.create_window('', html=html, on_top=on_top, js_api=js_api, width=width, height=height,
                                             x=x, y=y, background_color='#000000')
        self.webview.events.loaded += self.on_js_load
        self.loop()

    def loop(self):
        while 1:
            arg = self.queue.get()
            if arg in ('start', 'show', 'hide', 'exit'):
                webview.start(debug=self.debug) if arg == 'start' else getattr(self.webview, arg)()
                self.exit.set() if arg in ('start', 'exit') else None
            else:
                try:
                    self.webview.evaluate_js(arg)
                except KeyError:
                    return

    def on_js_load(self):
        self.loaded.set(), self.loop()


class Chart(LWC):
    def __init__(self, volume_enabled: bool = True, width: int = 800, height: int = 600, x: int = None, y: int = None,
                 on_top: bool = False, debug: bool = False, api: object = None, topbar: bool = False, searchbox: bool = False,
                 inner_width: float = 1.0, inner_height: float = 1.0, dynamic_loading: bool = False):
        super().__init__(volume_enabled, inner_width, inner_height, dynamic_loading)
        self._emit = mp.Queue()
        self._q = mp.Queue()
        self._script_func = self._q.put
        self._exit = mp.Event()
        self._loaded = mp.Event()
        self._process = mp.Process(target=PyWV, args=(self._q, self._exit, self._loaded, self._html,
                                                      width, height, x, y, on_top, debug, self._emit), daemon=True)
        self._process.start()
        self._create_chart()

        self.api = api
        self._js_api_code = 'pywebview.api.callback'
        if not topbar and not searchbox:
            return
        self.run_script(CALLBACK_SCRIPT)
        self.topbar = TopBar(self) if topbar else None
        self._make_search_box() if searchbox else None

    def show(self, block: bool = False):
        """
        Shows the chart window.\n
        :param block: blocks execution until the chart is closed.
        """
        if not self.loaded:
            self._q.put('start')
            self._loaded.wait()
            self._on_js_load()
        else:
            self._q.put('show')
        if block:
            try:
                self._exit.wait()
            except KeyboardInterrupt:
                return
            self._exit.clear()

    async def show_async(self, block=False):
        if not self.loaded:
            self._q.put('start')
            self._loaded.wait()
            self._on_js_load()
        else:
            self._q.put('show')
        if block:
            try:
                while 1:
                    while self._emit.empty() and not self._exit.is_set():
                        await asyncio.sleep(0.1)
                    if self._exit.is_set():
                        return
                    key, chart_id, arg = self._emit.get()
                    self.api.chart = self._charts[chart_id]
                    if widget := self.api.chart.topbar._widget_with_method(key):
                        widget.value = arg
                        await getattr(self.api, key)()
                    else:
                        await getattr(self.api, key)(arg)
            except KeyboardInterrupt:
                return
        asyncio.create_task(self.show_async(block=True))

    def hide(self):
        """
        Hides the chart window.\n
        """
        self._q.put('hide')

    def exit(self):
        """
        Exits and destroys the chart window.\n
        """
        self._q.put('exit')
        self._exit.wait()
        self._process.terminate()
        del self

