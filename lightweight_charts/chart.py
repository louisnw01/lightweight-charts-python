import asyncio
import json
import multiprocessing as mp
import typing
import webview
from webview.errors import JavascriptException

from lightweight_charts import abstract
from .util import parse_event_message, FLOAT

import os
import threading


class CallbackAPI:
    def __init__(self, emit_queue):
        self.emit_queue = emit_queue

    def callback(self, message: str):
        self.emit_queue.put(message)


class PyWV:
    def __init__(self, q, emit_q, return_q, loaded_event):
        self.queue = q
        self.return_queue = return_q
        self.emit_queue = emit_q
        self.loaded_event = loaded_event

        self.is_alive = True

        self.callback_api = CallbackAPI(emit_q)
        self.windows: typing.List[webview.Window] = []
        self.loop()


    def create_window(
        self, width, height, x, y, screen=None, on_top=False,
        maximize=False, title=''
    ):
        screen = webview.screens[screen] if screen is not None else None
        if maximize:
            if screen is None:
                active_screen = webview.screens[0]
                width, height = active_screen.width, active_screen.height
            else:
                width, height = screen.width, screen.height

        self.windows.append(webview.create_window(
            title,
            url=abstract.INDEX,
            js_api=self.callback_api,
            width=width,
            height=height,
            x=x,
            y=y,
            screen=screen,
            on_top=on_top,
            background_color='#000000')
        )

        self.windows[-1].events.loaded += lambda: self.loaded_event.set()


    def loop(self):
        # self.loaded_event.set()
        while self.is_alive:
            i, arg = self.queue.get()

            if i == 'start':
                webview.start(debug=arg, func=self.loop)
                self.is_alive = False
                self.emit_queue.put('exit')
                return
            if i == 'create_window':
                self.create_window(*arg)
                continue

            window = self.windows[i]
            if arg == 'show':
                window.show()
            elif arg == 'hide':
                window.hide()
            else:
                try:
                    if '_~_~RETURN~_~_' in arg:
                        self.return_queue.put(window.evaluate_js(arg[14:]))
                    else:
                        window.evaluate_js(arg)
                except KeyError as e:
                    return
                except JavascriptException as e:
                    msg = eval(str(e))
                    raise JavascriptException(f"\n\nscript -> '{arg}',\nerror -> {msg['name']}[{msg['line']}:{msg['column']}]\n{msg['message']}")


class WebviewHandler():
    def __init__(self) -> None:
        self._reset()
        self.debug = False

    def _reset(self):
        self.loaded_event = mp.Event()
        self.return_queue = mp.Queue()
        self.function_call_queue = mp.Queue()
        self.emit_queue = mp.Queue()
        self.wv_process = mp.Process(
            target=PyWV, args=(
                self.function_call_queue, self.emit_queue,
                self.return_queue, self.loaded_event
            ),
            daemon=True
        )
        self.max_window_num = -1

    def create_window(
        self, width, height, x, y, screen=None, on_top=False,
        maximize=False, title=''
    ):
        self.function_call_queue.put((
            'create_window',
            (width, height, x, y, screen, on_top, maximize, title)
        ))
        self.max_window_num += 1
        return self.max_window_num

    def start(self):
        self.loaded_event.clear()
        self.wv_process.start()
        self.function_call_queue.put(('start', self.debug))
        self.loaded_event.wait()

    def show(self, window_num):
        self.function_call_queue.put((window_num, 'show'))

    def hide(self, window_num):
        self.function_call_queue.put((window_num, 'hide'))

    def evaluate_js(self, window_num, script):
        self.function_call_queue.put((window_num, script))

    def exit(self):
        if self.wv_process.is_alive():
            self.wv_process.terminate()
            self.wv_process.join()
        self._reset()


class Chart(abstract.AbstractChart):
    _main_window_handlers = None
    WV: WebviewHandler = WebviewHandler()

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        x: int = None,
        y: int = None,
        title: str = '',
        screen: int = None,
        on_top: bool = False,
        maximize: bool = False,
        debug: bool = False,
        toolbox: bool = False,
        inner_width: float = 1.0,
        inner_height: float = 1.0,
        scale_candles_only: bool = False,
        position: FLOAT = 'left'
    ):
        Chart.WV.debug = debug
        self._i = Chart.WV.create_window(
                    width, height, x, y, screen, on_top, maximize, title
                )

        window = abstract.Window(
                    script_func=lambda s: Chart.WV.evaluate_js(self._i, s),
                    js_api_code='pywebview.api.callback'
                )

        abstract.Window._return_q = Chart.WV.return_queue

        self.is_alive = True

        if Chart._main_window_handlers is None:
            super().__init__(window, inner_width, inner_height, scale_candles_only, toolbox, position=position)
            Chart._main_window_handlers = self.win.handlers
        else:
            window.handlers = Chart._main_window_handlers
            super().__init__(window, inner_width, inner_height, scale_candles_only, toolbox, position=position)

    def show(self, block: bool = False):
        """
        Shows the chart window.\n
        :param block: blocks execution until the chart is closed.
        """
        if not self.win.loaded:
            Chart.WV.start()
            self.win.on_js_load()
        else:
            Chart.WV.show(self._i)
        if block:
            asyncio.run(self.show_async())

    async def show_async(self):
        self.show(block=False)
        try:
            from lightweight_charts import polygon
            [asyncio.create_task(self.polygon.async_set(*args)) for args in polygon._set_on_load]
            while 1:
                while Chart.WV.emit_queue.empty() and self.is_alive:
                    await asyncio.sleep(0.05)
                if not self.is_alive:
                    return
                response = Chart.WV.emit_queue.get()
                if response == 'exit':
                    Chart.WV.exit()
                    self.is_alive = False
                    return
                else:
                    func, args = parse_event_message(self.win, response)
                    await func(*args) if asyncio.iscoroutinefunction(func) else func(*args)
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
        Chart.WV.exit()
        self.is_alive = False
