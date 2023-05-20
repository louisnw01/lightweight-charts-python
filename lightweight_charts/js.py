import pandas as pd
from uuid import UUID, uuid4
from datetime import timedelta, datetime
from typing import Dict, Union, Literal

from lightweight_charts.pkg import LWC_3_5_0
from lightweight_charts.util import LINE_TYPE, POSITION, SHAPE, CROSSHAIR_MODE, _crosshair_mode, _line_type, \
    MissingColumn, _js_bool, _price_scale_mode, PRICE_SCALE_MODE, _position, _shape, IDGen, _valid_color


class Line:
    def __init__(self, lwc, line_id, color, width):
        self._lwc = lwc
        self.loaded = False
        self.id = line_id
        self.color = color
        self.width = width

    def set(self, data: pd.DataFrame):
        """
        Sets the line data.\n
        :param data: columns: date/time, price
        """
        self._lwc._set_line_data(self.id, data)

    def update(self, series: pd.Series):
        """
        Updates the line data.\n
        :param series: labels: date/time, price
        """
        self._lwc._update_line_data(self.id, series)


class API:
    def __init__(self):
        self.click_funcs = {}

    def onClick(self, data):
        click_func = self.click_funcs[data['id']]
        if isinstance(data['time'], int):
            data['time'] = datetime.fromtimestamp(data['time'])
        else:
            data['time'] = datetime(data['time']['year'], data['time']['month'], data['time']['day'])
        click_func(data) if click_func else None


class LWC:
    def __init__(self, volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0):
        self.id = uuid4()
        self.js_queue = []
        self.loaded = False

        self._rand = IDGen()
        self._chart_var = 'chart'

        self._js_api = API()
        self._js_api_code = ''

        self.volume_enabled = volume_enabled
        self.inner_width = inner_width
        self.inner_height = inner_height
        self._html = HTML.replace('__INNER_WIDTH__', str(self.inner_width)).replace('__INNER_HEIGHT__', str(self.inner_height))

        self.last_bar = None
        self.interval = None
        self._lines: Dict[UUID, Line] = {}
        self._subcharts: Dict[UUID, LWC] = {self.id: self}

        self.background_color = '#000000'
        self.volume_up_color = 'rgba(83,141,131,0.8)'
        self.volume_down_color = 'rgba(200,127,130,0.8)'

    def _on_js_load(self): pass

    def _stored(self, func, *args, **kwargs):
        if self.loaded:
            return False
        self.js_queue.append((func, args, kwargs))
        return True

    def _set_last_bar(self, bar: pd.Series): self.last_bar = bar

    def _set_interval(self, df: pd.DataFrame):
        df['time'] = pd.to_datetime(df['time'])
        intervals = df['time'].diff()
        counts = intervals.value_counts()
        self.interval = counts.index[0]

    def _df_datetime_format(self, df: pd.DataFrame):
        if 'date' in df.columns:
            df = df.rename(columns={'date': 'time'})
        self._set_interval(df)
        df['time'] = df['time'].apply(self._datetime_format)
        return df

    def _series_datetime_format(self, series):
        if 'date' in series.keys():
            series = series.rename({'date': 'time'})
        series['time'] = self._datetime_format(series['time'])
        return series

    def _datetime_format(self, string):
        string = pd.to_datetime(string)
        if self.interval != timedelta(days=1):
            string = string.timestamp()
            string = self.interval.total_seconds() * (string // self.interval.total_seconds())
        else:
            string = string.strftime('%Y-%m-%d')
        return string

    def run_script(self, script): pass

    def set(self, df: pd.DataFrame):
        """
        Sets the initial data for the chart.\n
        :param df: columns: date/time, open, high, low, close, volume (if volume enabled).
        """
        if self._stored('set', df):
            return None

        df = self._df_datetime_format(df)
        self._set_last_bar(df.iloc[-1])
        bars = df
        if self.volume_enabled:
            if 'volume' not in df:
                raise MissingColumn("Volume enabled, but 'volume' column was not found.")

            volume = df.drop(columns=['open', 'high', 'low', 'close'])
            volume = volume.rename(columns={'volume': 'value'})
            volume['color'] = self.volume_down_color
            volume.loc[df['close'] > df['open'], 'color'] = self.volume_up_color

            self.run_script(f'{self._chart_var}.volumeSeries.setData({volume.to_dict(orient="records")})')
            bars = df.drop(columns=['volume'])

        bars = bars.to_dict(orient='records')
        self.run_script(f'{self._chart_var}.series.setData({bars})')

    def update(self, series, from_tick=False):
        """
        Updates the data from a bar;
        if series['time'] is the same time as the last bar, the last bar will be overwritten.\n
        :param series: columns: date/time, open, high, low, close, volume (if volume enabled).
        """
        if self._stored('update', series, from_tick):
            return None

        series = self._series_datetime_format(series) if not from_tick else series
        self._set_last_bar(series)
        if self.volume_enabled:
            if 'volume' not in series:
                raise MissingColumn("Volume enabled, but 'volume' column was not found.")

            volume = series.drop(['open', 'high', 'low', 'close'])
            volume = volume.rename({'volume': 'value'})
            volume['color'] = self.volume_up_color if series['close'] > series['open'] else self.volume_down_color
            self.run_script(f'{self._chart_var}.volumeSeries.update({volume.to_dict()})')
            series = series.drop(['volume'])

        dictionary = series.to_dict()
        self.run_script(f'{self._chart_var}.series.update({dictionary})')

    def update_from_tick(self, series):
        """
        Updates the data from a tick.\n
        :param series: columns: date/time, price, volume (if volume enabled).
        """
        if self._stored('update_from_tick', series):
            return None

        series = self._series_datetime_format(series)
        bar = pd.Series()
        if series['time'] == self.last_bar['time']:
            bar = self.last_bar
            bar['high'] = max(self.last_bar['high'], series['price'])
            bar['low'] = min(self.last_bar['low'], series['price'])
            bar['close'] = series['price']
            if self.volume_enabled:
                if 'volume' not in series:
                    raise MissingColumn("Volume enabled, but 'volume' column was not found.")
                bar['volume'] = series['volume']
        else:
            for key in ('open', 'high', 'low', 'close'):
                bar[key] = series['price']
            bar['time'] = series['time']
            bar['volume'] = 0
        self.update(bar, from_tick=True)

    def create_line(self, color: str = 'rgba(214, 237, 255, 0.6)', width: int = 2):
        """
        Creates and returns a Line object.)\n
        :return a Line object used to set/update the line.
        """
        line_id = uuid4()
        self._lines[line_id] = Line(self, line_id, color, width)
        return self._lines[line_id]

    def _set_line_data(self, line_id, df: pd.DataFrame):
        if self._stored('_set_line_data', line_id, df):
            return None
        line = self._lines[line_id]

        if not line.loaded:
            var = self._rand.generate()
            self.run_script(f'''
            let lineSeries{var} = {{
                    color: '{line.color}',
                    lineWidth: {line.width},
                    }};
            let line{var} = {{
                series: {self._chart_var}.chart.addLineSeries(lineSeries{var}),
                id: '{line_id}',
            }};
            lines.push(line{var})
                ''')
            line.loaded = True
        df = self._df_datetime_format(df)
        self.run_script(f'''
        lines.forEach(function (line) {{
            if ('{line_id}' === line.id) {{
                line.series.setData({df.to_dict('records')})
            }}
        }})''')

    def _update_line_data(self, line_id, series: pd.Series):
        if self._stored('_update_line_data', line_id, series):
            return None

        series = self._series_datetime_format(series)
        self.run_script(f'''
        lines.forEach(function (line) {{
            if ('{line_id}' === line.id) {{
                line.series.update({series.to_dict()})
            }}
        }})''')

    def marker(self, time: datetime = None, position: POSITION = 'below', shape: SHAPE = 'arrow_up',
               color: str = '#2196F3', text: str = '', m_id: UUID = None) -> UUID:
        """
        Creates a new marker.\n
        :param time: The time that the marker will be placed at. If no time is given, it will be placed at the last bar.
        :param position: The position of the marker.
        :param color: The color of the marker (rgb, rgba or hex).
        :param shape: The shape of the marker.
        :param text: The text to be placed with the marker.
        :return: The UUID of the marker placed.
        """
        _valid_color(color)
        if not m_id:
            m_id = uuid4()
        if self._stored('marker', time, position, shape, color, text, m_id):
            return m_id

        try:
            time = self.last_bar['time'] if not time else self._datetime_format(time)
        except TypeError:
            raise TypeError('Chart marker created before data was set.')
        time = time if isinstance(time, float) else f"'{time}'"

        self.run_script(f"""
                markers.push({{
                    time: {time},
                    position: '{_position(position)}',
                    color: '{color}', shape: '{_shape(shape)}',
                    text: '{text}',
                    id: '{m_id}'
                    }});
                {self._chart_var}.series.setMarkers(markers)""")
        return m_id

    def remove_marker(self, m_id: UUID):
        """
        Removes the marker with the given UUID.\n
        """
        if self._stored('remove_marker', m_id):
            return None

        self.run_script(f'''
               markers.forEach(function (marker) {{
                   if ('{m_id}' === marker.id) {{
                       markers.splice(markers.indexOf(marker), 1)
                       {self._chart_var}.series.setMarkers(markers)
                       }}
                   }});''')

    def horizontal_line(self, price: Union[float, int], color: str = 'rgb(122, 146, 202)', width: int = 1,
                        style: LINE_TYPE = 'solid', text: str = '', axis_label_visible=True):
        """
        Creates a horizontal line at the given price.\n
        """
        if self._stored('horizontal_line', price, color, width, style, text, axis_label_visible):
            return None

        var = self._rand.generate()
        self.run_script(f"""
               let priceLine{var} = {{
                   price: {price},
                   color: '{color}',
                   lineWidth: {width},
                   lineStyle: LightweightCharts.LineStyle.{_line_type(style)},
                   axisLabelVisible: {'true' if axis_label_visible else 'false'},
                   title: '{text}',
               }};
               let line{var} = {{
                   line: {self._chart_var}.series.createPriceLine(priceLine{var}),
                   price: {price},
               }};
               horizontal_lines.push(line{var})""")

    def remove_horizontal_line(self, price: Union[float, int]):
        """
        Removes a horizontal line at the given price.
        """
        if self._stored('remove_horizontal_line', price):
            return None

        self.run_script(f'''
               horizontal_lines.forEach(function (line) {{
               if ({price} === line.price) {{
                   {self._chart_var}.series.removePriceLine(line.line);
                   horizontal_lines.splice(horizontal_lines.indexOf(line), 1)
                   }}
               }});''')

    def config(self, mode: PRICE_SCALE_MODE = None, title: str = None, right_padding: float = None):
        """
        :param mode: Chart price scale mode.
        :param title: Last price label text.
        :param right_padding: How many bars of empty space to the right of the last bar.
        """
        if self._stored('config', mode, title, right_padding):
            return None

        self.run_script(f'{self._chart_var}.chart.timeScale().scrollToPosition({right_padding}, false)') if right_padding is not None else None
        self.run_script(f'{self._chart_var}.series.applyOptions({{title: "{title}"}})') if title else None
        self.run_script(
            f"{self._chart_var}.chart.priceScale().applyOptions({{mode: LightweightCharts.PriceScaleMode.{_price_scale_mode(mode)}}})") if mode else None

    def time_scale(self, visible: bool = True, time_visible: bool = True, seconds_visible: bool = False):
        """
        Options for the time scale of the chart.
        :param visible: Time scale visibility control.
        :param time_visible: Time visibility control.
        :param seconds_visible: Seconds visibility control.
        :return:
        """
        if self._stored('time_scale', visible, time_visible, seconds_visible):
            return None

        time_scale_visible = f'visible: {_js_bool(visible)},'
        time = f'timeVisible: {_js_bool(time_visible)},'
        seconds = f'secondsVisible: {_js_bool(seconds_visible)},'
        self.run_script(f'''
           {self._chart_var}.chart.applyOptions({{
               timeScale: {{
               {time_scale_visible if visible is not None else ''}
               {time if time_visible is not None else ''}
               {seconds if seconds_visible is not None else ''}
               }}
           }})''')

    def layout(self, background_color: str = None, text_color: str = None, font_size: int = None,
               font_family: str = None):
        """
        Global layout options for the chart.
        """
        if self._stored('layout', background_color, text_color, font_size, font_family):
            return None

        self.background_color = background_color if background_color else self.background_color
        self.run_script(f"""
            document.body.style.backgroundColor = '{self.background_color}'
            {self._chart_var}.chart.applyOptions({{
            layout: {{
                {f'backgroundColor: "{background_color}",' if background_color else ''}
                {f'textColor: "{text_color}",' if text_color else ''}
                {f'fontSize: {font_size},' if font_size else ''}
                {f'fontFamily: "{font_family}",' if font_family else ''}
            }}}})""")

    def grid(self, vert_enabled: bool = True, horz_enabled: bool = True, color: str = 'rgba(29, 30, 38, 5)', style: LINE_TYPE = 'solid'):
        """
        Grid styling for the chart.
        """
        if self._stored('grid', vert_enabled, horz_enabled, color, style):
            return None

        self.run_script(f"""
        {self._chart_var}.chart.applyOptions({{
        grid: {{
            {f'''vertLines: {{
                {f'visible: {_js_bool(vert_enabled)},' if vert_enabled is not None else ''}
                {f'color: "{color}",' if color else ''}
                {f'style: LightweightCharts.LineStyle.{_line_type(style)},' if style else ''}
            }},''' if vert_enabled is not None or color or style else ''}
            
            {f'''horzLines: {{
                {f'visible: {_js_bool(horz_enabled)},' if horz_enabled is not None else ''}
                {f'color: "{color}",' if color else ''}
                {f'style: LightweightCharts.LineStyle.{_line_type(style)},' if style else ''}
            }},''' if horz_enabled is not None or color or style else ''}
        }}
        }})
        """)

    def candle_style(self, up_color: str = 'rgba(39, 157, 130, 100)', down_color: str = 'rgba(200, 97, 100, 100)',
                     wick_enabled: bool = True, border_enabled: bool = True, border_up_color: str = '',
                     border_down_color: str = '', wick_up_color: str = '', wick_down_color: str = ''):
        """
        Candle styling for each of its parts.
        """
        if self._stored('candle_style', up_color, down_color, wick_enabled, border_enabled,
                        border_up_color, border_down_color, wick_up_color, wick_down_color):
            return None

        self.run_script(f"""
            {self._chart_var}.series.applyOptions({{
                {f'upColor: "{up_color}",' if up_color else ''}
                {f'downColor: "{down_color}",' if down_color else ''}
                {f'wickVisible: {_js_bool(wick_enabled)},' if wick_enabled is not None else ''}
                {f'borderVisible: {_js_bool(border_enabled)},' if border_enabled is not None else ''}
                {f'borderUpColor: "{border_up_color}",' if border_up_color else ''}
                {f'borderDownColor: "{border_down_color}",' if border_down_color else ''}
                {f'wickUpColor: "{wick_up_color}",' if wick_up_color else ''}
                {f'wickDownColor: "{wick_down_color}",' if wick_down_color else ''}
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
        if self._stored('volume_config', scale_margin_top, scale_margin_bottom, up_color, down_color):
            return None

        self.volume_up_color = up_color if up_color else self.volume_up_color
        self.volume_down_color = down_color if down_color else self.volume_down_color
        self.run_script(f'''
        {self._chart_var}.volumeSeries.priceScale().applyOptions({{
            scaleMargins: {{
            top: {scale_margin_top},
            bottom: {scale_margin_bottom},
            }}
        }})''')

    def crosshair(self, mode: CROSSHAIR_MODE = 'normal', vert_width: int = 1, vert_color: str = None,
                  vert_style: LINE_TYPE = None, vert_label_background_color: str = None, horz_width: int = 1,
                  horz_color: str = None, horz_style: LINE_TYPE = None, horz_label_background_color: str = None):
        """
        Crosshair formatting for its vertical and horizontal axes.
        """
        if self._stored('crosshair', mode, vert_width, vert_color, vert_style, vert_label_background_color,
                        horz_width, horz_color, horz_style, horz_label_background_color):
            return None

        args = f"LightweightCharts.CrosshairMode.{_crosshair_mode(mode)}", \
               f"{vert_width}}}", f"'{vert_color}'}}", f"LightweightCharts.LineStyle.{_line_type(vert_style)}}}",\
               f"'{vert_label_background_color}'}}", \
               f"{horz_width}}}", f"'{horz_color}'}}", f"LightweightCharts.LineStyle.{_line_type(horz_style)}}}",\
               f"'{horz_label_background_color}'}}"
        for key, arg in zip(
                ('mode', 'vertLine: {width', 'vertLine: {color', 'vertLine: {style', 'vertLine: {labelBackgroundColor',
                 'horzLine: {width', 'horzLine: {color', 'horzLine: {style', 'horzLine: {labelBackgroundColor'), args):
            if 'None' in arg:
                continue
            self.run_script(f'''
            {self._chart_var}.chart.applyOptions({{
                crosshair: {{
                    {key}: {arg}
            }}}})''')

    def watermark(self, text: str, font_size: int = 44, color: str = 'rgba(180, 180, 200, 0.5)'):
        """
        Adds a watermark to the chart.
        """
        if self._stored('watermark', text, font_size, color):
            return None

        self.run_script(f'''
          {self._chart_var}.chart.applyOptions({{
              watermark: {{
                  visible: true,
                  fontSize: {font_size},
                  horzAlign: 'center',
                  vertAlign: 'center',
                  color: '{color}',
                  text: '{text}',
              }}
          }})''')

    def legend(self, visible: bool = False, ohlc: bool = True, percent: bool = True, color: str = None,
               font_size: int = None, font_family: str = None):
        """
        Configures the legend of the chart.
        """
        if self._stored('legend', visible, ohlc, percent, color, font_size, font_family):
            return None

        if visible:
            self.run_script(f'''
            {f"{self._chart_var}.legend.style.color = '{color}'" if color else ''}
            {f"{self._chart_var}.legend.style.fontSize = {font_size}" if font_size else ''}
            {f"{self._chart_var}.legend.style.fontFamily = '{font_family}'" if font_family else ''}
            
            {self._chart_var}.chart.subscribeCrosshairMove((param) => {{   
                if (param.time){{
                    const data = param.seriesPrices.get({self._chart_var}.series);
                    if (!data) {{return}}
                    let percentMove = ((data.close-data.open)/data.open)*100
                    let ohlc = `open: ${{legendItemFormat(data.open)}} 
                                | high: ${{legendItemFormat(data.high)}} 
                                | low: ${{legendItemFormat(data.low)}}
                                | close: ${{legendItemFormat(data.close)}} `
                    let percent = `| daily: ${{percentMove >= 0 ? '+' : ''}}${{percentMove.toFixed(2)}} %`
                    let finalString = ''
                    {'finalString += ohlc' if ohlc else ''}
                    {'finalString += percent' if percent else ''}
                    {self._chart_var}.legend.innerHTML = finalString
                }}
                else {{
                    {self._chart_var}.legend.innerHTML = ''
                }}
            }});''')

    def subscribe_click(self, function: object):
        if self._stored('subscribe_click', function):
            return None

        self._js_api.click_funcs[str(self.id)] = function
        var = self._rand.generate()
        self.run_script(f'''
            {self._chart_var}.chart.subscribeClick((param) => {{
                if (!param.point) {{return}}
                let prices{var} = param.seriesPrices.get({self._chart_var}.series);
                let data{var} = {{
                    time: param.time,
                    open: prices{var}.open,
                    high: prices{var}.high,
                    low: prices{var}.low,
                    close: prices{var}.close,
                    id: '{self.id}'
                    }}
                {self._js_api_code}(data{var})
                }})''')

    def create_subchart(self, volume_enabled: bool = True, position: Literal['left', 'right', 'top', 'bottom'] = 'left',
                         width: float = 0.5, height: float = 0.5, sync: Union[bool, UUID] = False):
        subchart = SubChart(self, volume_enabled, position, width, height, sync)
        self._subcharts[subchart.id] = subchart
        return subchart

    def _pywebview_subchart(self, volume_enabled, position, width, height, sync, parent=None):
        subchart = PyWebViewSubChart(self if not parent else parent, volume_enabled, position, width, height, sync)
        self._subcharts[subchart.id] = subchart
        return subchart.id


class SubChart(LWC):
    def __init__(self, parent, volume_enabled, position, width, height, sync):
        super().__init__(volume_enabled, width, height)
        self._chart = parent._chart if isinstance(parent, SubChart) else parent
        self._parent = parent

        self._rand = self._chart._rand
        self._chart_var = f'window.{self._rand.generate()}'
        self._js_api = self._chart._js_api
        self._js_api_code = self._chart._js_api_code

        self.position = position

        self._create_panel(sync)

    def _stored(self, func, *args, **kwargs):
        if self._chart.loaded:
            return False
        self._chart.js_queue.append((f'SUB{func}', (self.id,)+args, kwargs))
        return True

    def run_script(self, script): self._chart.run_script(script)

    def _create_panel(self, sync):
        if self._stored('_create_panel', sync):
            return None

        parent_div = 'chartsDiv' if self._parent._chart_var == 'chart' else self._parent._chart_var+'div'

        sub_sync = ''
        if sync:
            sync_parent_var = self._chart._subcharts[sync]._chart_var if isinstance(sync, UUID) else self._parent._chart_var
            sub_sync = f'''
                {sync_parent_var}.chart.timeScale().subscribeVisibleLogicalRangeChange((timeRange) => {{
                    {self._chart_var}.chart.timeScale().setVisibleLogicalRange(timeRange)
                }});
            '''
        self.run_script(f'''
            {self._chart_var}div = document.createElement('div')
            //{self._chart_var}div.style.position = 'relative'
            {self._chart_var}div.style.float = "{self.position}"
            
            //chartsDiv.style.display = 'inline-block'
            chartsDiv.style.float = 'left'
            
            {self._chart_var} = {{}}
            {self._chart_var}.scale = {{
                width: {self.inner_width},
                height: {self.inner_height}
            }}
            {self._chart_var}.chart = makeChart(window.innerWidth*{self._chart_var}.scale.width,
                                        window.innerHeight*{self._chart_var}.scale.height, {self._chart_var}div)
            {self._chart_var}.series = makeCandlestickSeries({self._chart_var}.chart)
            {self._chart_var}.volumeSeries = makeVolumeSeries({self._chart_var}.chart)
    
            {self._chart_var}.legend = document.createElement('div')
            {self._chart_var}.legend.style.position = 'absolute'
            {self._chart_var}.legend.style.zIndex = 1000
            {self._chart_var}.legend.style.width = '{(self.inner_width*100)-8}vw'
            {self._chart_var}.legend.style.top = '10px'
            {self._chart_var}.legend.style.left = '10px'
            {self._chart_var}.legend.style.fontFamily = 'Monaco'
            {self._chart_var}.legend.style.fontSize = '11px'
            {self._chart_var}.legend.style.color = 'rgb(191, 195, 203)'
            {self._chart_var}div.appendChild({self._chart_var}.legend)
            
            {parent_div}.parentNode.insertBefore({self._chart_var}div, {parent_div}.nextSibling)
            charts.push({self._chart_var})
            
            {self._chart_var}.chart.priceScale('').applyOptions({{
             scaleMargins: {{
                top: 0.8,
                bottom: 0,
                }}
            }});
            {sub_sync}
            ''')


class PyWebViewSubChart(SubChart):
    def create_subchart(self, volume_enabled: bool = True, position: Literal['left', 'right', 'top', 'bottom'] = 'left',
                         width: float = 0.5, height: float = 0.5, sync: Union[bool, UUID] = False):
        return self._chart._pywebview_subchart(volume_enabled, position, width, height, sync, parent=self)

    def create_line(self, color: str = 'rgba(214, 237, 255, 0.6)', width: int = 2):
        return super().create_line(color, width).id


SCRIPT = """
document.body.style.backgroundColor = '#000000'

const markers = []
const horizontal_lines = []
const lines = []
const charts = []

const up = 'rgba(39, 157, 130, 100)'
const down = 'rgba(200, 97, 100, 100)'


function makeChart(width, height, div) {
    return LightweightCharts.createChart(div, {
        width: width,
        height: height,
        layout: {
            textColor: '#d1d4dc',
            backgroundColor: '#000000',
            fontSize: 12,
        },
        rightPriceScale: {
            scaleMargins: {
                top: 0.3,
                bottom: 0.25,
            },
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        grid: {
            vertLines: {
                color: 'rgba(29, 30, 38, 5)',
            },
            horzLines: {
                color: 'rgba(29, 30, 58, 5)',
            },
        },
        handleScroll: {
            vertTouchDrag: true,
        },
    })
}
function makeCandlestickSeries(chart){
    return chart.addCandlestickSeries({
        color: 'rgb(0, 120, 255)',
        upColor: up,
        borderUpColor: up,
        wickUpColor: up,
    
        downColor: down,
        borderDownColor: down,
        wickDownColor: down,
        lineWidth: 2,
    })
}

function makeVolumeSeries(chart) {
    return chart.addHistogramSeries({
    color: '#26a69a',
    priceFormat: {
        type: 'volume',
    },
    priceScaleId: '',
});
}

const chartsDiv = document.createElement('div')

var chart = {}
chart.scale = {
    width: __INNER_WIDTH__,
    height: __INNER_HEIGHT__
}
chart.chart = makeChart(window.innerWidth*chart.scale.width, window.innerHeight*chart.scale.height, chartsDiv)
chart.series = makeCandlestickSeries(chart.chart)
chart.volumeSeries = makeVolumeSeries(chart.chart)

            
document.body.appendChild(chartsDiv)

chart.legend = document.createElement('div')
chart.legend.style.position = 'absolute'
chart.legend.style.zIndex = 1000
chart.legend.style.width = `${(chart.scale.width*100)-8}vw`
chart.legend.style.top = '10px'
chart.legend.style.left = '10px'
chart.legend.style.fontFamily = 'Monaco'
chart.legend.style.fontSize = '11px'
chart.legend.style.color = 'rgb(191, 195, 203)'
document.body.appendChild(chart.legend)

chart.chart.priceScale('').applyOptions({
    scaleMargins: {
        top: 0.8,
        bottom: 0,
    }
});

window.addEventListener('resize', function() {
    let width = window.innerWidth;
    let height = window.innerHeight;
    chart.chart.resize(width*chart.scale.width, height*chart.scale.height)
    
    charts.forEach(function (subchart) {{
        subchart.chart.resize(width*subchart.scale.width, height*subchart.scale.height)
        }});
    
});

function legendItemFormat(num) {
    return num.toFixed(2).toString().padStart(8, ' ')
}

"""

HTML = f"""
<!DOCTYPE html>
<html lang="">
<head>
    <title>lightweight-charts-python</title>
    <script>{LWC_3_5_0}</script>
    <meta name="viewport" content ="width=device-width, initial-scale=1">
    <style>
    body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
    }}
    </style>
</head>
<body>
<div id="chart"></div>
<script>
{SCRIPT}
</script>
</body>
</html>"""
