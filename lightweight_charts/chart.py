import asyncio
import multiprocessing as mp
import webview

from lightweight_charts import abstract
from .util import parse_event_message


class CallbackAPI:
    def __init__(self, emit_queue):
        self.emit_q = emit_queue

    def callback(self, message: str):
        self.emit_q.put(message)


class PyWV:
    def __init__(self, q, start_ev, exit_ev, loaded, emit_queue, return_queue, html, debug,
                 width, height, x, y, screen, on_top, maximize):
        self.queue = q
        self.return_queue = return_queue
        self.exit = exit_ev
        self.callback_api = CallbackAPI(emit_queue)
        self.loaded: list = loaded
        self.html = html

        self.windows = []
        self.create_window(width, height, x, y, screen, on_top, maximize)

        start_ev.wait()
        webview.start(debug=debug)
        self.exit.set()

    def create_window(self, width, height, x, y, screen=None, on_top=False, maximize=False):
        screen = webview.screens[screen] if screen is not None else None
        if maximize:
            width, height = screen.width, screen.height
        self.windows.append(webview.create_window(
            '', html=self.html, js_api=self.callback_api,
            width=width, height=height, x=x, y=y, screen=screen,
            on_top=on_top,  background_color='#000000'))
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
                    if '_~_~RETURN~_~_' in arg:
                        self.return_queue.put(self.windows[i].evaluate_js(arg[14:]))
                    else:
                        self.windows[i].evaluate_js(arg)
                except KeyError:
                    return


class Chart(abstract.AbstractChart):
    MAX_WINDOWS = 10
    _window_num = 0
    _main_window_handlers = None
    _exit, _start = (mp.Event() for _ in range(2))
    _q, _emit_q, _return_q = (mp.Queue() for _ in range(3))
    _loaded_list = [mp.Event() for _ in range(MAX_WINDOWS)]

    def __init__(self, width: int = 800, height: int = 600, x: int = None, y: int = None, screen: int = None,
                 on_top: bool = False, maximize: bool = False, debug: bool = False, toolbox: bool = False,
                 inner_width: float = 1.0, inner_height: float = 1.0, scale_candles_only: bool = False):
        self._i = Chart._window_num
        self._loaded = Chart._loaded_list[self._i]
        abstract.Window._return_q = Chart._return_q
        Chart._window_num += 1
        self.is_alive = True

        window = abstract.Window(lambda s: self._q.put((self._i, s)), 'pywebview.api.callback')
        if self._i == 0:
            super().__init__(window, inner_width, inner_height, scale_candles_only, toolbox)
            Chart._main_window_handlers = self.win.handlers
            self._process = mp.Process(target=PyWV, args=(
                self._q, self._start, self._exit, Chart._loaded_list,
                self._emit_q, self._return_q, abstract.TEMPLATE, debug,
                width, height, x, y, screen, on_top, maximize,
            ), daemon=True)
            self._process.start()
        else:
            window.handlers = Chart._main_window_handlers
            super().__init__(window, inner_width, inner_height, scale_candles_only, toolbox)
            self._q.put(('create_window', (width, height, x, y, screen, on_top, maximize)))

    def show(self, block: bool = False):
        """
        Shows the chart window.\n
        :param block: blocks execution until the chart is closed.
        """
        if not self.win.loaded:
            self._start.set()
            self._loaded.wait()
            self.win.on_js_load()
        else:
            self._q.put((self._i, 'show'))
        if block:
            asyncio.run(self.show_async(block=True))

    async def show_async(self, block=False):
        self.show(block=False)
        if not block:
            asyncio.create_task(self.show_async(block=True))
            return
        try:
            from lightweight_charts import polygon
            [asyncio.create_task(self.polygon.async_set(*args)) for args in polygon._set_on_load]
            while 1:
                while self._emit_q.empty() and not self._exit.is_set():
                    await asyncio.sleep(0.05)
                if self._exit.is_set():
                    self._exit.clear()
                    self.is_alive = False
                    self.exit()
                    return
                elif not self._emit_q.empty():
                    func, args = parse_event_message(self.win, self._emit_q.get())
                    await func(*args) if asyncio.iscoroutinefunction(func) else func(*args)
                    continue
        except KeyboardInterrupt:
            return

    def hide(self):
        """
        Hides the chart window.\n
        """
        self._q.put((self._i, 'hide'))

    def exit(self):
        """
        Exits and destroys the chart window.\n
        """
        self._q.put((self._i, 'exit'))
        self._exit.wait() if self.win.loaded else None
        self._process.terminate()

        Chart._main_window_handlers = None
        Chart._window_num = 0
        Chart._q = mp.Queue()
        Chart._exit.clear(), Chart._start.clear()
        self.is_alive = False
