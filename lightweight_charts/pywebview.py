from typing import Literal, Union
from uuid import UUID
import webview
from multiprocessing import Queue

from lightweight_charts.js import LWC

_q = Queue()
_result_q = Queue()


class Webview(LWC):
    def __init__(self, chart):
        super().__init__(chart.volume_enabled, chart.inner_width, chart.inner_height)
        self.chart = chart
        self.started = False
        self._js_api_code = 'pywebview.api.onClick'

        self.webview = webview.create_window('', html=self._html, on_top=chart.on_top, js_api=self._js_api,
                                             width=chart.width, height=chart.height, x=chart.x, y=chart.y)
        self.webview.events.loaded += self._on_js_load

    def run_script(self, script): self.webview.evaluate_js(script)

    def _on_js_load(self):
        self.loaded = True
        while len(self.js_queue) > 0:
            func, args, kwargs = self.js_queue[0]

            if 'SUB' in func:
                c_id = args[0]
                args = args[1:]
                getattr(self._subcharts[c_id], func.replace('SUB', ''))(*args)
            else:
                getattr(self, func)(*args)
            del self.js_queue[0]

        _loop(self.chart, controller=self)

    def show(self):
        if self.loaded:
            self.webview.show()
        else:
            webview.start(debug=self.chart.debug)

    def hide(self): self.webview.hide()

    def exit(self):
        self.webview.destroy()
        del self

    def create_line(self, color: str = 'rgba(214, 237, 255, 0.6)', width: int = 2):
        return super().create_line(color, width).id

    def create_subchart(self, volume_enabled: bool = True, position: Literal['left', 'right', 'top', 'bottom'] = 'left',
                         width: float = 0.5, height: float = 0.5, sync: Union[bool, UUID] = False):
        return super()._pywebview_subchart(volume_enabled, position, width, height, sync)


def _loop(chart, controller=None):
    wv = Webview(chart) if not controller else controller
    chart._result_q.put(wv.id)
    while 1:
        obj = wv
        func, args = chart._q.get()

        if 'SUB' in func:
            obj = obj._subcharts[args[0]]
            args = args[1:]
            func = func.replace('SUB', '')

        try:
            result = getattr(obj, func)(*args)
        except KeyError as e:
            return
        if func == 'show':
            chart._exit.set()
        elif func == 'exit':
            chart._exit.set()

        chart._result_q.put(result) if result is not None else None

