<div align="center">

# lightweight-charts-python

[![PyPi Release](https://img.shields.io/pypi/v/lightweight-charts?color=32a852&label=PyPi)](https://pypi.org/project/lightweight-charts/)
[![Made with Python](https://img.shields.io/badge/Python-3.9+-c7a002?logo=python&logoColor=white)](https://python.org "Go to Python homepage")
[![License](https://img.shields.io/github/license/louisnw01/lightweight-charts-python?color=9c2400)](https://github.com/louisnw01/lightweight-charts-python/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/documentation-006ee3)](https://lightweight-charts-python.readthedocs.io/en/latest/docs.html)

![async](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/6_async/async.png)
![cover](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/cover.png)

lightweight-charts-python aims to provide a simple and pythonic way to access and implement [TradingView's Lightweight Charts](https://www.tradingview.com/lightweight-charts/).
</div>

## Installation
```
pip install lightweight-charts
```
___

## Features
1. Simple and easy to use.
2. Blocking or non-blocking GUI.
3. Streamlined for live data, with methods for updating directly from tick data.
4. Supports:
   * PyQt
   * wxPython
   * Streamlit
   * asyncio
5. [Callbacks](https://lightweight-charts-python.readthedocs.io/en/latest/docs.html#chartasync) allowing for timeframe (1min, 5min, 30min etc.) selectors, searching, and more.
6. Multi-Pane Charts using the `SubChart` ([examples](https://lightweight-charts-python.readthedocs.io/en/latest/docs.html#subchart)).
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
        result.append({'time': data.iloc[i]['date'], 'value': val})
    return pd.DataFrame(result)


if __name__ == '__main__':
    
    chart = Chart()
    
    df = pd.read_csv('ohlcv.csv')
    chart.set(df)
    
    line = chart.create_line()
    sma_data = calculate_sma(df)
    line.set(sma_data)
    
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

### 6. ChartAsync:

```python
import asyncio
import pandas as pd

from lightweight_charts import ChartAsync


def get_bar_data(symbol, timeframe):
    return pd.read_csv(f'bar_data/{symbol}_{timeframe}.csv')


class API:
    def __init__(self):
        self.chart = None  # Changes after each callback.
        self.symbol = 'TSLA'
        self.timeframe = '5min'

    async def on_search(self, searched_string):  # Called when the user searches.
        self.symbol = searched_string
        new_data = await self.get_data()
        if new_data.empty:
            return
        self.chart.set(new_data)
        self.chart.corner_text(searched_string)

    async def on_timeframe_selection(self, timeframe):  # Called when the user changes the timeframe.
        self.timeframe = timeframe
        new_data = await self.get_data()
        if new_data.empty:
            return
        self.chart.set(new_data)

    async def get_data(self):
        if self.symbol not in ('AAPL', 'GOOGL', 'TSLA'):
            print(f'No data for "{self.symbol}"')
            return pd.DataFrame()
        data = get_bar_data(self.symbol, self.timeframe)
        return data


async def main():
    api = API()

    chart = ChartAsync(api=api, debug=True)
    chart.legend(True)

    chart.create_switcher(api.on_timeframe_selection, '1min', '5min', '30min', default='5min')
    chart.corner_text(api.symbol)

    df = get_bar_data(api.symbol, api.timeframe)
    chart.set(df)

    await chart.show(block=True)


if __name__ == '__main__':
    asyncio.run(main())

```
![async gif](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/examples/6_async/async.gif)
___

<div align="center">

[![Documentation](https://img.shields.io/badge/documentation-006ee3)](https://lightweight-charts-python.readthedocs.io/en/latest/docs.html)
___

_This package is an independent creation and has not been endorsed, sponsored, or approved by TradingView. The author of this package does not have any official relationship with TradingView, and the package does not represent the views or opinions of TradingView._
</div>
