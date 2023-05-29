import webview
import multiprocessing as mp

from lightweight_charts.js import LWC


class CallbackAPI:
    def __init__(self, emit): self.emit = emit

    def callback(self, message: str):
        messages = message.split('__')
        name, chart_id = messages[:2]
        args = messages[2:]
        self.emit.put((name, chart_id, *args))


class PyWV:
    def __init__(self, q, exit, loaded, html, width, height, x, y, on_top, debug, emit=None):
        self.queue = q
        self.exit = exit
        self.loaded = loaded
        self.debug = debug
        js_api = CallbackAPI(emit) if emit else None
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
                 on_top: bool = False, debug: bool = False,
                 inner_width: float = 1.0, inner_height: float = 1.0, dynamic_loading: bool = False):
        super().__init__(volume_enabled, inner_width, inner_height, dynamic_loading)
        self._q = mp.Queue()
        self._script_func = self._q.put
        self._exit = mp.Event()
        self._loaded = mp.Event()
        self._process = mp.Process(target=PyWV, args=(self._q, self._exit, self._loaded, self._html,
                                                      width, height, x, y, on_top, debug,), daemon=True)
        self._process.start()
        self._create_chart()

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

