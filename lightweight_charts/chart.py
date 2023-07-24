import asyncio
import multiprocessing as mp
import webview

from lightweight_charts.abstract import LWC


class CallbackAPI:
    def __init__(self, emit_queue, return_queue):
        self.emit_q, self.return_q = emit_queue, return_queue

    def callback(self, message: str):
        messages = message.split('_~_')
        name, chart_id = messages[:2]
        args = messages[2:]
        self.return_q.put(*args) if name == 'return' else self.emit_q.put((name, chart_id, *args))


class PyWV:
    def __init__(self, q, exit, loaded, html, width, height, x, y, on_top, maximize, debug, emit_queue, return_queue):
        if maximize:
            width, height = webview.screens[0].width, webview.screens[0].height
        self.queue = q
        self.exit = exit
        self.loaded = loaded
        self.debug = debug
        js_api = CallbackAPI(emit_queue, return_queue)
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

    def on_js_load(self): self.loaded.set(), self.loop()


class Chart(LWC):
    def __init__(self, volume_enabled: bool = True, width: int = 800, height: int = 600, x: int = None, y: int = None,
                 on_top: bool = False, maximize: bool = False, debug: bool = False,
                 api: object = None, topbar: bool = False, searchbox: bool = False, toolbox: bool = False,
                 inner_width: float = 1.0, inner_height: float = 1.0, dynamic_loading: bool = False, scale_candles_only: bool = False):
        super().__init__(volume_enabled, inner_width, inner_height, dynamic_loading, scale_candles_only, topbar, searchbox, toolbox, 'pywebview.api.callback')
        self._q, self._emit_q, self._return_q = (mp.Queue() for _ in range(3))
        self._exit, self._loaded = mp.Event(), mp.Event()
        self._script_func = self._q.put
        self._api = api
        self._process = mp.Process(target=PyWV, args=(self._q, self._exit, self._loaded, self._html,
                                                      width, height, x, y, on_top, maximize, debug,
                                                      self._emit_q, self._return_q), daemon=True)
        self._process.start()

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
            asyncio.run(self.show_async(block=True))

    async def show_async(self, block=False):
        self.show(block=False)
        if not block:
            asyncio.create_task(self.show_async(block=True))
            return
        try:
            while 1:
                while self._emit_q.empty() and not self._exit.is_set() and self.polygon._q.empty():
                    await asyncio.sleep(0.05)
                if self._exit.is_set():
                    self._exit.clear()
                    return
                elif not self._emit_q.empty():
                    name, chart_id, arg = self._emit_q.get()
                    self._api.chart = self._charts[chart_id]
                    if name == 'save_drawings':
                        self._api.chart.toolbox._save_drawings(arg)
                        continue
                    fixed_callbacks = ('on_search', 'on_horizontal_line_move')
                    func = self._methods[name] if name not in fixed_callbacks else getattr(self._api, name)
                    if hasattr(self._api.chart, 'topbar') and (widget := self._api.chart.topbar._widget_with_method(name)):
                        widget.value = arg
                        await func() if asyncio.iscoroutinefunction(func) else func()
                    else:
                        await func(*arg.split(';;;')) if asyncio.iscoroutinefunction(func) else func(*arg.split(';;;'))
                    continue
                value = self.polygon._q.get()
                func, args = value[0], value[1:]
                func(*args)
        except KeyboardInterrupt:
            return


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
