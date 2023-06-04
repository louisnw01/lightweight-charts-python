import pandas as pd
from datetime import timedelta, datetime
from typing import Union, Literal, Dict

from lightweight_charts.pkg import LWC_4_0_1
from lightweight_charts.util import LINE_STYLE, MARKER_POSITION, MARKER_SHAPE, CROSSHAIR_MODE, _crosshair_mode, _line_style, \
    MissingColumn, _js_bool, _price_scale_mode, PRICE_SCALE_MODE, _marker_position, _marker_shape, IDGen


class SeriesCommon:
    def _set_interval(self, df: pd.DataFrame):
        common_interval = pd.to_datetime(df['time']).diff().value_counts()
        self._interval = common_interval.index[0]

    def _df_datetime_format(self, df: pd.DataFrame):
        df = df.copy()
        if 'date' in df.columns:
            df = df.rename(columns={'date': 'time'})
        self._set_interval(df)
        df['time'] = self._datetime_format(df['time'])
        return df

    def _series_datetime_format(self, series):
        series = series.copy()
        if 'date' in series.keys():
            series = series.rename({'date': 'time'})
        series['time'] = self._datetime_format(series['time'])
        return series

    def _datetime_format(self, arg: Union[pd.Series, str]):
        arg = pd.to_datetime(arg)
        if self._interval != timedelta(days=1):
            arg = arg.astype('int64') // 10 ** 9 if isinstance(arg, pd.Series) else arg.timestamp()
            arg = self._interval.total_seconds() * (arg // self._interval.total_seconds())
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
                position: '{_marker_position(position)}',
                color: '{color}',
                shape: '{_marker_shape(shape)}',
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

    def horizontal_line(self, price: Union[float, int], color: str = 'rgb(122, 146, 202)', width: int = 1,
                        style: LINE_STYLE = 'solid', text: str = '', axis_label_visible=True):
        """
        Creates a horizontal line at the given price.\n
        """
        self.run_script(f"""
        makeHorizontalLine({self.id}, {price}, '{color}', {width}, {_line_style(style)}, {_js_bool(axis_label_visible)}, '{text}')
        """)

    def remove_horizontal_line(self, price: Union[float, int]):
        """
        Removes a horizontal line at the given price.
        """
        self.run_script(f'''
           {self.id}.horizontal_lines.forEach(function (line) {{
           if ({price} === line.price) {{
               {self.id}.series.removePriceLine(line.line);
               {self.id}.horizontal_lines.splice({self.id}.horizontal_lines.indexOf(line), 1)
               }}
           }});''')

    def title(self, title: str):
        self.run_script(f'{self.id}.series.applyOptions({{title: "{title}"}})')


class Line(SeriesCommon):
    def __init__(self, parent, color, width):
        self._parent = parent
        self._rand = self._parent._rand
        self.id = f'window.{self._rand.generate()}'
        self.run_script = self._parent.run_script

        self._parent.run_script(f'''
            {self.id} = {{
                series: {self._parent.id}.chart.addLineSeries({{
                    color: '{color}',
                    lineWidth: {width},
                }}),
                markers: [],
                horizontal_lines: [],
            }}
        ''')

    def set(self, data: pd.DataFrame):
        """
        Sets the line data.\n
        :param data: columns: date/time, value
        """
        df = self._parent._df_datetime_format(data)
        self._last_bar = df.iloc[-1]
        self.run_script(f'{self.id}.series.setData({df.to_dict("records")})')

    def update(self, series: pd.Series):
        """
        Updates the line data.\n
        :param series: labels: date/time, value
        """
        series = self._parent._series_datetime_format(series)
        self._last_bar = series
        self.run_script(f'{self.id}.series.update({series.to_dict()})')


class Widget:
    def __init__(self, chart):
        self._chart = chart
        self.method = None


class TextWidget(Widget):
    def __init__(self, chart, initial_text):
        super().__init__(chart)
        self.value = initial_text
        self.id = f"window.{self._chart._rand.generate()}"
        self._chart.run_script(f'''{self.id} = makeTextBoxWidget({self._chart.id}, "{initial_text}")''')

    def set(self, string):
        self.value = string
        self._chart.run_script(f'{self.id}.innerText = "{string}"')


class SwitcherWidget(Widget):
    def __init__(self, chart, method, *options, default):
        super().__init__(chart)
        self.value = default
        self.method = method.__name__
        self._chart.run_script(f'''
            makeSwitcher({self._chart.id}, {list(options)}, '{default}', {self._chart._js_api_code}, '{method.__name__}')
            {self._chart.id}.chart.resize(window.innerWidth*{self._chart._inner_width}, (window.innerHeight*{self._chart._inner_height})-{self._chart.id}.topBar.offsetHeight)
        ''')


class TopBar:
    def __init__(self, chart):
        self._chart = chart
        self._widgets: Dict[str, Widget] = {}
        self._chart.run_script(f'''
            makeTopBar({self._chart.id})
            {self._chart.id}.chart.resize(window.innerWidth*{self._chart._inner_width}, (window.innerHeight*{self._chart._inner_height})-{self._chart.id}.topBar.offsetHeight)
        ''')

    def __getitem__(self, item): return self._widgets.get(item)

    def switcher(self, name, method, *options, default=None):
        self._widgets[name] = SwitcherWidget(self._chart, method, *options, default=default if default else options[0])

    def textbox(self, name, initial_text=''): self._widgets[name] = TextWidget(self._chart, initial_text)

    def _widget_with_method(self, method_name):
        for widget in self._widgets.values():
            if widget.method == method_name:
                return widget


class LWC(SeriesCommon):
    def __init__(self, volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0, dynamic_loading: bool = False):
        self._volume_enabled = volume_enabled
        self._inner_width = inner_width
        self._inner_height = inner_height
        self._dynamic_loading = dynamic_loading

        self._rand = IDGen()
        self.id = f'window.{self._rand.generate()}'
        self._position = 'left'
        self.loaded = False
        self._html = HTML
        self._scripts = []
        self._script_func = None
        self._last_bar = None
        self._interval = None
        self._charts = {self.id: self}
        self._js_api_code = None

        self._background_color = '#000000'
        self._volume_up_color = 'rgba(83,141,131,0.8)'
        self._volume_down_color = 'rgba(200,127,130,0.8)'

        # self.polygon: PolygonAPI = PolygonAPI(self)

    def _on_js_load(self):
        if self.loaded:
            return
        self.loaded = True
        [self.run_script(script) for script in self._scripts]

    def _create_chart(self, autosize=True):
        self.run_script(f'''
            {self.id} = makeChart({self._inner_width}, {self._inner_height}, autoSize={_js_bool(autosize)})
            {self.id}.id = '{self.id}'
            {self.id}.wrapper.style.float = "{self._position}"
            ''')

    def _make_search_box(self):
        self.run_script(f'makeSearchBox({self.id}, {self._js_api_code})')

    def run_script(self, script):
        """
        For advanced users; evaluates JavaScript within the Webview.
        """
        self._script_func(script) if self.loaded else self._scripts.append(script)

    def set(self, df: pd.DataFrame):
        """
        Sets the initial data for the chart.\n
        :param df: columns: date/time, open, high, low, close, volume (if volume enabled).
        """
        bars = self._df_datetime_format(df)
        self._last_bar = bars.iloc[-1]
        if self._volume_enabled:
            if 'volume' not in bars:
                raise MissingColumn("Volume enabled, but 'volume' column was not found.")

            volume = bars.drop(columns=['open', 'high', 'low', 'close']).rename(columns={'volume': 'value'})
            volume['color'] = self._volume_down_color
            volume.loc[bars['close'] > bars['open'], 'color'] = self._volume_up_color
            self.run_script(f'{self.id}.volumeSeries.setData({volume.to_dict(orient="records")})')
            bars = bars.drop(columns=['volume'])

        bars = bars.to_dict(orient='records')
        self.run_script(f'''
            {self.id}.candleData = {bars}
            {self.id}.shownData = ({self.id}.candleData.length >= 190) ? {self.id}.candleData.slice(-190) : {self.id}.candleData
            {self.id}.series.setData({self.id}.shownData);
            
            var timer = null;
            {self.id}.chart.timeScale().subscribeVisibleLogicalRangeChange(() => {{
                if (timer !== null) {{
                    return;
                }}
                timer = setTimeout(() => {{
                let chart = {self.id}
                let logicalRange = chart.chart.timeScale().getVisibleLogicalRange();
                if (logicalRange !== null) {{
                    let barsInfo = chart.series.barsInLogicalRange(logicalRange);
                    if (barsInfo === null || barsInfo.barsBefore === null || barsInfo.barsAfter === null) {{return}}
                    if (barsInfo !== null && barsInfo.barsBefore < 20 || barsInfo.barsAfter < 20) {{
                        let newBeginning = chart.candleData.indexOf(chart.shownData[0])+Math.round(barsInfo.barsBefore)-20
                        let newEnd = chart.candleData.indexOf(chart.shownData[chart.shownData.length-2])-Math.round(barsInfo.barsAfter)+20
                        if (newBeginning < 0) {{
                            newBeginning = 0
                        }}
                        chart.shownData = chart.candleData.slice(newBeginning, newEnd)
                        if (newEnd-17 <= chart.candleData.length-1) {{
                            chart.shownData[chart.shownData.length - 1] = Object.assign({{}}, chart.shownData[chart.shownData.length - 1]);
                            chart.shownData[chart.shownData.length - 1].open = chart.candleData[chart.candleData.length - 1].close;
                            chart.shownData[chart.shownData.length - 1].high = chart.candleData[chart.candleData.length - 1].close;
                            chart.shownData[chart.shownData.length - 1].low = chart.candleData[chart.candleData.length - 1].close;
                            chart.shownData[chart.shownData.length - 1].close = chart.candleData[chart.candleData.length - 1].close;
                            }}
                        chart.series.setData(chart.shownData);
                    }}
                }}
                timer = null;
                }}, 50);
            }});
        ''') if self._dynamic_loading else self.run_script(f'{self.id}.series.setData({bars})')

    def update(self, series, from_tick=False):
        """
        Updates the data from a bar;
        if series['time'] is the same time as the last bar, the last bar will be overwritten.\n
        :param series: labels: date/time, open, high, low, close, volume (if volume enabled).
        """
        series = self._series_datetime_format(series) if not from_tick else series
        self._last_bar = series
        if self._volume_enabled:
            if 'volume' not in series:
                raise MissingColumn("Volume enabled, but 'volume' column was not found.")

            volume = series.drop(['open', 'high', 'low', 'close']).rename({'volume': 'value'})
            volume['color'] = self._volume_up_color if series['close'] > series['open'] else self._volume_down_color
            self.run_script(f'{self.id}.volumeSeries.update({volume.to_dict()})')
            series = series.drop(['volume'])
        bar = series.to_dict()
        self.run_script(f'''
        
            let logicalRange = {self.id}.chart.timeScale().getVisibleLogicalRange();
            let barsInfo = {self.id}.series.barsInLogicalRange(logicalRange);
                
            if ({self.id}.candleData[{self.id}.candleData.length-1].time === {bar['time']}) {{
            
                {self.id}.shownData[{self.id}.shownData.length-1] = {bar}
                {self.id}.candleData[{self.id}.candleData.length-1] = {bar}
            }}
            else {{
                if (barsInfo.barsAfter > 0) {{
                    {self.id}.shownData[{self.id}.shownData.length-1] = {bar}
                }}
                else {{
                    {self.id}.shownData.push({bar})
                }}
                
            {self.id}.candleData.push({bar})
            }}
            {self.id}.series.update({self.id}.shownData[{self.id}.shownData.length-1])
            ''') if self._dynamic_loading else self.run_script(f'{self.id}.series.update({bar})')

    def update_from_tick(self, series):
        """
        Updates the data from a tick.\n
        :param series: labels: date/time, price, volume (if volume enabled).
        """
        series = self._series_datetime_format(series)
        bar = pd.Series()
        if series['time'] == self._last_bar['time']:
            bar = self._last_bar
            bar['high'] = max(self._last_bar['high'], series['price'])
            bar['low'] = min(self._last_bar['low'], series['price'])
            bar['close'] = series['price']
            if self._volume_enabled:
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
        """
        return Line(self, color, width)

    def price_scale(self, mode: PRICE_SCALE_MODE = 'normal', align_labels: bool = True, border_visible: bool = False,
                    border_color: str = None, text_color: str = None, entire_text_only: bool = False, ticks_visible: bool = False):
        self.run_script(f'''
            {self.id}.chart.priceScale('right').applyOptions({{
                mode: {_price_scale_mode(mode)},
                alignLabels: {_js_bool(align_labels)},
                borderVisible: {_js_bool(border_visible)},
                {f'borderColor: "{border_color}",' if border_color else ''}
                {f'textColor: "{text_color}",' if text_color else ''}
                entireTextOnly: {_js_bool(entire_text_only)},
                ticksVisible: {_js_bool(ticks_visible)},
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
                    visible: {_js_bool(visible)},
                    timeVisible: {_js_bool(time_visible)},
                    secondsVisible: {_js_bool(seconds_visible)},
                    borderVisible: {_js_bool(border_visible)},
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
                visible: {_js_bool(vert_enabled)},
                color: "{color}",
                style: {_line_style(style)},
            }},
            horzLines: {{
                visible: {_js_bool(horz_enabled)},
                color: "{color}",
                style: {_line_style(style)},
            }},
        }}
        }})""")

    def candle_style(self, up_color: str = 'rgba(39, 157, 130, 100)', down_color: str = 'rgba(200, 97, 100, 100)',
                     wick_enabled: bool = True, border_enabled: bool = True, border_up_color: str = '',
                     border_down_color: str = '', wick_up_color: str = '', wick_down_color: str = ''):
        """
        Candle styling for each of its parts.
        """
        self.run_script(f"""
            {self.id}.series.applyOptions({{
                upColor: "{up_color}",
                downColor: "{down_color}",
                wickVisible: {_js_bool(wick_enabled)},
                borderVisible: {_js_bool(border_enabled)},
                {f'borderUpColor: "{border_up_color}",' if border_up_color else up_color if border_enabled else ''}
                {f'borderDownColor: "{border_down_color}",' if border_down_color else down_color if border_enabled else ''}
                {f'wickUpColor: "{wick_up_color}",' if wick_up_color else wick_up_color if wick_enabled else ''}
                {f'wickDownColor: "{wick_down_color}",' if wick_down_color else wick_down_color if wick_enabled else ''}
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

    def crosshair(self, mode: CROSSHAIR_MODE = 'normal', vert_width: int = 1, vert_color: str = None,
                  vert_style: LINE_STYLE = 'dashed', vert_label_background_color: str = 'rgb(46, 46, 46)', horz_width: int = 1,
                  horz_color: str = None, horz_style: LINE_STYLE = 'dashed', horz_label_background_color: str = 'rgb(55, 55, 55)'):
        """
        Crosshair formatting for its vertical and horizontal axes.
        """
        self.run_script(f'''
        {self.id}.chart.applyOptions({{
            crosshair: {{
                mode: {_crosshair_mode(mode)},
                vertLine: {{
                    width: {vert_width},
                    {f'color: "{vert_color}",' if vert_color else ''}
                    style: {_line_style(vert_style)},
                    labelBackgroundColor: "{vert_label_background_color}"
                }},
                horzLine: {{
                    width: {horz_width},
                    {f'color: "{horz_color}",' if horz_color else ''}
                    style: {_line_style(horz_style)},
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

    def legend(self, visible: bool = False, ohlc: bool = True, percent: bool = True, color: str = None,
               font_size: int = None, font_family: str = None):
        """
        Configures the legend of the chart.
        """
        if visible:
            self.run_script(f'''
            {f"{self.id}.legend.style.color = '{color}'" if color else ''}
            {f"{self.id}.legend.style.fontSize = {font_size}" if font_size else ''}
            {f"{self.id}.legend.style.fontFamily = '{font_family}'" if font_family else ''}
            
            {self.id}.chart.subscribeCrosshairMove((param) => {{   
                if (param.time){{
                    const data = param.seriesData.get({self.id}.series);
                    if (!data) {{return}}
                    let percentMove = ((data.close-data.open)/data.open)*100
                    let ohlc = `O ${{legendItemFormat(data.open)}} 
                                | H ${{legendItemFormat(data.high)}} 
                                | L ${{legendItemFormat(data.low)}}
                                | C ${{legendItemFormat(data.close)}} `
                    let percent = `| ${{percentMove >= 0 ? '+' : ''}}${{percentMove.toFixed(2)}} %`
                    let finalString = ''
                    {'finalString += ohlc' if ohlc else ''}
                    {'finalString += percent' if percent else ''}
                    {self.id}.legend.innerHTML = finalString
                }}
                else {{
                    {self.id}.legend.innerHTML = ''
                }}
            }});''')

    def create_subchart(self, volume_enabled: bool = True, position: Literal['left', 'right', 'top', 'bottom'] = 'left',
                        width: float = 0.5, height: float = 0.5, sync: Union[bool, str] = False,
                        topbar: bool = False, searchbox: bool = False):
        subchart = SubChart(self, volume_enabled, position, width, height, sync, topbar, searchbox)
        self._charts[subchart.id] = subchart
        return subchart


class SubChart(LWC):
    def __init__(self, parent, volume_enabled, position, width, height, sync, topbar, searchbox):
        super().__init__(volume_enabled, width, height)
        self._chart = parent._chart if isinstance(parent, SubChart) else parent
        self._parent = parent
        self._position = position
        self._rand = self._chart._rand
        self._js_api_code = self._chart._js_api_code
        self.run_script = self._chart.run_script
        self._charts = self._chart._charts
        self.id = f'window.{self._rand.generate()}'

        self._create_chart()
        self.topbar = TopBar(self) if topbar else None
        self._make_search_box() if searchbox else None
        if not sync:
            return
        sync_parent_var = self._parent.id if isinstance(sync, bool) else sync
        self.run_script(f'''
            {sync_parent_var}.chart.timeScale().subscribeVisibleLogicalRangeChange((timeRange) => {{
                {self.id}.chart.timeScale().setVisibleLogicalRange(timeRange)
            }});
        ''')


SCRIPT = """
document.getElementById('wrapper').style.backgroundColor = '#000000'

function makeChart(innerWidth, innerHeight, autoSize=true) {
    let chart = {
        markers: [],
        horizontal_lines: [],
        div: document.createElement('div'),
        wrapper: document.createElement('div'),
        legend: document.createElement('div'),
        scale: {
            width: innerWidth,
            height: innerHeight
        },
    }    
    chart.chart = LightweightCharts.createChart(chart.div, {
        width: window.innerWidth*innerWidth,
        height: window.innerHeight*innerHeight,
        layout: {
            textColor: '#d1d4dc',
            background: {
                color:'#000000',
                type: LightweightCharts.ColorType.Solid,
                },
            fontSize: 12
            },
        rightPriceScale: {
            scaleMargins: {top: 0.3, bottom: 0.25},
        },
        timeScale: {timeVisible: true, secondsVisible: false},
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                labelBackgroundColor: 'rgb(46, 46, 46)'
            },
            horzLine: {
                labelBackgroundColor: 'rgb(55, 55, 55)'
            }
        },
        grid: {
            vertLines: {color: 'rgba(29, 30, 38, 5)'},
            horzLines: {color: 'rgba(29, 30, 58, 5)'},
        },
        handleScroll: {vertTouchDrag: true},
    })
    let up = 'rgba(39, 157, 130, 100)'
    let down = 'rgba(200, 97, 100, 100)'
    chart.series = chart.chart.addCandlestickSeries({color: 'rgb(0, 120, 255)', upColor: up, borderUpColor: up, wickUpColor: up,
                                        downColor: down, borderDownColor: down, wickDownColor: down, lineWidth: 2,
                                        })
    chart.volumeSeries = chart.chart.addHistogramSeries({
                        color: '#26a69a',
                        priceFormat: {type: 'volume'},
                        priceScaleId: '',
                        })
    chart.chart.priceScale('').applyOptions({
        scaleMargins: {top: 0.8, bottom: 0},
        });
    chart.legend.style.position = 'absolute'
    chart.legend.style.zIndex = 1000
    chart.legend.style.width = `${(chart.scale.width*100)-8}vw`
    chart.legend.style.top = '10px'
    chart.legend.style.left = '10px'
    chart.legend.style.fontFamily = 'Monaco'
    chart.legend.style.fontSize = '11px'
    chart.legend.style.color = 'rgb(191, 195, 203)'
    
    chart.wrapper.style.width = `${100*innerWidth}%`
    chart.wrapper.style.height = `${100*innerHeight}%`
    chart.div.style.position = 'relative'
    chart.wrapper.style.display = 'flex'
    chart.wrapper.style.flexDirection = 'column'
    
    chart.div.appendChild(chart.legend)
    chart.wrapper.appendChild(chart.div)
    document.getElementById('wrapper').append(chart.wrapper)
    
    if (!autoSize) {
        return chart
    }
    let topBarOffset = 0
    window.addEventListener('resize', function() {
        if ('topBar' in chart) {
        topBarOffset = chart.topBar.offsetHeight
        }
        chart.chart.resize(window.innerWidth*innerWidth, (window.innerHeight*innerHeight)-topBarOffset)
        });
    return chart
}
function makeHorizontalLine(chart, price, color, width, style, axisLabelVisible, text) {
    let priceLine = {
       price: price,
       color: color,
       lineWidth: width,
       lineStyle: style,
       axisLabelVisible: axisLabelVisible,
       title: text,
    };
    let line = {
       line: chart.series.createPriceLine(priceLine),
       price: price,
    };
    chart.horizontal_lines.push(line)
}
function legendItemFormat(num) {
return num.toFixed(2).toString().padStart(8, ' ')
}
"""

HTML = f"""
<!DOCTYPE html>
<html lang="">
<head>
    <title>lightweight-charts-python</title>
    <script>{LWC_4_0_1}</script>
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
    }}
    </style>
</head>
<body>
    <div id="wrapper"></div>
    <script>
    {SCRIPT}
    </script>
</body>
</html>"""

CALLBACK_SCRIPT = '''
function makeSearchBox(chart, callbackFunction) {
    let searchWindow = document.createElement('div')
    searchWindow.style.position = 'absolute'
    searchWindow.style.top = '0'
    searchWindow.style.bottom = '200px'
    searchWindow.style.left = '0'
    searchWindow.style.right = '0'
    searchWindow.style.margin = 'auto'
    searchWindow.style.width = '150px'
    searchWindow.style.height = '30px'
    searchWindow.style.padding = '10px'
    searchWindow.style.backgroundColor = 'rgba(30, 30, 30, 0.9)'
    searchWindow.style.border = '3px solid #3C434C'
    searchWindow.style.zIndex = '1000'
    searchWindow.style.display = 'none'
    searchWindow.style.borderRadius = '5px'
    
    let magnifyingGlass = document.createElement('span');
    magnifyingGlass.style.display = 'inline-block';
    magnifyingGlass.style.width = '12px';
    magnifyingGlass.style.height = '12px';
    magnifyingGlass.style.border = '2px solid #FFF';
    magnifyingGlass.style.borderRadius = '50%';
    magnifyingGlass.style.position = 'relative';
    let handle = document.createElement('span');
    handle.style.display = 'block';
    handle.style.width = '7px';
    handle.style.height = '2px';
    handle.style.backgroundColor = '#FFF';
    handle.style.position = 'absolute';
    handle.style.top = 'calc(50% + 7px)';
    handle.style.right = 'calc(50% - 11px)';
    handle.style.transform = 'rotate(45deg)';

    let sBox = document.createElement('input');
    sBox.type = 'text';
    sBox.placeholder = 'search';
    sBox.style.position = 'relative';
    sBox.style.display = 'inline-block';
    sBox.style.zIndex = '1000';
    sBox.style.textAlign = 'center'
    sBox.style.width = '100px'
    sBox.style.marginLeft = '15px'
    sBox.style.backgroundColor = 'rgba(0, 122, 255, 0.2)'
    sBox.style.color = 'lightgrey'
    sBox.style.fontSize = '20px'            
    sBox.style.border = 'none'
    sBox.style.outline = 'none'
    sBox.style.borderRadius = '2px'
    
    searchWindow.appendChild(magnifyingGlass)
    magnifyingGlass.appendChild(handle)
    searchWindow.appendChild(sBox)
    chart.div.appendChild(searchWindow);

    let yPrice = null
    chart.chart.subscribeCrosshairMove((param) => {
        if (param.point){
            yPrice = param.point.y;
        }
    });
    let selectedChart = false
    chart.wrapper.addEventListener('mouseover', (event) => {
        selectedChart = true
    })
    chart.wrapper.addEventListener('mouseout', (event) => {
        selectedChart = false
    })
    document.addEventListener('keydown', function(event) {
        if (!selectedChart) {return}
        if (event.altKey && event.code === 'KeyH') {
            let price = chart.series.coordinateToPrice(yPrice)
            makeHorizontalLine(chart, price, '#FFFFFF', 1, LightweightCharts.LineStyle.Solid, true, '')
        }
        if (searchWindow.style.display === 'none') {
            if (/^[a-zA-Z0-9]$/.test(event.key)) {
                searchWindow.style.display = 'block';
                sBox.focus();
            }
        }
        else if (event.key === 'Enter') {
            callbackFunction(`on_search__${chart.id}__${sBox.value}`)
            searchWindow.style.display = 'none'
            sBox.value = ''
        }
        else if (event.key === 'Escape') {
            searchWindow.style.display = 'none'
            sBox.value = ''
        }
    });
    sBox.addEventListener('input', function() {
        sBox.value = sBox.value.toUpperCase();
    });
}

function makeSwitcher(chart, items, activeItem, callbackFunction, callbackName) {
    let switcherElement = document.createElement('div');
    switcherElement.style.margin = '4px 18px'
    switcherElement.style.zIndex = '1000'

    let intervalElements = items.map(function(item) {
        let itemEl = document.createElement('button');
        itemEl.style.cursor = 'pointer'
        itemEl.style.padding = '3px 6px'
        itemEl.style.margin = '0px 4px'
        itemEl.style.fontSize = '14px'
        itemEl.style.color = 'lightgrey'
        itemEl.style.backgroundColor = item === activeItem ? 'rgba(0, 122, 255, 0.7)' : 'transparent'

        itemEl.style.border = 'none'
        itemEl.style.borderRadius = '4px'
        itemEl.addEventListener('mouseenter', function() {
            itemEl.style.backgroundColor = item === activeItem ? 'rgba(0, 122, 255, 0.7)' : 'rgb(19, 40, 84)'
        })
        itemEl.addEventListener('mouseleave', function() {
            itemEl.style.backgroundColor = item === activeItem ? 'rgba(0, 122, 255, 0.7)' : 'transparent'
        })
        itemEl.innerText = item;
        itemEl.addEventListener('click', function() {
            onItemClicked(item);
        });
        switcherElement.appendChild(itemEl);
        return itemEl;
    });
    function onItemClicked(item) {
        if (item === activeItem) {
            return;
        }
        intervalElements.forEach(function(element, index) {
            element.style.backgroundColor = items[index] === item ? 'rgba(0, 122, 255, 0.7)' : 'transparent'
        });
        activeItem = item;
        callbackFunction(`${callbackName}__${chart.id}__${item}`);
    }
    chart.topBar.appendChild(switcherElement)
    makeSeperator(chart.topBar)
    return switcherElement;
}

function makeTextBoxWidget(chart, text) {
    let textBox = document.createElement('div')
    textBox.style.margin = '0px 18px'
    textBox.style.position = 'relative'
    textBox.style.color = 'lightgrey'
    textBox.innerText = text
    chart.topBar.append(textBox)
    makeSeperator(chart.topBar)
    return textBox
}
function makeTopBar(chart) {
    chart.topBar = document.createElement('div')
    chart.topBar.style.backgroundColor = '#191B1E'
    chart.topBar.style.borderBottom = '3px solid #3C434C'
    chart.topBar.style.display = 'flex'
    chart.topBar.style.alignItems = 'center'
    chart.wrapper.prepend(chart.topBar)
}
function makeSeperator(topBar) {
    let seperator = document.createElement('div')
        seperator.style.width = '1px'
        seperator.style.height = '20px'
        seperator.style.backgroundColor = '#3C434C'
        topBar.appendChild(seperator)
    }
'''

