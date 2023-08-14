import asyncio
import json
import os
from datetime import timedelta, datetime
from base64 import b64decode
import pandas as pd
from typing import Union, Literal, Dict, List

from lightweight_charts.table import Table
from lightweight_charts.util import LINE_STYLE, MARKER_POSITION, MARKER_SHAPE, CROSSHAIR_MODE, crosshair_mode, \
    line_style, jbool, price_scale_mode, PRICE_SCALE_MODE, marker_position, marker_shape, IDGen, Events

JS = {}
current_dir = os.path.dirname(os.path.abspath(__file__))
for file in ('pkg', 'funcs', 'callback', 'toolbox', 'table'):
    with open(os.path.join(current_dir, 'js', f'{file}.js'), 'r', encoding='utf-8') as f:
        JS[file] = f.read()

HTML = f"""
<!DOCTYPE html>
<html lang="">
<head>
    <title>lightweight-charts-python</title>
    <script>{JS['pkg']}</script>
    <meta name="viewport" content ="width=device-width, initial-scale=1">
    <style>
    body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
    }}
    #wrapper {{
        width: 100vw;
        height: 100vh;
        background-color: #000000;
    }}
    </style>
</head>
<body>
    <div id="wrapper"></div>
    <script>
    {JS['funcs']}
    {JS['table']}
    </script>
</body>
</html>
"""


class SeriesCommon:
    def _set_interval(self, df: pd.DataFrame):
        if not pd.api.types.is_datetime64_any_dtype(df['time']):
            df['time'] = pd.to_datetime(df['time'])
        common_interval = df['time'].diff().value_counts()
        try:
            self._interval = common_interval.index[0]
        except IndexError:
            raise IndexError('Not enough bars within the given data to calculate the interval/timeframe.')
        self.run_script(f'''
            if ({self.id}.toolBox) {{
                {self.id}.toolBox.interval = {self._interval.total_seconds()*1000}
            }}
        ''')

    @staticmethod
    def _rename(data, mapper, is_dataframe):
        if is_dataframe:
            data.columns = [mapper[key] if key in mapper else key for key in data.columns]
        else:
            data.index = [mapper[key] if key in mapper else key for key in data.index]

    def _df_datetime_format(self, df: pd.DataFrame, exclude_lowercase=None):
        df = df.copy()
        if 'date' not in df.columns and 'time' not in df.columns:
            df.columns = df.columns.str.lower()
            if exclude_lowercase:
                df[exclude_lowercase] = df[exclude_lowercase.lower()]
        if 'date' in df.columns:
            self._rename(df, {'date': 'time'}, True)
        elif 'time' not in df.columns:
            df['time'] = df.index
        self._set_interval(df)
        df['time'] = self._datetime_format(df['time'])
        return df

    def _series_datetime_format(self, series: pd.Series, exclude_lowercase=None):
        series = series.copy()
        if 'date' not in series.index and 'time' not in series.index:
            series.index = series.index.str.lower()
            if exclude_lowercase:
                self._rename(series, {exclude_lowercase.lower(): exclude_lowercase}, False)
        if 'date' in series.index:
            self._rename(series, {'date': 'time'}, False)
        elif 'time' not in series.index:
            series['time'] = series.name
        series['time'] = self._datetime_format(series['time'])
        return series

    def _datetime_format(self, arg: Union[pd.Series, str]):
        if not pd.api.types.is_datetime64_any_dtype(arg):
            arg = pd.to_datetime(arg)
        if self._interval < timedelta(days=1):
            if isinstance(arg, pd.Series):
                arg = arg.astype('int64') // 10 ** 9
            else:
                interval_seconds = self._interval.total_seconds()
                arg = interval_seconds * (arg.timestamp() // interval_seconds)
        else:
            arg = arg.dt.strftime('%Y-%m-%d') if isinstance(arg, pd.Series) else arg.strftime('%Y-%m-%d')

        return arg

    def marker(self, time: datetime = None, position: MARKER_POSITION = 'below', shape: MARKER_SHAPE = 'arrow_up',
               color: str = '#2196F3', text: str = '') -> str:
        """
        Creates a new marker.\n
        :param time: The time that the marker will be placed at. If no time is given, it will be placed at the last bar.
        :param position: The position of the marker.
        :param color: The color of the marker (rgb, rgba or hex).
        :param shape: The shape of the marker.
        :param text: The text to be placed with the marker.
        :return: The id of the marker placed.
        """
        try:
            time = self._last_bar['time'] if not time else self._datetime_format(time)
        except TypeError:
            raise TypeError('Chart marker created before data was set.')
        marker_id = self._rand.generate()
        self.run_script(f"""
            {self.id}.markers.push({{
                time: {time if isinstance(time, float) else f"'{time}'"},
                position: '{marker_position(position)}',
                color: '{color}',
                shape: '{marker_shape(shape)}',
                text: '{text}',
                id: '{marker_id}'
                }});
            {self.id}.series.setMarkers({self.id}.markers)""")
        return marker_id

    def remove_marker(self, marker_id: str):
        """
        Removes the marker with the given id.\n
        """
        self.run_script(f'''
           {self.id}.markers.forEach(function (marker) {{
               if ('{marker_id}' === marker.id) {{
                   {self.id}.markers.splice({self.id}.markers.indexOf(marker), 1)
                   {self.id}.series.setMarkers({self.id}.markers)
                   }}
               }});''')

    def horizontal_line(self, price: Union[float, int], color: str = 'rgb(122, 146, 202)', width: int = 2,
                        style: LINE_STYLE = 'solid', text: str = '', axis_label_visible: bool = True, func: callable = None) -> 'HorizontalLine':
        """
        Creates a horizontal line at the given price.
        """
        return HorizontalLine(self, price, color, width, style, text, axis_label_visible, func)

    def remove_horizontal_line(self, price: Union[float, int] = None):
        """
        Removes a horizontal line at the given price.
        """
        self.run_script(f'''
        {self.id}.horizontal_lines.forEach(function (line) {{
            if ({price} === line.price) line.deleteLine()
        }})''')

    def clear_markers(self):
        """
        Clears the markers displayed on the data.\n
        """
        self.run_script(f'''{self.id}.markers = []; {self.id}.series.setMarkers([])''')

    def clear_horizontal_lines(self):
        """
        Clears the horizontal lines displayed on the data.\n
        """
        self.run_script(f'''
        {self.id}.horizontal_lines.forEach(function (line) {{{self.id}.series.removePriceLine(line.line);}});
        {self.id}.horizontal_lines = [];
        ''')

    def price_line(self, label_visible: bool = True, line_visible: bool = True, title: str = ''):
        self.run_script(f'''
        {self.id}.series.applyOptions({{
            lastValueVisible: {jbool(label_visible)},
            priceLineVisible: {jbool(line_visible)},
            title: '{title}',
        }})''')

    def precision(self, precision: int):
        """
        Sets the precision and minMove.\n
        :param precision: The number of decimal places.
        """
        self.run_script(f'''
        {self.id}.precision = {precision}
        {self.id}.series.applyOptions({{
            priceFormat: {{precision: {precision}, minMove: {1 / (10 ** precision)}}}
        }})''')

    def hide_data(self): self._toggle_data(False)

    def show_data(self): self._toggle_data(True)

    def _toggle_data(self, arg):
        self.run_script(f'''
        {self.id}.series.applyOptions({{visible: {jbool(arg)}}})
        {f'{self.id}.volumeSeries.applyOptions({{visible: {jbool(arg)}}})' if hasattr(self, 'loaded') else ''}
        ''')

class HorizontalLine:
    def __init__(self, chart, price, color, width, style, text, axis_label_visible, func):
        self._chart = chart
        self.id = self._chart._rand.generate()
        self.price = price
        self._chart.run_script(f'''
        {self.id} = new HorizontalLine({self._chart.id}, '{self.id}', {price}, '{color}', {width}, {line_style(style)}, {jbool(axis_label_visible)}, '{text}')
        ''')
        if not func: return
        def wrapper(p):
            self.price = p
            func(chart, self)
        chart._handlers[self.id] = wrapper
        self._chart.run_script(f'if ("toolBox" in {self._chart.id}) {self._chart.id}.toolBox.drawings.push({self.id})')

    def update(self, price):
        """
        Moves the horizontal line to the given price.
        """
        self._chart.run_script(f'{self.id}.updatePrice({price})')
        self.price = price

    def label(self, text: str):
        self._chart.run_script(f'{self.id}.updateLabel("{text}")')

    def delete(self):
        """
        Irreversibly deletes the horizontal line.
        """
        self._chart.run_script(f'{self.id}.deleteLine()')
        del self


class Line(SeriesCommon):
    def __init__(self, chart, name, color, style, width, price_line, price_label, crosshair_marker=True):
        self.color = color
        self.name = name
        self._chart = chart
        self._rand = chart._rand
        self.id = self._rand.generate()
        self.run_script = self._chart.run_script
        self.run_script(f'''
        {self.id} = {{
            series: {self._chart.id}.chart.addLineSeries({{
                color: '{color}',
                lineStyle: {line_style(style)},
                lineWidth: {width},
                lastValueVisible: {jbool(price_label)},
                priceLineVisible: {jbool(price_line)},
                crosshairMarkerVisible: {jbool(crosshair_marker)},
                {"""autoscaleInfoProvider: () => ({
                    priceRange: {
                        minValue: 1_000_000_000,
                        maxValue: 0,
                        },
                    }),""" if self._chart._scale_candles_only else ''}
                }}),
            markers: [],
            horizontal_lines: [],
            name: '{name}',
            color: '{color}',
            precision: 2,
            }}
        {self._chart.id}.lines.push({self.id})
        if ('legend' in {self._chart.id}) {{
            {self._chart.id}.legend.makeLines({self._chart.id})
        }}
        ''')


    def set(self, data: pd.DataFrame):
        """
        Sets the line data.\n
        :param data: If the name parameter is not used, the columns should be named: date/time, value.
        :param name: The column of the DataFrame to use as the line value. When used, the Line will be named after this column.
        """
        if data.empty or data is None:
            self.run_script(f'{self.id}.series.setData([])')
            return
        df = self._df_datetime_format(data, exclude_lowercase=self.name)
        if self.name:
            if self.name not in data:
                raise NameError(f'No column named "{self.name}".')
            df = df.rename(columns={self.name: 'value'})
        self._last_bar = df.iloc[-1]
        self.run_script(f'{self.id}.series.setData({df.to_dict("records")})')

    def update(self, series: pd.Series):
        """
        Updates the line data.\n
        :param series: labels: date/time, value
        """
        series = self._series_datetime_format(series, exclude_lowercase=self.name)
        if self.name in series.index:
            series.rename({self.name: 'value'}, inplace=True)
        self._last_bar = series
        self.run_script(f'{self.id}.series.update({series.to_dict()})')

    def _set_trend(self, start_time, start_value, end_time, end_value, ray=False):
        def time_format(time_val):
            time_val = pd.to_datetime(time_val)
            time_val = time_val.timestamp() if self._chart._interval < pd.Timedelta(days=1) else time_val.strftime('%Y-%m-%d')
            return f"'{time_val}'" if isinstance(time_val, str) else time_val
        self.run_script(f'''
        {self._chart.id}.chart.timeScale().applyOptions({{shiftVisibleRangeOnNewBar: false}})
        {self.id}.series.setData(calculateTrendLine({time_format(start_time)}, {start_value}, {time_format(end_time)}, {end_value},
                                {self._chart._interval.total_seconds()*1000}, {self._chart.id}, {jbool(ray)}))
        {self._chart.id}.chart.timeScale().applyOptions({{shiftVisibleRangeOnNewBar: true}})
        ''')

    def delete(self):
        """
        Irreversibly deletes the line, as well as the object that contains the line.
        """
        self._chart._lines.remove(self) if self in self._chart._lines else None
        self.run_script(f'''
            {self._chart.id}.chart.removeSeries({self.id}.series)
            delete {self.id}
            ''')
        del self


class Widget:
    def __init__(self, topbar, value, func=None):
        self._chart = topbar._chart
        self.id = topbar._chart._rand.generate()
        self.value = value
        self._handler = func
        def wrapper(v):
            self.value = v
            func(topbar._chart)
        async def async_wrapper(v):
            self.value = v
            await func(topbar._chart)
        self._chart._handlers[self.id] = async_wrapper if asyncio.iscoroutinefunction(func) else wrapper


class TextWidget(Widget):
    def __init__(self, topbar, initial_text):
        super().__init__(topbar, value=initial_text)
        self._chart.run_script(f'{self.id} = {topbar.id}.makeTextBoxWidget("{initial_text}")')

    def set(self, string):
        self.value = string
        self._chart.run_script(f'{self.id}.innerText = "{string}"')


class SwitcherWidget(Widget):
    def __init__(self, topbar, options, default, func):
        super().__init__(topbar, value=default, func=func)
        self._chart.run_script(f'''
        {self.id} = {topbar.id}.makeSwitcher({list(options)}, '{default}', '{self.id}')
        reSize({self._chart.id})
        ''')


class ButtonWidget(Widget):
    def __init__(self, topbar, button, separator, func):
        super().__init__(topbar, value=button, func=func)
        self._chart.run_script(f'''
        {self.id} = {topbar.id}.makeButton('{button}', '{self.id}')
        {f'{topbar.id}.makeSeparator()' if separator else ''}
        reSize({self._chart.id})
        ''')

    def set(self, string):
        self.value = string
        self._chart.run_script(f'{self.id}.elem.innerText = "{string}"')


class TopBar:
    def __init__(self, chart):
        self._chart = chart
        self.id = chart._rand.generate()
        self._widgets: Dict[str, Widget] = {}

        self.click_bg_color = '#50565E'
        self.hover_bg_color = '#3c434c'
        self.active_bg_color = 'rgba(0, 122, 255, 0.7)'
        self.active_text_color = '#ececed'
        self.text_color = '#d8d9db'
        self._created = False

    def _create(self):
        if self._created:
            return
        self._created = True
        if not self._chart._callbacks_enabled:
            self._chart._callbacks_enabled = True
            self._chart.run_script(JS['callback'])
        self._chart.run_script(f'''
        {self.id} = new TopBar({self._chart.id}, '{self.hover_bg_color}', '{self.click_bg_color}',
                            '{self.active_bg_color}', '{self.text_color}', '{self.active_text_color}')
        {self._chart.id}.topBar = {self.id}.topBar
        reSize({self._chart.id})
        ''')

    def __getitem__(self, item):
        if widget := self._widgets.get(item):
            return widget
        raise KeyError(f'Topbar widget "{item}" not found.')

    def get(self, widget_name): return self._widgets.get(widget_name)

    def __setitem__(self, key, value): self._widgets[key] = value

    def switcher(self, name, options: tuple, default: str = None, func: callable = None):
        self._create()
        self._widgets[name] = SwitcherWidget(self, options, default if default else options[0], func)

    def textbox(self, name: str, initial_text: str = ''):
        self._create()
        self._widgets[name] = TextWidget(self, initial_text)

    def button(self, name, button_text: str, separator: bool = True, func: callable = None):
        self._create()
        self._widgets[name] = ButtonWidget(self, button_text, separator, func)


class ToolBox:
    def __init__(self, chart):
        self.run_script = chart.run_script
        self.id = chart.id
        self._return_q = chart._return_q
        self._save_under = None
        self.drawings = {}
        chart._handlers[f'save_drawings{self.id}'] = self._save_drawings

    def save_drawings_under(self, widget: Widget):
        """
        Drawings made on charts will be saved under the widget given. eg `chart.toolbox.save_drawings_under(chart.topbar['symbol'])`.
        """
        self._save_under = widget

    def load_drawings(self, tag: str):
        """
        Loads and displays the drawings on the chart stored under the tag given.
        """
        if not self.drawings.get(tag):
            return
        self.run_script(f'if ("toolBox" in {self.id}) {self.id}.toolBox.loadDrawings({json.dumps(self.drawings[tag])})')

    def import_drawings(self, file_path):
        """
        Imports a list of drawings stored at the given file path.
        """
        with open(file_path, 'r') as f:
            json_data = json.load(f)
            self.drawings = json_data

    def export_drawings(self, file_path):
        """
        Exports the current list of drawings to the given file path.
        """
        with open(file_path, 'w+') as f:
            json.dump(self.drawings, f, indent=4)

    def _save_drawings(self, drawings):
        if not self._save_under:
            return
        self.drawings[self._save_under.value] = json.loads(drawings)


class LWC(SeriesCommon):
    def __init__(self, inner_width: float = 1.0, inner_height: float = 1.0,
                 scale_candles_only: bool = False, toolbox: bool = False, _js_api_code: str = None,
                 autosize: bool = True, _run_script=None):
        self.loaded = False
        self._scripts = []
        self._final_scripts = []
        if _run_script:
            self.run_script = _run_script
        self.run_script(f'window.callbackFunction = {_js_api_code}') if _js_api_code else None
        self._scale_candles_only = scale_candles_only
        self._inner_width = inner_width
        self._inner_height = inner_height
        self._rand = IDGen()
        self.id = self._rand.generate()
        self._position = 'left'
        self._html = HTML
        self._script_func = None
        self.candle_data = pd.DataFrame()
        self._last_bar = None
        self._interval = None
        self._lines = []
        self.events: Events = Events(self)
        self._handlers = {}
        self._return_q = None
        self._callbacks_enabled = False
        self.topbar: TopBar = TopBar(self)

        self._background_color = '#000000'
        self._volume_up_color = 'rgba(83,141,131,0.8)'
        self._volume_down_color = 'rgba(200,127,130,0.8)'

        from lightweight_charts.polygon import PolygonAPI
        self.polygon: PolygonAPI = PolygonAPI(self)

        self.run_script(f'''
            {self.id} = makeChart({self._inner_width}, {self._inner_height}, autoSize={jbool(autosize)})
            {self.id}.id = '{self.id}'
            {self.id}.wrapper.style.float = "{self._position}"
        ''')
        if toolbox:
            self.run_script(JS['toolbox'])
            self.run_script(f'{self.id}.toolBox = new ToolBox({self.id})')
            self.toolbox: ToolBox = ToolBox(self)

    def _on_js_load(self):
        if self.loaded:
            return
        self.loaded = True
        [self.run_script(script) for script in self._scripts]
        [self.run_script(script) for script in self._final_scripts]

    def run_script(self, script: str, run_last: bool = False):
        """
        For advanced users; evaluates JavaScript within the Webview.
        """
        if self.loaded:
            self._script_func(script)
            return
        self._scripts.append(script) if not run_last else self._final_scripts.append(script)

    def set(self, df: pd.DataFrame = None, render_drawings=False):
        """
        Sets the initial data for the chart.\n
        :param df: columns: date/time, open, high, low, close, volume (if volume enabled).
        :param render_drawings: Re-renders any drawings made through the toolbox. Otherwise, they will be deleted.
        """

        if df.empty or df is None:
            self.run_script(f'{self.id}.series.setData([])')
            self.run_script(f'{self.id}.volumeSeries.setData([])')
            self.candle_data = pd.DataFrame()
            return
        bars = self._df_datetime_format(df)
        self.candle_data = bars.copy()
        self._last_bar = bars.iloc[-1]

        if 'volume' in bars:
            volume = bars.drop(columns=['open', 'high', 'low', 'close']).rename(columns={'volume': 'value'})
            volume['color'] = self._volume_down_color
            volume.loc[bars['close'] > bars['open'], 'color'] = self._volume_up_color
            self.run_script(f'{self.id}.volumeSeries.setData({volume.to_dict(orient="records")})')
            bars = bars.drop(columns=['volume'])

        bars = bars.to_dict(orient='records')
        self.run_script(f'{self.id}.candleData = {bars}; {self.id}.series.setData({self.id}.candleData)')
        self.run_script(f"if ('toolBox' in {self.id}) {self.id}.toolBox.{'clearDrawings' if not render_drawings else 'renderDrawings'}()")

        # for line in self._lines:
        #     if line.name in df.columns:
        #         line.set()

    def fit(self):
        """
        Fits the maximum amount of the chart data within the viewport.
        """
        self.run_script(f'{self.id}.chart.timeScale().fitContent()')

    def update(self, series: pd.Series, _from_tick=False):
        """
        Updates the data from a bar;
        if series['time'] is the same time as the last bar, the last bar will be overwritten.\n
        :param series: labels: date/time, open, high, low, close, volume (if volume enabled).
        """
        series = self._series_datetime_format(series) if not _from_tick else series
        if series['time'] != self._last_bar['time']:
            self.candle_data.loc[self.candle_data.index[-1]] = self._last_bar
            self.candle_data = pd.concat([self.candle_data, series.to_frame().T], ignore_index=True)
            self.events.new_bar._emit(self)
        self._last_bar = series

        if 'volume' in series:
            volume = series.drop(['open', 'high', 'low', 'close']).rename({'volume': 'value'})
            volume['color'] = self._volume_up_color if series['close'] > series['open'] else self._volume_down_color
            self.run_script(f'{self.id}.volumeSeries.update({volume.to_dict()})')
            series = series.drop(['volume'])
        bar = series.to_dict()
        self.run_script(f'''
            if (chartTimeToDate({self.id}.candleData[{self.id}.candleData.length-1].time).getTime() === chartTimeToDate({bar['time']}).getTime()) {{
                {self.id}.candleData[{self.id}.candleData.length-1] = {bar}
            }}
            else {{
                {self.id}.candleData.push({bar})
            }}
            {self.id}.series.update({bar})
            ''')

    def update_from_tick(self, series: pd.Series, cumulative_volume: bool = False):
        """
        Updates the data from a tick.\n
        :param series: labels: date/time, price, volume (if volume enabled).
        :param cumulative_volume: Adds the given volume onto the latest bar.
        """
        series = self._series_datetime_format(series)
        bar = pd.Series()
        if series['time'] == self._last_bar['time']:
            bar = self._last_bar
            bar['high'] = max(self._last_bar['high'], series['price'])
            bar['low'] = min(self._last_bar['low'], series['price'])
            bar['close'] = series['price']
            if 'volume' in series:
                if cumulative_volume:
                    bar['volume'] += series['volume']
                else:
                    bar['volume'] = series['volume']
        else:
            for key in ('open', 'high', 'low', 'close'):
                bar[key] = series['price']
            bar['time'] = series['time']
            if 'volume' in series:
                bar['volume'] = series['volume']
        self.update(bar, _from_tick=True)

    def create_line(self, name: str = '', color: str = 'rgba(214, 237, 255, 0.6)', style: LINE_STYLE = 'solid', width: int = 2,
                    price_line: bool = True, price_label: bool = True) -> Line:
        """
        Creates and returns a Line object.)\n
        """
        self._lines.append(Line(self, name, color, style, width, price_line, price_label))
        return self._lines[-1]

    def lines(self) -> List[Line]:
        """
        Returns all lines for the chart.
        """
        return self._lines.copy()

    def trend_line(self, start_time, start_value, end_time, end_value, color: str = '#1E80F0', width: int = 2) -> Line:
        line = Line(self, '', color, 'solid', width, price_line=False, price_label=False, crosshair_marker=False)
        line._set_trend(start_time, start_value, end_time, end_value, ray=False)
        return line

    def ray_line(self, start_time, value, color: str = '#1E80F0', width: int = 2) -> Line:
        line = Line(self, '', color, 'solid', width, price_line=False, price_label=False, crosshair_marker=False)
        line._set_trend(start_time, value, start_time, value, ray=True)
        return line

    def price_scale(self, mode: PRICE_SCALE_MODE = 'normal', align_labels: bool = True, border_visible: bool = False,
                    border_color: str = None, text_color: str = None, entire_text_only: bool = False,
                    ticks_visible: bool = False, scale_margin_top: float = 0.2, scale_margin_bottom: float = 0.2):
        self.run_script(f'''
            {self.id}.series.priceScale().applyOptions({{
                mode: {price_scale_mode(mode)},
                alignLabels: {jbool(align_labels)},
                borderVisible: {jbool(border_visible)},
                {f'borderColor: "{border_color}",' if border_color else ''}
                {f'textColor: "{text_color}",' if text_color else ''}
                entireTextOnly: {jbool(entire_text_only)},
                ticksVisible: {jbool(ticks_visible)},
                scaleMargins: {{top: {scale_margin_top}, bottom: {scale_margin_bottom}}}
            }})''')

    def time_scale(self, right_offset: int = 0, min_bar_spacing: float = 0.5,
                   visible: bool = True, time_visible: bool = True, seconds_visible: bool = False,
                   border_visible: bool = True, border_color: str = None):
        """
        Options for the time scale of the chart.
        """
        self.run_script(f'''
            {self.id}.chart.applyOptions({{
                timeScale: {{
                    rightOffset: {right_offset},
                    minBarSpacing: {min_bar_spacing},
                    visible: {jbool(visible)},
                    timeVisible: {jbool(time_visible)},
                    secondsVisible: {jbool(seconds_visible)},
                    borderVisible: {jbool(border_visible)},
                    {f'borderColor: "{border_color}",' if border_color else ''}
                }}
            }})''')

    def layout(self, background_color: str = None, text_color: str = None, font_size: int = None,
               font_family: str = None):
        """
        Global layout options for the chart.
        """
        self._background_color = background_color if background_color else self._background_color
        self.run_script(f"""
            document.getElementById('wrapper').style.backgroundColor = '{self._background_color}'
            {self.id}.chart.applyOptions({{
            layout: {{
                background: {{
                    color: "{self._background_color}",
                }},
                {f'textColor: "{text_color}",' if text_color else ''}
                {f'fontSize: {font_size},' if font_size else ''}
                {f'fontFamily: "{font_family}",' if font_family else ''}
            }}}})""")

    def grid(self, vert_enabled: bool = True, horz_enabled: bool = True, color: str = 'rgba(29, 30, 38, 5)', style: LINE_STYLE = 'solid'):
        """
        Grid styling for the chart.
        """
        self.run_script(f"""
        {self.id}.chart.applyOptions({{
        grid: {{
            vertLines: {{
                visible: {jbool(vert_enabled)},
                color: "{color}",
                style: {line_style(style)},
            }},
            horzLines: {{
                visible: {jbool(horz_enabled)},
                color: "{color}",
                style: {line_style(style)},
            }},
        }}
        }})""")

    def candle_style(self, up_color: str = 'rgba(39, 157, 130, 100)', down_color: str = 'rgba(200, 97, 100, 100)',
                     wick_enabled: bool = True, border_enabled: bool = True, border_up_color: str = '',
                     border_down_color: str = '', wick_up_color: str = '', wick_down_color: str = ''):
        """
        Candle styling for each of its parts.\n
        If only `up_color` and `down_color` are passed, they will color all parts of the candle.
        """
        self.run_script(f"""
            {self.id}.series.applyOptions({{
                upColor: "{up_color}",
                downColor: "{down_color}",
                wickVisible: {jbool(wick_enabled)},
                borderVisible: {jbool(border_enabled)},
                {f'borderUpColor: "{border_up_color if border_up_color else up_color}",' if border_enabled else ''}
                {f'borderDownColor: "{border_down_color if border_down_color else down_color}",' if border_enabled else ''}
                {f'wickUpColor: "{wick_up_color if wick_up_color else up_color}",' if wick_enabled else ''}
                {f'wickDownColor: "{wick_down_color if wick_down_color else down_color}",' if wick_enabled else ''}
            }})""")

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
        self._volume_up_color = up_color if up_color else self._volume_up_color
        self._volume_down_color = down_color if down_color else self._volume_down_color
        self.run_script(f'''
        {self.id}.volumeSeries.priceScale().applyOptions({{
            scaleMargins: {{
            top: {scale_margin_top},
            bottom: {scale_margin_bottom},
            }}
        }})''')

    def crosshair(self, mode: CROSSHAIR_MODE = 'normal', vert_visible: bool = True, vert_width: int = 1, vert_color: str = None,
                  vert_style: LINE_STYLE = 'large_dashed', vert_label_background_color: str = 'rgb(46, 46, 46)', horz_visible: bool = True,
                  horz_width: int = 1, horz_color: str = None, horz_style: LINE_STYLE = 'large_dashed', horz_label_background_color: str = 'rgb(55, 55, 55)'):
        """
        Crosshair formatting for its vertical and horizontal axes.
        """
        self.run_script(f'''
        {self.id}.chart.applyOptions({{
            crosshair: {{
                mode: {crosshair_mode(mode)},
                vertLine: {{
                    visible: {jbool(vert_visible)},
                    width: {vert_width},
                    {f'color: "{vert_color}",' if vert_color else ''}
                    style: {line_style(vert_style)},
                    labelBackgroundColor: "{vert_label_background_color}"
                }},
                horzLine: {{
                    visible: {jbool(horz_visible)},
                    width: {horz_width},
                    {f'color: "{horz_color}",' if horz_color else ''}
                    style: {line_style(horz_style)},
                    labelBackgroundColor: "{horz_label_background_color}"
                }}
            }}}})''')

    def watermark(self, text: str, font_size: int = 44, color: str = 'rgba(180, 180, 200, 0.5)'):
        """
        Adds a watermark to the chart.
        """
        self.run_script(f'''
          {self.id}.chart.applyOptions({{
              watermark: {{
                  visible: true,
                  fontSize: {font_size},
                  horzAlign: 'center',
                  vertAlign: 'center',
                  color: '{color}',
                  text: '{text}',
              }}
          }})''')

    def legend(self, visible: bool = False, ohlc: bool = True, percent: bool = True, lines: bool = True, color: str = 'rgb(191, 195, 203)',
               font_size: int = 11, font_family: str = 'Monaco'):
        """
        Configures the legend of the chart.
        """
        if not visible:
            return
        self.run_script(f'''
        {self.id}.legend = new Legend({self.id}, {jbool(ohlc)}, {jbool(percent)}, {jbool(lines)}, '{color}', {font_size}, '{font_family}')
        ''')

    def spinner(self, visible): self.run_script(f"{self.id}.spinner.style.display = '{'block' if visible else 'none'}'")

    def screenshot(self) -> bytes:
        """
        Takes a screenshot. This method can only be used after the chart window is visible.
        :return: a bytes object containing a screenshot of the chart.
        """
        self.run_script(f'''
            let canvas = {self.id}.chart.takeScreenshot()
            canvas.toBlob(function(blob) {{
                const reader = new FileReader();
                reader.onload = function(event) {{
                    window.callbackFunction(`return_~_{self.id}_~_${{event.target.result}}`)
                }};
                reader.readAsDataURL(blob);
            }})
            ''')
        serial_data = self._return_q.get()
        return b64decode(serial_data.split(',')[1])

    def hotkey(self, modifier_key: Literal['ctrl', 'alt', 'shift', 'meta'], keys: Union[str, tuple, int], func: callable):
        if not isinstance(keys, tuple): keys = (keys,)
        for key in keys:
            key_code = 'Key' + key.upper() if isinstance(key, str) else 'Digit' + str(key)
            self.run_script(f'''
            {self.id}.commandFunctions.unshift((event) => {{
                if (event.{modifier_key + 'Key'} && event.code === '{key_code}') {{
                    event.preventDefault()
                    window.callbackFunction(`{modifier_key, keys}_~_{key}`)
                    return true
                }}
                else return false
            }})''')
        self._handlers[f'{modifier_key, keys}'] = func

    def create_table(self, width: Union[float, int], height: Union[float, int], headings: tuple, widths: tuple = None, alignments: tuple = None,
                     position: str = 'left', draggable: bool = False, func: callable = None) -> Table:
        return Table(self, width, height, headings, widths, alignments, position, draggable, func)

    def create_subchart(self, position: Literal['left', 'right', 'top', 'bottom'] = 'left', width: float = 0.5, height: float = 0.5,
                        sync: Union[bool, str] = False, scale_candles_only: bool = False, toolbox: bool = False):
        return SubChart(self, position, width, height, sync, scale_candles_only, toolbox)


class SubChart(LWC):
    def __init__(self, parent, position, width, height, sync, scale_candles_only, toolbox):
        self._chart = parent._chart if isinstance(parent, SubChart) else parent
        super().__init__(width, height, scale_candles_only, toolbox, _run_script=self._chart.run_script)
        self._parent = parent
        self._position = position
        self._return_q = self._chart._return_q
        for key, val in self._handlers.items():
            self._chart._handlers[key] = val
        self._handlers = self._chart._handlers
        self.polygon = self._chart.polygon._subchart(self)

        if not sync:
            return
        sync_parent_id = self._parent.id if isinstance(sync, bool) else sync
        self.run_script(f'''
            {sync_parent_id}.chart.timeScale().subscribeVisibleLogicalRangeChange((timeRange) => {{
                {self.id}.chart.timeScale().setVisibleLogicalRange(timeRange)
            }});
            syncCrosshairs({self.id}.chart, {sync_parent_id}.chart)
        ''')
        self.run_script(f'''
        {self.id}.chart.timeScale().setVisibleLogicalRange({sync_parent_id}.chart.timeScale().getVisibleLogicalRange())
        ''', run_last=True)
