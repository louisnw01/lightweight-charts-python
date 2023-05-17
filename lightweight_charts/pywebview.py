import webview
from multiprocessing import Queue

from lightweight_charts.js import LWC

_q = Queue()
_result_q = Queue()


class Webview(LWC):
    def __init__(self, chart):
        super().__init__(chart.volume_enabled)
        self.chart = chart
        self.started = False
        self._click_func_code('pywebview.api.onClick(data)')

        self.webview = webview.create_window('', html=self._html, on_top=chart.on_top, js_api=self._js_api,
                                             width=chart.width, height=chart.height, x=chart.x, y=chart.y)
        self.webview.events.loaded += self._on_js_load

    def run_script(self, script): self.webview.evaluate_js(script)

    def _on_js_load(self):
        self.loaded = True
        while len(self.js_queue) > 0:
            func, args, kwargs = self.js_queue[0]
            getattr(self, func)(*args)
            del self.js_queue[0]
        _loop(self.chart, controller=self)

    def show(self):
        if self.loaded:
            self.webview.show()
        else:
            webview.start(debug=self.chart.debug)

    def create_line(self, color: str = 'rgba(214, 237, 255, 0.6)', width: int = 2):
        return super().create_line(color, width).id

    def hide(self): self.webview.hide()

    def exit(self):
        self.webview.destroy()
        del self


def _loop(chart, controller=None):
    wv = Webview(chart) if not controller else controller
    while 1:
        func, args = chart._q.get()
        try:
            result = getattr(wv, func)(*args)
        except KeyError as e:
            return
        if func == 'show':
            chart._exit.set()
        elif func == 'exit':
            chart._exit.set()
        chart._result_q.put(result) if result is not None else None

