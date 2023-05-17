import pandas as pd
import uuid
from datetime import timedelta, datetime
from typing import Dict, Union

from lightweight_charts.pkg import LWC_3_5_0
from lightweight_charts.util import LINE_TYPE, POSITION, SHAPE, CROSSHAIR_MODE, _crosshair_mode, _line_type, \
    MissingColumn, _js_bool, _price_scale_mode, PRICE_SCALE_MODE, _position, _shape, IDGen


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
        self.click_func = None

    def onClick(self, data):
        if isinstance(data['time'], int):
            data['time'] = datetime.fromtimestamp(data['time'])
        else:
            data['time'] = datetime(data['time']['year'], data['time']['month'], data['time']['day'])
        self.click_func(data) if self.click_func else None


class LWC:
    def __init__(self, volume_enabled):
        self.js_queue = []
        self.loaded = False
        self._html = HTML
        self._rand = IDGen()

        self._js_api = API()

        self.volume_enabled = volume_enabled
        self.last_bar = None
        self.interval = None
        self._lines: Dict[uuid.UUID, Line] = {}

        self.background_color = '#000000'
        self.volume_up_color = 'rgba(83,141,131,0.8)'
        self.volume_down_color = 'rgba(200,127,130,0.8)'

    def _on_js_load(self): pass

    def _stored(self, func, *args, **kwargs):
        if self.loaded:
            return False
        self.js_queue.append((func, args, kwargs))
        return True

    def _click_func_code(self, string): self._html = self._html.replace('// __onClick__', string)

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

            self.run_script(f'chart.volumeSeries.setData({volume.to_dict(orient="records")})')
            bars = df.drop(columns=['volume'])

        bars = bars.to_dict(orient='records')
        self.run_script(f'chart.series.setData({bars})')

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
            self.run_script(f'chart.volumeSeries.update({volume.to_dict()})')
            series = series.drop(['volume'])

        dictionary = series.to_dict()
        self.run_script(f'chart.series.update({dictionary})')

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
        line_id = uuid.uuid4()
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
                series: chart.chart.addLineSeries(lineSeries{var}),
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
               color: str = '#2196F3', text: str = '', m_id: uuid.UUID = None) -> uuid.UUID:
        """
        Creates a new marker.\n
        :param time: The time that the marker will be placed at. If no time is given, it will be placed at the last bar.
        :param position: The position of the marker.
        :param color: The color of the marker (rgb, rgba or hex).
        :param shape: The shape of the marker.
        :param text: The text to be placed with the marker.
        :return: The UUID of the marker placed.
        """
        if not m_id:
            m_id = uuid.uuid4()
        if self._stored('marker', time, position, shape, color, text, m_id):
            return m_id

        time = self.last_bar['time'] if not time else self._datetime_format(time)

        self.run_script(f"""
                markers.push({{
                    time: '{time}',
                    position: '{_position(position)}',
                    color: '{color}', shape: '{_shape(shape)}',
                    text: '{text}',
                    id: '{m_id}'
                    }});
                chart.series.setMarkers(markers)""")
        return m_id

    def remove_marker(self, m_id: uuid.UUID):
        """
        Removes the marker with the given uuid.\n
        """
        if self._stored('remove_marker', m_id):
            return None

        self.run_script(f'''
                       markers.forEach(function (marker) {{
                           if ('{m_id}' === marker.id) {{
                               markers.splice(markers.indexOf(marker), 1)
                               chart.series.setMarkers(markers)
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
                   lineStyle: LightweightCharts.LineStyle.{style},
                   axisLabelVisible: {'true' if axis_label_visible else 'false'},
                   title: '{text}',
               }};
               let line{var} = {{
                   line: chart.series.createPriceLine(priceLine{var}),
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
                   chart.series.removePriceLine(line.line);
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

        self.run_script(f'chart.chart.timeScale().scrollToPosition({right_padding}, false)') if right_padding else None
        self.run_script(f'chart.series.applyOptions({{title: "{title}"}})') if title else None
        self.run_script(
            f"chart.chart.priceScale().applyOptions({{mode: LightweightCharts.PriceScaleMode.{_price_scale_mode(mode)}}})") if mode else None

    def time_scale(self, time_visible: bool = True, seconds_visible: bool = False):
        """
        Options for the time scale of the chart.
        :param time_visible: Time visibility control.
        :param seconds_visible: Seconds visibility control
        :return:
        """
        if self._stored('time_scale', time_visible, seconds_visible):
            return None

        time = f'timeVisible: {_js_bool(time_visible)},'
        seconds = f'secondsVisible: {_js_bool(seconds_visible)}'
        self.run_script(f'''
           chart.chart.applyOptions({{
               timeScale: {{
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
        args = f"'{self.background_color}'", f"'{text_color}'", f"{font_size}", f"'{font_family}'",
        for key, arg in zip(('backgroundColor', 'textColor', 'fontSize', 'fontFamily'), args):
            if not arg:
                continue
            self.run_script(f"""
                  chart.chart.applyOptions({{
                     layout: {{
                          {key}: {arg}
                     }} 
                  }})""")

    def candle_style(self, up_color: str = 'rgba(39, 157, 130, 100)', down_color: str = 'rgba(200, 97, 100, 100)',
                     wick_enabled: bool = True, border_enabled: bool = True, border_up_color: str = '',
                     border_down_color: str = '', wick_up_color: str = '', wick_down_color: str = ''):
        """
        Candle styling for each of its parts.
        """
        if self._stored('candle_style', up_color, down_color, wick_enabled, border_enabled,
                        border_up_color, border_down_color, wick_up_color, wick_down_color):
            return None

        params = None, 'upColor', 'downColor', 'wickVisible', 'borderVisible', 'borderUpColor', 'borderDownColor',\
                 'wickUpColor', 'wickDownColor'
        for param, key_arg in zip(params, locals().items()):
            key, arg = key_arg
            if isinstance(arg, bool):
                arg = _js_bool(arg)
            if key == 'self' or arg is None:
                continue
            else:
                arg = f"'{arg}'"
            self.run_script(
                f"""chart.series.applyOptions({{
                    {param}: {arg},
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
        top = f'top: {scale_margin_top},'
        bottom = f'bottom: {scale_margin_bottom},'
        self.run_script(f'''
        chart.volumeSeries.priceScale().applyOptions({{
            scaleMargins: {{
            {top if top else ''}
            {bottom if bottom else ''}
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
            chart.chart.applyOptions({{
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
          chart.chart.applyOptions({{
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

        scripts = f'legendToggle = {_js_bool(visible)}; legend.innerText = ""', f'legendOHLCVisible = {_js_bool(ohlc)}',\
                  f'legendPercentVisible = {_js_bool(percent)}', f'legend.style.color = {color}', \
                  f'legend.style.fontSize = "{font_size}px"', f'legend.style.fontFamily = "{font_family}"'
        for script, arg in zip(scripts, (visible, ohlc, percent, color, font_size, font_family)):
            if arg is None:
                continue
            self.run_script(script)

    def subscribe_click(self, function: object):
        if self._stored('subscribe_click', function):
            return None

        self._js_api.click_func = function
        self.run_script('isSubscribed = true')


SCRIPT = """

const markers = []
const horizontal_lines = []
const lines = []

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

chart.chart = makeChart(window.innerWidth, window.innerHeight, chartsDiv)
chart.series = makeCandlestickSeries(chart.chart)
chart.volumeSeries = makeVolumeSeries(chart.chart)
            
document.body.appendChild(chartsDiv)

const legend = document.createElement('div')
legend.style.display = 'block'
legend.style.position = 'absolute'
legend.style.zIndex = 1000
legend.style.width = '98vw'
legend.style.top = '10px'
legend.style.left = '10px'
legend.style.fontFamily = 'Monaco'

legend.style.fontSize = '11px'
legend.style.color = 'rgb(191, 195, 203)'

document.body.appendChild(legend)

chart.chart.priceScale('').applyOptions({
    scaleMargins: {
        top: 0.8,
        bottom: 0,
    }
});

window.addEventListener('resize', function() {
    let width = window.innerWidth;
    let height = window.innerHeight;
    chart.chart.resize(width, height)
});

function legendItemFormat(num) {
    return num.toFixed(2).toString().padStart(8, ' ')
}
let legendToggle = false
let legendOHLCVisible = true
let legendPercentVisible = true
chart.chart.subscribeCrosshairMove((param) => {
    if (param.time){
        const data = param.seriesPrices.get(chart.series);
        if (!data || legendToggle === false) {return}
        const percentMove = ((data.close-data.open)/data.open)*100
        //legend.style.color = percentMove >= 0 ? up : down
        
        let ohlc = `open: ${legendItemFormat(data.open)} 
                    | high: ${legendItemFormat(data.high)} 
                    | low: ${legendItemFormat(data.low)} 
                    | close: ${legendItemFormat(data.close)} `
        let percent = `| daily: ${percentMove >= 0 ? '+' : ''}${percentMove.toFixed(2)} %`
        
        let finalString = ''
        if (legendOHLCVisible) {
            finalString += ohlc
        }
        if (legendPercentVisible) {
            finalString += percent
        }
        legend.innerHTML = finalString
    }
    else {
        legend.innerHTML = ''
    }
});
let isSubscribed = false
function clickHandler(param) {
    if (!param.point || !isSubscribed) {return}
    let prices = param.seriesPrices.get(chart.series);
    let data = {
        time: param.time,
        open: prices.open,
        high: prices.high,
        low: prices.low,
        close: prices.close,
    }
    // __onClick__

}
chart.chart.subscribeClick(clickHandler)
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
