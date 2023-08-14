import asyncio
import multiprocessing as mp
import webview

from lightweight_charts.abstract import LWC


chart = None
num_charts = 0


class CallbackAPI:
    def __init__(self, emit_queue, return_queue):
        self.emit_q, self.return_q = emit_queue, return_queue

    def callback(self, message: str):
        name, args = message.split('_~_')
        self.return_q.put(*args) if name == 'return' else self.emit_q.put((name, args.split(';;;')))


class PyWV:
    def __init__(self, q, start: mp.Event, exit, loaded, html, width, height, x, y, on_top, maximize, debug, emit_queue, return_queue):
        if maximize:
            width, height = webview.screens[0].width, webview.screens[0].height
        self.queue = q
        self.exit = exit
        self.callback_api = CallbackAPI(emit_queue, return_queue)
        self.loaded: list = loaded

        self.windows = []
        self.create_window(html, on_top, width, height, x, y)

        start.wait()
        webview.start(debug=debug)
        self.exit.set()

    def create_window(self, html, on_top, width, height, x, y):
        self.windows.append(webview.create_window(
            '', html=html, on_top=on_top, js_api=self.callback_api,
            width=width, height=height, x=x, y=y, background_color='#000000'))
        self.windows[-1].events.loaded += lambda: self.loop(self.loaded[len(self.windows)-1])

    def loop(self, loaded):
        loaded.set()
        while 1:
            i, arg = self.queue.get()
            if i == 'create_window':
                self.create_window(*arg)
            elif arg in ('show', 'hide'):
                 getattr(self.windows[i], arg)()
            elif arg == 'exit':
                self.exit.set()
            else:
                try:
                    self.windows[i].evaluate_js(arg)
                except KeyError:
                    return


class Chart(LWC):
    def __init__(self, width: int = 800, height: int = 600, x: int = None, y: int = None,
                 on_top: bool = False, maximize: bool = False, debug: bool = False, toolbox: bool = False,
                 inner_width: float = 1.0, inner_height: float = 1.0, scale_candles_only: bool = False):
        super().__init__(inner_width, inner_height, scale_candles_only, toolbox, 'pywebview.api.callback')
        global chart, num_charts

        if chart:
            self._q, self._exit, self._start, self._process = chart._q, chart._exit, chart._start, chart._process
            self._emit_q, self._return_q = mp.Queue(), mp.Queue()
            for key, val in self._handlers.items():
                chart._handlers[key] = val
            self._handlers = chart._handlers
            self._loaded = chart._loaded_list[num_charts]
            self._q.put(('create_window', (self._html, on_top, width, height, x, y)))
        else:
            self._q, self._emit_q, self._return_q = (mp.Queue() for _ in range(3))
            self._loaded_list = [mp.Event() for _ in range(10)]
            self._loaded = self._loaded_list[0]
            self._exit, self._start = (mp.Event() for _ in range(2))
            self._process = mp.Process(target=PyWV, args=(self._q, self._start, self._exit, self._loaded_list, self._html,
                                                          width, height, x, y, on_top, maximize, debug,
                                                          self._emit_q, self._return_q), daemon=True)
            self._process.start()
            chart = self

        self.i = num_charts
        num_charts += 1
        self._script_func = lambda s: self._q.put((self.i, s))

    def show(self, block: bool = False):
        """
        Shows the chart window.\n
        :param block: blocks execution until the chart is closed.
        """
        if not self.loaded:
            self._start.set()
            self._loaded.wait()
            self._on_js_load()
        else:
            self._q.put((self.i, 'show'))
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
                    name, args = self._emit_q.get()
                    func = self._handlers[name]
                    await func(*args) if asyncio.iscoroutinefunction(func) else func(*args)
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
        self._q.put((self.i, 'hide'))

    def exit(self):
        """
        Exits and destroys the chart window.\n
        """
        global num_charts, chart
        chart = None
        num_charts = 0
        self._q.put((self.i, 'exit'))
        self._exit.wait()
        self._process.terminate()
        del self
