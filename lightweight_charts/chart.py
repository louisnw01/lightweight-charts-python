
import pandas as pd
import multiprocessing as mp
from uuid import UUID
from datetime import datetime
from typing import Union, Literal

from lightweight_charts.pywebview import _loop
from lightweight_charts.util import LINE_TYPE, POSITION, SHAPE, CROSSHAIR_MODE, PRICE_SCALE_MODE


class Line:
    def __init__(self, chart, line_id):
        self._chart = chart
        self.id = line_id

    def set(self, data: pd.DataFrame):
        """
        Sets the line data.\n
        :param data: columns: date/time, price
        """
        self._chart._go('_set_line_data', self.id, data)

    def update(self, series: pd.Series):
        """
        Updates the line data.\n
        :param series: labels: date/time, price
        """
        self._chart._go('_update_line_data', self.id, series)


class Chart:
    def __init__(self, volume_enabled: bool = True, width: int = 800, height: int = 600, x: int = None, y: int = None,
                 on_top: bool = False, debug: bool = False, sub: bool = False,
                 inner_width: float = 1.0, inner_height: float = 1.0):
        self.debug = debug
        self.volume_enabled = volume_enabled
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.on_top = on_top
        self.inner_width = inner_width
        self.inner_height = inner_height

        if sub:
            return
        self._q = mp.Queue()
        self._result_q = mp.Queue()
        self._exit = mp.Event()
        self._process = mp.Process(target=_loop, args=(self,), daemon=True)
        self._process.start()
        self.id = self._result_q.get()

    def _go(self, func, *args): self._q.put((func, args))

    def _go_return(self, func, *args):
        self._q.put((func, args))
        return self._result_q.get()

    def show(self, block: bool = False):
        """
        Shows the chart window.\n
        :param block: blocks execution until the chart is closed.
        """
        self._go('show')
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
        self._go('hide')

    def exit(self):
        """
        Exits and destroys the chart window.\n
        """
        self._go('exit')
        self._exit.wait()
        self._process.terminate()
        del self

    def run_script(self, script: str):
        """
        For advanced users; evaluates JavaScript within the Webview.
        """
        self._go('run_script', script)

    def set(self, data: pd.DataFrame):
        """
        Sets the initial data for the chart.\n
        :param data: columns: date/time, open, high, low, close, volume (if volume enabled).
        """
        self._go('set', data)

    def update(self, series: pd.Series):
        """
        Updates the data from a bar;
        if series['time'] is the same time as the last bar, the last bar will be overwritten.\n
        :param series: columns: date/time, open, high, low, close, volume (if volume enabled).
        """
        self._go('update', series)

    def update_from_tick(self, series: pd.Series):
        """
        Updates the data from a tick.\n
        :param series: columns: date/time, price, volume (if volume enabled).
        """
        self._go('update_from_tick', series)

    def create_line(self, color: str = 'rgba(214, 237, 255, 0.6)', width: int = 2):
        """
        Creates and returns a Line object.)\n
        :return a Line object used to set/update the line.
        """
        line_id = self._go_return('create_line', color, width)
        return Line(self, line_id)

    def marker(self, time: datetime = None, position: POSITION = 'below', shape: SHAPE = 'arrow_up',
               color='#2196F3', text='') -> UUID:
        """
        Creates a new marker.\n
        :param time: The time that the marker will be placed at. If no time is given, it will be placed at the last bar.
        :param position: The position of the marker.
        :param color: The color of the marker (rgb, rgba or hex).
        :param shape: The shape of the marker.
        :param text: The text to be placed with the marker.
        :return: The UUID of the marker placed.
        """
        return self._go_return('marker', time, position, shape, color, text)

    def remove_marker(self, marker_id: UUID):
        """
        Removes the marker with the given uuid.\n
        :param marker_id:
        """
        self._go('remove_marker', marker_id)

    def horizontal_line(self, price: Union[float, int], color: str = 'rgb(122, 146, 202)', width: int = 1,
                        style: LINE_TYPE = 'solid', text: str = '', axis_label_visible: bool = True):
        """
        Creates a horizontal line at the given price.\n
        """
        self._go('horizontal_line', price, color, width, style, text, axis_label_visible)

    def remove_horizontal_line(self, price: Union[float, int]):
        """
        Removes a horizontal line at the given price.
        """
        self._go('remove_horizontal_line', price)

    def config(self, mode: PRICE_SCALE_MODE = None, title: str = None, right_padding: float = None):
        """
        :param mode: Chart price scale mode.
        :param title: Last price label text.
        :param right_padding: How many bars of empty space to the right of the last bar.
        """
        self._go('config', mode, title, right_padding)

    def time_scale(self, visible: bool = True, time_visible: bool = True, seconds_visible: bool = False):
        """
        Options for the time scale of the chart.
        :param visible: Time scale visibility control.
        :param time_visible: Time visibility control.
        :param seconds_visible: Seconds visibility control
        :return:
        """
        self._go('time_scale', visible, time_visible, seconds_visible)

    def layout(self, background_color: str = None, text_color: str = None, font_size: int = None,
               font_family: str = None):
        """
        Global layout options for the chart.
        """
        self._go('layout', background_color, text_color, font_size, font_family)

    def grid(self, vert_enabled: bool = True, horz_enabled: bool = True, color: str = 'rgba(29, 30, 38, 5)', style: LINE_TYPE = 'solid'):
        """
        Grid styling for the chart.
        """
        self._go('grid', vert_enabled, horz_enabled, color, style)

    def candle_style(self, up_color: str = 'rgba(39, 157, 130, 100)', down_color: str = 'rgba(200, 97, 100, 100)',
                     wick_enabled: bool = True, border_enabled: bool = True, border_up_color: str = '',
                     border_down_color: str = '', wick_up_color: str = '', wick_down_color: str = ''):
        """
        Candle styling for each of its parts.
        """
        self._go('candle_style', up_color, down_color, wick_enabled, border_enabled,
                 border_up_color, border_down_color, wick_up_color, wick_down_color)

    def volume_config(self, scale_margin_top: float = 0.8, scale_margin_bottom: float = 0.0,
                      up_color='rgba(83,141,131,0.8)', down_color='rgba(200,127,130,0.8)'):
        """
        Configure volume settings.\n
        Numbers for scaling must be greater than 0 and less than 1.\n
        Volume colors must be applied prior to setting/updating the bars.\n
        :param scale_margin_top: Scale the top of the margin.
        :param scale_margin_bottom: Scale the bottom of the margin.
        :param up_color: Volume color for upward direction (rgb, rgba or hex)
        :param down_color: Volume color for downward direction (rgb, rgba or hex)
        """
        self._go('volume_config', scale_margin_top, scale_margin_bottom, up_color, down_color)

    def crosshair(self, mode: CROSSHAIR_MODE = 'normal', vert_width: int = 1, vert_color: str = None,
                  vert_style: LINE_TYPE = None, vert_label_background_color: str = None, horz_width: int = 1,
                  horz_color: str = None, horz_style: LINE_TYPE = None, horz_label_background_color: str = None):
        """
        Crosshair formatting for its vertical and horizontal axes.
        """
        self._go('crosshair', mode, vert_width, vert_color, vert_style, vert_label_background_color,
                 horz_width, horz_color, horz_style, horz_label_background_color)

    def watermark(self, text: str, font_size: int = 44, color: str = 'rgba(180, 180, 200, 0.5)'):
        """
        Adds a watermark to the chart.
        """
        self._go('watermark', text, font_size, color)

    def legend(self, visible: bool = False, ohlc: bool = True, percent: bool = True, color: str = None,
               font_size: int = None, font_family: str = None):
        """
        Configures the legend of the chart.
        """
        self._go('legend', visible, ohlc, percent, color, font_size, font_family)

    def subscribe_click(self, function: object):
        """
        Subscribes the given function to a chart 'click' event.
        The event returns a dictionary containing the bar object at the time clicked.
        """
        self._go('subscribe_click', function)

    def create_subchart(self, volume_enabled: bool = True, position: Literal['left', 'right', 'top', 'bottom'] = 'left',
                         width: float = 0.5, height: float = 0.5, sync: Union[bool, UUID] = False):
        c_id = self._go_return('create_subchart', volume_enabled, position, width, height, sync)
        return SubChart(self, c_id)


class SubChart(Chart):
    def __init__(self, parent, c_id):
        self._parent = parent._parent if isinstance(parent, SubChart) else parent

        super().__init__(sub=True)

        self.id = c_id
        self._q = self._parent._q
        self._result_q = self._parent._result_q

    def _go(self, func, *args):
        func = 'SUB'+func
        args = (self.id,) + args
        super()._go(func, *args)

    def _go_return(self, func, *args):
        func = 'SUB' + func
        args = (self.id,) + args
        return super()._go_return(func, *args)
