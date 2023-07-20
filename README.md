<div align="center">

# lightweight-charts-python

[![PyPi Release](https://img.shields.io/pypi/v/lightweight-charts?color=32a852&label=PyPi)](https://pypi.org/project/lightweight-charts/)
[![Made with Python](https://img.shields.io/badge/Python-3.8+-c7a002?logo=python&logoColor=white)](https://python.org "Go to Python homepage")
[![License](https://img.shields.io/github/license/louisnw01/lightweight-charts-python?color=9c2400)](https://github.com/louisnw01/lightweight-charts-python/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/documentation-006ee3)](https://lightweight-charts-python.readthedocs.io/en/latest/docs.html)

![cover](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/cover.png)

lightweight-charts-python aims to provide a simple and pythonic way to access and implement [TradingView's Lightweight Charts](https://www.tradingview.com/lightweight-charts/).
</div>


## Installation
```
pip install lightweight-charts
```
* White screen? Having issues with pywebview? Click [here](https://github.com/louisnw01/lightweight-charts-python/issues?q=label%3A%22pywebview+issue%22+).
___

## Features
1. Simple and easy to use.
2. Blocking or non-blocking GUI.
3. Streamlined for live data, with methods for updating directly from tick data.
4. Multi-Pane Charts using the [`SubChart`](https://lightweight-charts-python.readthedocs.io/en/latest/docs.html#subchart).
5. The Toolbox, allowing for trendlines, rays and horizontal lines to be drawn directly onto charts.
6. [Callbacks](https://lightweight-charts-python.readthedocs.io/en/latest/docs.html#callbacks) allowing for timeframe (1min, 5min, 30min etc.) selectors, searching, and more.
7. Direct integration of market data through [Polygon.io's](https://polygon.io/?utm_source=affiliate&utm_campaign=pythonlwcharts) market data API.

__Supports:__ Jupyter Notebooks, PyQt, wxPython, Streamlit, and asyncio.

PartTimeLarry: [Interactive Brokers API and TradingView Charts in Python](https://www.youtube.com/watch?v=TlhDI3PforA)
___

### 1. Display data from a csv:

```python
import pandas as pd
from lightweight_charts import Chart


if __name__ == '__main__':
    
    chart = Chart()
    
    # Columns: | time | open | high | low | close | volume (if volume is enabled) |
    df = pd.read_csv('ohlcv.csv')
    chart.set(df)
    
    chart.show(block=True)

```
![setting_data image](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/1_setting_data/setting_data.png)
___

### 2. Updating bars in real-time:

```python
import pandas as pd
from time import sleep
from lightweight_charts import Chart

if __name__ == '__main__':

    chart = Chart()

    df1 = pd.read_csv('ohlcv.csv')
    df2 = pd.read_csv('next_ohlcv.csv')

    chart.set(df1)

    chart.show()

    last_close = df1.iloc[-1]
    
    for i, series in df2.iterrows():
        chart.update(series)

        if series['close'] > 20 and last_close < 20:
            chart.marker(text='The price crossed $20!')
            
        last_close = series['close']
        sleep(0.1)

```

![live data gif](https://github.com/louisnw01/lightweight-charts-python/blob/main/examples/2_live_data/live_data.gif?raw=true)
___

### 3. Updating bars from tick data in real-time:

```python
import pandas as pd
from time import sleep
from lightweight_charts import Chart


if __name__ == '__main__':
    
    df1 = pd.read_csv('ohlc.csv')
    
    # Columns: | time | price | volume (if volume is enabled) |
    df2 = pd.read_csv('ticks.csv')
    
    chart = Chart(volume_enabled=False)
    
    chart.set(df1)
    
    chart.show()
    
    for i, tick in df2.iterrows():
        chart.update_from_tick(tick)
            
        sleep(0.3)

```
![tick data gif](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/3_tick_data/tick_data.gif)
___

### 4. Line Indicators:

```python
import pandas as pd
from lightweight_charts import Chart


def calculate_sma(data: pd.DataFrame, period: int = 50):
   def avg(d: pd.DataFrame):
      return d['close'].mean()

   result = []
   for i in range(period - 1, len(data)):
      val = avg(data.iloc[i - period + 1:i])
      result.append({'time': data.iloc[i]['date'], f'SMA {period}': val})
   return pd.DataFrame(result)


if __name__ == '__main__':
   chart = Chart()
   chart.legend(visible=True)
   
   df = pd.read_csv('ohlcv.csv')
   chart.set(df)

   line = chart.create_line()
   sma_data = calculate_sma(df, period=50)
   line.set(sma_data, name='SMA 50')

   chart.show(block=True)

```
![line indicators image](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/4_line_indicators/line_indicators.png)
___

### 5. Styling:

```python
import pandas as pd
from lightweight_charts import Chart


if __name__ == '__main__':
    
    chart = Chart(debug=True)

    df = pd.read_csv('ohlcv.csv')

    chart.layout(background_color='#090008', text_color='#FFFFFF', font_size=16,
                 font_family='Helvetica')

    chart.candle_style(up_color='#00ff55', down_color='#ed4807',
                       border_up_color='#FFFFFF', border_down_color='#FFFFFF',
                       wick_up_color='#FFFFFF', wick_down_color='#FFFFFF')

    chart.volume_config(up_color='#00ff55', down_color='#ed4807')

    chart.watermark('1D', color='rgba(180, 180, 240, 0.7)')

    chart.crosshair(mode='normal', vert_color='#FFFFFF', vert_style='dotted',
                    horz_color='#FFFFFF', horz_style='dotted')

    chart.legend(visible=True, font_size=14)

    chart.set(df)

    chart.show(block=True)

```
![styling image](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/5_styling/styling.png)
___

### 6. Callbacks:

```python
import asyncio
import pandas as pd

from lightweight_charts import Chart


def get_bar_data(symbol, timeframe):
    if symbol not in ('AAPL', 'GOOGL', 'TSLA'):
        print(f'No data for "{symbol}"')
        return pd.DataFrame()
    return pd.read_csv(f'bar_data/{symbol}_{timeframe}.csv')


class API:
    def __init__(self):
        self.chart = None  # Changes after each callback.

    async def on_search(self, searched_string):  # Called when the user searches.
        new_data = get_bar_data(searched_string, self.chart.topbar['timeframe'].value)
        if new_data.empty:
            return
        self.chart.topbar['corner'].set(searched_string)
        self.chart.set(new_data)

    async def on_timeframe_selection(self):  # Called when the user changes the timeframe.
        new_data = get_bar_data(self.chart.topbar['corner'].value, self.chart.topbar['timeframe'].value)
        if new_data.empty:
            return
        self.chart.set(new_data)
            
    async def on_horizontal_line_move(self, line_id, price):
        print(f'Horizontal line moved to: {price}')


async def main():
    api = API()

    chart = Chart(api=api, topbar=True, searchbox=True, toolbox=True)
    chart.legend(True)

    chart.topbar.textbox('corner', 'TSLA')
    chart.topbar.switcher('timeframe', api.on_timeframe_selection, '1min', '5min', '30min', default='5min')

    df = get_bar_data('TSLA', '5min')
    chart.set(df)
    
    chart.horizontal_line(200, interactive=True)

    await chart.show_async(block=True)


if __name__ == '__main__':
    asyncio.run(main())

```
![callbacks gif](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/6_callbacks/callbacks.gif)
___

<div align="center">

[![Documentation](https://img.shields.io/badge/documentation-006ee3)](https://lightweight-charts-python.readthedocs.io/en/latest/docs.html)

Inquiries: [shaders_worker_0e@icloud.com](mailto:shaders_worker_0e@icloud.com)
___

_This package is an independent creation and has not been endorsed, sponsored, or approved by TradingView. The author of this package does not have any official relationship with TradingView, and the package does not represent the views or opinions of TradingView._
</div>
