# Docs

[![louisnw01 - lightweight-charts-python](https://img.shields.io/static/v1?label=louisnw01&message=lightweight-charts-python&color=057dfc&logo=github)](https://github.com/louisnw01/lightweight-charts-python "Go to GitHub repo")
[![PyPi Release](https://img.shields.io/pypi/v/lightweight-charts?color=32a852&label=PyPi)](https://pypi.org/project/lightweight-charts/)
[![Made with Python](https://img.shields.io/badge/Python-3.9+-c7a002?logo=python&logoColor=white)](https://python.org "Go to Python homepage")
[![License](https://img.shields.io/github/license/louisnw01/lightweight-charts-python?color=9c2400)](https://github.com/louisnw01/lightweight-charts-python/blob/main/LICENSE)
[![Stars - lightweight-charts-python](https://img.shields.io/github/stars/louisnw01/lightweight-charts-python?style=social)](https://github.com/louisnw01/lightweight-charts-python)
[![Forks - lightweight-charts-python](https://img.shields.io/github/forks/louisnw01/lightweight-charts-python?style=social)](https://github.com/louisnw01/lightweight-charts-python)
___

## Common Methods
The methods below can be used within all chart objects.

___
### `set`
`data: pd.DataFrame` `render_drawings: bool`

Sets the initial data for the chart.

The data must be given as a DataFrame, with the columns:

`time | open | high | low | close | volume`

The `time` column can also be named `date` or be the index, and the `volume` column can be omitted if volume is not enabled.

Column names are not case sensitive.

If `render_drawings` is `True`, any drawings made using the `toolbox` will be redrawn with the new data. This is designed to be used when switching to a different timeframe of the same symbol.

```{important}
the `time` column must have rows all of the same timezone and locale. This is particularly noticeable for data which crosses over daylight saving hours on data with intervals of less than 1 day. Errors are likely to be raised if they are not converted beforehand.
```

An empty `DataFrame` object can also be given to this method, which will erase all candle and volume data displayed on the chart.
___

### `update`
`series: pd.Series`

Updates the chart data from a given bar.

The bar should contain values with labels of the same name as the columns required for using `chart.set()`.
___

### `update_from_tick`
`series: pd.Series` | `cumulative_volume: bool`

Updates the chart from a tick.

The series should use the labels:

`time | price | volume`

As before, the `time` can also be named `date`, and the `volume` can be omitted if volume is not enabled.

```{information}
The provided ticks do not need to be rounded to an interval (1 min, 5 min etc.), as the library handles this automatically.```````
```

If `cumulative_volume` is used, the volume data given will be added onto the latest bar of volume data.
___

### `create_line`
`color: str` | `width: int` | `price_line: bool` | `price_label: bool` | `-> Line`

Creates and returns a [Line](#line) object.
___

### `lines`
`-> List[Line]`

Returns a list of all lines for the chart or subchart.
___

### `trend_line`
`start_time: str/datetime` | `start_value: float/int` | `end_time: str/datetime` | `end_value: float/int` | `color: str` | `width: int` | `-> Line`

Creates a trend line, drawn from the first point (`start_time`, `start_value`) to the last point (`end_time`, `end_value`).
___

### `ray_line`
`start_time: str/datetime` | `value: float/int` | `color: str` | `width: int` | `-> Line`

Creates a ray line, drawn from the first point (`start_time`, `value`) and onwards.
___

### `marker`
`time: datetime` | `position: 'above'/'below'/'inside'` | `shape: 'arrow_up'/'arrow_down'/'circle'/'square'` | `color: str` | `text: str` | `-> str`

Adds a marker to the chart, and returns its id.

If the `time` parameter is not given, the marker will be placed at the latest bar.

When using multiple markers, they should be placed in chronological order or display bugs may be present.
___

### `remove_marker`
`marker_id: str`

Removes the marker with the given id.

Usage:
```python
marker = chart.marker(text='hello_world')
chart.remove_marker(marker)
```
___

### `horizontal_line`
`price: float/int` | `color: str` | `width: int` | `style: 'solid'/'dotted'/'dashed'/'large_dashed'/'sparse_dotted'` | `text: str` | `axis_label_visible: bool` | `interactive: bool` | `-> HorizontalLine`

Places a horizontal line at the given price, and returns a HorizontalLine object.

If `interactive` is set to `True`, this horizontal line can be edited on the chart. Upon its movement a callback will also be emitted to an `on_horizontal_line_move` method, containing its ID and price. The toolbox should be enabled during its usage. It is designed to be used to update an order (limit, stop, etc.) directly on the chart.
___

### `remove_horizontal_line`
`price: float/int`

Removes a horizontal line at the given price.
___

### `clear_markers`

Clears the markers displayed on the data.
___

### `clear_horizontal_lines`

Clears the horizontal lines displayed on the data.
___

### `precision`
`precision: int`

Sets the precision of the chart based on the given number of decimal places.
___

### `price_scale`
`mode: 'normal'/'logarithmic'/'percentage'/'index100'` | `align_labels: bool` | `border_visible: bool` | `border_color: str` | `text_color: str` | `entire_text_only: bool` | `ticks_visible: bool` | `scale_margin_top: float` | `scale_margin_bottom: float`

Price scale options for the chart.
___

### `time_scale`
`right_offset: int` | `min_bar_spacing: float` | `visible: bool` | `time_visible: bool` | `seconds_visible: bool` | `border_visible: bool` | `border_color: str`

Timescale options for the chart.
___

### `layout`
`background_color: str` | `text_color: str` | `font_size: int` | `font_family: str`

Global layout options for the chart.
___

### `grid`
`vert_enabled: bool` | `horz_enabled: bool` | `color: str` | `style: 'solid'/'dotted'/'dashed'/'large_dashed'/'sparse_dotted'`

Grid options for the chart.
___

### `candle_style`
`up_color: str` | `down_color: str` | `wick_enabled: bool` | `border_enabled: bool` | `border_up_color: str` | `border_down_color: str` | `wick_up_color: str` | `wick_down_color: str`

 Candle styling for each of the candle's parts (border, wick).

```{admonition} Color Formats
:class: note

Throughout the library, colors should be given as either: 
* rgb: `rgb(100, 100, 100)`
* rgba: `rgba(100, 100, 100, 0.7)`
* hex: `#32a852`
```
___

### `volume_config`
`scale_margin_top: float` | `scale_margin_bottom: float` | `up_color: str` | `down_color: str`

Volume config options.

```{important}
The float values given to scale the margins must be greater than 0 and less than 1.
```
___

### `crosshair`
`mode` | `vert_visible: bool` | `vert_width: int` | `vert_color: str` | `vert_style: str` | `vert_label_background_color: str` | `horz_visible: bool` | `horz_width: int` | `horz_color: str` | `horz_style: str` | `horz_label_background_color: str`

Crosshair formatting for its vertical and horizontal axes.

`vert_style` and `horz_style` should be given as one of: `'solid'/'dotted'/'dashed'/'large_dashed'/'sparse_dotted'`
___

### `watermark`
`text: str` | `font_size: int` | `color: str`

Overlays a watermark on top of the chart.
___

### `legend`
`visible: bool` | `ohlc: bool` | `percent: bool` | `lines: bool` | `color: str` | `font_size: int` | `font_family: str`

Configures the legend of the chart.
___

### `spinner`
`visible: bool`

Shows a loading spinner on the chart, which can be used to visualise the loading of large datasets, API calls, etc.
___

### `price_line`
`label_visible: bool` | `line_visible: bool` | `title: str`

Configures the visibility of the last value price line and its label.
___

### `fit`

Attempts to fit all data displayed on the chart within the viewport (`fitContent()`).
___

### `hide_data`

Hides the candles on the chart.
___

### `show_data`

Shows the hidden candles on the chart.
___

### `polygon`
Used to access Polygon.io's API (see [here](https://lightweight-charts-python.readthedocs.io/en/latest/polygon.html)).
___

### `create_subchart`
`volume_enabled: bool` | `position: 'left'/'right'/'top'/'bottom'`, `width: float` | `height: float` | `sync: bool/str` | `-> SubChart`

Creates and returns a [SubChart](#subchart) object, placing it adjacent to the declaring `Chart` or `SubChart`.

`position`: specifies how the `SubChart` will float within the `Chart` window.

`height` | `width`: Specifies the size of the `SubChart`, where `1` is the width/height of the window (100%)

`sync`: If given as `True`, the `SubChart`'s timescale and crosshair will follow that of the declaring `Chart` or `SubChart`. If a `str` is passed, the `SubChart` will follow the panel with the given id.  Chart ids  can be accessed from the`chart.id` and `subchart.id` attributes. 

```{important}
`width` and `height` should be given as a number between 0 and 1.
```

___


## Chart
`volume_enabled: bool` | `width: int` | `height: int` | `x: int` | `y: int` | `on_top: bool` | `maximize: bool` | `debug: bool` |
`api: object` | `topbar: bool` | `searchbox: bool` | `toolbox: bool`

The main object used for the normal functionality of lightweight-charts-python, built on the pywebview library.

```{important}
The `Chart` object should be defined within an `if __name__ == '__main__'` block.
```
___

### `show`
`block: bool`

Shows the chart window, blocking until the chart has loaded. If `block` is enabled, the method will block code execution until the window is closed.
___

### `hide`

Hides the chart window, which can be later shown by calling `chart.show()`.
___

### `exit`

Exits and destroys the chart window.

___

### `show_async`
`block: bool`

Show the chart asynchronously. This should be utilised when using [Callbacks](#callbacks).

### `screenshot`
`-> bytes`

Takes a screenshot of the chart, and returns a bytes object containing the image. For example:

```python
if __name__ == '__main__':
    chart = Chart()
    df = pd.read_csv('ohlcv.csv')
    chart.set(df)
    chart.show()
    
    img = chart.screenshot()
    with open('screenshot.png', 'wb') as f:
        f.write(img)
```

```{important}
This method should be called after the chart window has loaded.
```
___

### `add_hotkey`
`modifier: 'ctrl'/'shift'/'alt'/'meta'` | `key: str/int/tuple` | `method: object`

Adds a global hotkey to the chart window, which will execute the method or function given.

When using a number in `key`, it should be given as an integer. If multiple key commands are needed for the same function, you can pass a tuple to `key`. For example:

```python
def place_buy_order(key):
    print(f'Buy {key} shares.')
    
    
def place_sell_order(key):
    print(f'Sell all shares, because I pressed {key}.')


chart.add_hotkey('shift', (1, 2, 3), place_buy_order)
chart.add_hotkey('shift', 'X', place_sell_order)
```



___

## Line

The `Line` object represents a `LineSeries` object in Lightweight Charts and can be used to create indicators. As well as the methods described below, the `Line` object also has access to:
[`title`](#title), [`marker`](#marker), [`horizontal_line`](#horizontal-line) [`hide_data`](#hide-data), [`show_data`](#show-data) and[`price_line`](#price-line).

```{important}
The `Line` object should only be accessed from the [`create_line`](#create-line) method of `Chart`.
```
___

### `set`
`data: pd.DataFrame` `name: str`

Sets the data for the line.

When not using the `name` parameter, the columns should be named: `time | value` (Not case sensitive).

Otherwise, the method will use the column named after the string given in `name`. This name will also be used within the legend of the chart. For example:
```python
line = chart.create_line()

# DataFrame with columns: date | SMA 50
df = pd.read_csv('sma50.csv')

line.set(df, name='SMA 50')
```
___

### `update`
`series: pd.Series`

Updates the data for the line.

This should be given as a Series object, with labels akin to the `line.set()` function.
___

### `delete`

Irreversibly deletes the line.
___

## HorizontalLine

The `HorizontalLine` object represents a `PriceLine` in Lightweight Charts.

```{important}
The `HorizontalLine` object should only be accessed from the [`horizontal_line`](#horizontal-line) Common Method.
```
___

### `update`
`price: float/int`

Updates the price of the horizontal line.

___

### `delete`

Irreversibly deletes the horizontal line.
___

## SubChart

The `SubChart` object allows for the use of multiple chart panels within the same `Chart` window. All of the [Common Methods](#common-methods) can be used within a `SubChart`. Its instance should be accessed using the [create_subchart](#create-subchart) method.

`SubCharts` are arranged horizontally from left to right. When the available space is no longer sufficient, the subsequent `SubChart` will be positioned on a new row, starting from the left side.
___

### Grid of 4 Example:

```python
import pandas as pd
from lightweight_charts import Chart

if __name__ == '__main__':
    chart = Chart(inner_width=0.5, inner_height=0.5)

    chart2 = chart.create_subchart(position='right', width=0.5, height=0.5)

    chart3 = chart2.create_subchart(position='left', width=0.5, height=0.5)

    chart4 = chart3.create_subchart(position='right', width=0.5, height=0.5)

    chart.watermark('1')
    chart2.watermark('2')
    chart3.watermark('3')
    chart4.watermark('4')

    df = pd.read_csv('ohlcv.csv')
    chart.set(df)
    chart2.set(df)
    chart3.set(df)
    chart4.set(df)

    chart.show(block=True)

```
___

### Synced Line Chart Example:

```python
import pandas as pd
from lightweight_charts import Chart

if __name__ == '__main__':
    chart = Chart(inner_width=1, inner_height=0.8)
    chart.time_scale(visible=False)

    chart2 = chart.create_subchart(width=1, height=0.2, sync=True, volume_enabled=False)
    
    df = pd.read_csv('ohlcv.csv')
    df2 = pd.read_csv('rsi.csv')

    chart.set(df)
    line = chart2.create_line()
    line.set(df2)

    chart.show(block=True)

```
___

## Callbacks

The `Chart` object allows for asynchronous and synchronous callbacks to be passed back to python when using the `show_async` method, allowing for more sophisticated chart layouts including searching, timeframe selectors, and text boxes.

[`QtChart`](#qtchart) and [`WxChart`](#wxchart) can also use callbacks, however they use their respective event loops to emit callbacks rather than asyncio.

A variety of the parameters below should be passed to the Chart upon decaration.
* `api`: The class object that the fixed callbacks will always be emitted to (see [How to use Callbacks](#how-to-use-callbacks)).
* `topbar`: Adds a [TopBar](#topbar) to the `Chart` or `SubChart` and allows use of the `create_switcher` method.
* `searchbox`: Adds a search box onto the `Chart` or `SubChart` that is activated by typing.

___
### How to use Callbacks

Fixed Callbacks are emitted to the class given as the `api` parameter shown above.

Take a look at this minimal example:

```python
class API:
    def __init__(self):
        self.chart = None

    async def on_search(self, string):
        print(f'Search Text: "{string}" | Chart/SubChart ID: "{self.chart.id}"')
```
Upon searching in a pane, the expected output would be akin to:
```
Search Text: "AAPL" | Chart/SubChart ID: "window.blyjagcr"
```
The ID shown above will change depending upon which pane was used to search, due to the instance of `self.chart` dynamically updating to the latest pane which triggered the callback.
`self.chart` will update upon each callback, allowing for access to the specific [Common Methods](#common-methods) for the pane in question.

```{important}
* Search callbacks will always be emitted to a method named `on_search`
* `API` class methods can be either coroutines or normal methods.
* Non fixed callbacks (switchers, hotkeys) can be methods, coroutines, or regular functions.
```
___

### `TopBar`
The `TopBar` class represents the top bar shown on the chart when using callbacks:

![topbar](https://i.imgur.com/Qu2FW9Y.png)

This class is accessed from the `topbar` attribute of the chart object (`chart.topbar.<method>`), after setting the topbar parameter to `True` upon declaration of the chart.

Switchers and text boxes can be created within the top bar, and their instances can be accessed through the `topbar` dictionary. For example:

```python
chart = Chart(api=api, topbar=True)

chart.topbar.textbox('symbol', 'AAPL') # Declares a textbox displaying 'AAPL'.
print(chart.topbar['symbol'].value) # Prints the value within ('AAPL')

chart.topbar['symbol'].set('MSFT') # Sets the 'symbol' textbox to 'MSFT'
print(chart.topbar['symbol'].value) # Prints the value again ('MSFT')
```
___

### `switcher`
`name: str` | `method: function` | `*options: str` | `default: str`

* `name`: the name of the switcher which can be used to access it from the `topbar` dictionary.
* `method`: The function from the `api` class given to the constructor that will receive the callback.
* `options`: The strings to be displayed within the switcher. This may be a variety of timeframes, security types, or whatever needs to be updated directly from the chart.
* `default`: The initial switcher option set.
___

### `textbox`
`name: str` | `initial_text: str`

* `name`: the name of the text box which can be used to access it from the `topbar` dictionary.
* `initial_text`: The text to show within the text box.
___

### Callbacks Example:

```python
import asyncio
import pandas as pd
from my_favorite_broker import get_bar_data

from lightweight_charts import Chart


class API:
    def __init__(self):
        self.chart = None

    async def on_search(self, searched_string):  # Called when the user searches.
        timeframe = self.chart.topbar['timeframe'].value
        new_data = await get_bar_data(searched_string, timeframe)
        if not new_data:
            return
        self.chart.set(new_data)  # sets data for the Chart or SubChart in question.
        self.chart.topbar['symbol'].set(searched_string)

    async def on_timeframe(self):  # Called when the user changes the timeframe.
        timeframe = self.chart.topbar['timeframe'].value
        symbol = self.chart.topbar['symbol'].value
        new_data = await get_bar_data(symbol, timeframe)
        if not new_data:
            return
        self.chart.set(new_data)


async def main():
    api = API()

    chart = Chart(api=api, topbar=True, searchbox=True)

    chart.topbar.textbox('symbol', 'TSLA')
    chart.topbar.switcher('timeframe', api.on_timeframe, '1min', '5min', '30min', 'H', 'D', 'W', default='5min')

    df = pd.read_csv('ohlcv.csv')
    chart.set(df)

    await chart.show_async(block=True)


if __name__ == '__main__':
    asyncio.run(main())
```
___

## Toolbox
The Toolbox allows for trendlines, ray lines and horizontal lines to be drawn and edited directly on the chart.

It can be used within any Chart object, and is enabled by setting the `toolbox` parameter to `True` upon Chart declaration.

The following hotkeys can also be used when the Toolbox is enabled:
* Alt+T: Trendline
* Alt+H: Horizontal Line
* Alt+R: Ray Line
* Meta+Z or Ctrl+Z: Undo

Drawings can also be deleted by right-clicking on them, which brings up a context menu.
___

### `save_drawings_under`
`widget: Widget`

Saves drawings under a specific `topbar` text widget. For example:

```python
chart.toolbox.save_drawings_under(chart.topbar['symbol'])
```
___

### `load_drawings`
`tag: str`

Loads and displays drawings stored under the tag given.
___
### `import_drawings`
`file_path: str`

Imports the drawings stored at the JSON file given in `file_path`.

___
### `export_drawings`
`file_path: str`

Exports all currently saved drawings to the JSON file given in `file_path`.
___

## QtChart
`widget: QWidget` | `volume_enabled: bool`

The `QtChart` object allows the use of charts within a `QMainWindow` object, and has similar functionality to the `Chart` and `ChartAsync` objects for manipulating data, configuring and styling.

Callbacks can be recieved through the Qt event loop, using an [API](#how-to-use-callbacks) class that uses **syncronous** methods instead of **asyncronous** methods.
___

### `get_webview`

`-> QWebEngineView`

Returns the `QWebEngineView` object.

___
### Example:

```python
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from lightweight_charts.widgets import QtChart

app = QApplication([])
window = QMainWindow()
layout = QVBoxLayout()
widget = QWidget()
widget.setLayout(layout)

window.resize(800, 500)
layout.setContentsMargins(0, 0, 0, 0)

chart = QtChart(widget)

df = pd.read_csv('ohlcv.csv')
chart.set(df)

layout.addWidget(chart.get_webview())

window.setCentralWidget(widget)
window.show()

app.exec_()
```
___

## WxChart
`parent: wx.Panel` | `volume_enabled: bool`

The WxChart object allows the use of charts within a `wx.Frame` object, and has similar functionality to the `Chart` and `ChartAsync` objects for manipulating data, configuring and styling.

Callbacks can be recieved through the Wx event loop, using an [API](#how-to-use-callbacks) class that uses **syncronous** methods instead of **asyncronous** methods.
___

### `get_webview`
`-> wx.html2.WebView`

Returns a `wx.html2.WebView` object which can be used to for positioning and styling within wxPython.
___

### Example:

```python
import wx
import pandas as pd

from lightweight_charts.widgets import WxChart


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None)
        self.SetSize(1000, 500)

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)

        chart = WxChart(panel)

        df = pd.read_csv('ohlcv.csv')
        chart.set(df)

        sizer.Add(chart.get_webview(), 1, wx.EXPAND | wx.ALL)
        sizer.Layout()
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()

```
___

## StreamlitChart
`parent: wx.Panel` | `volume_enabled: bool`

The `StreamlitChart` object allows the use of charts within a Streamlit app, and has similar functionality to the `Chart` object for manipulating data, configuring and styling.

This object only supports the displaying of **static** data, and should not be used with the `update_from_tick` or `update` methods. Every call to the chart object must occur **before** calling `load`.
___

### `load`

Loads the chart into the Streamlit app. This should be called after setting, styling, and configuring the chart, as no further calls to the `StreamlitChart` will be acknowledged. 
___

### Example:
```python
import pandas as pd
from lightweight_charts.widgets import StreamlitChart

chart = StreamlitChart(width=900, height=600)

df = pd.read_csv('ohlcv.csv')
chart.set(df)

chart.load()
```
___

## JupyterChart

The `JupyterChart` object allows the use of charts within a notebook, and has similar functionality to the `Chart` object for manipulating data, configuring and styling.

This object only supports the displaying of **static** data, and should not be used with the `update_from_tick` or `update` methods. Every call to the chart object must occur **before** calling `load`.
___

### `load`

Renders the chart. This should be called after setting, styling, and configuring the chart, as no further calls to the `JupyterChart` will be acknowledged. 
___

### Example:
```python
import pandas as pd
from lightweight_charts import JupyterChart

chart = JupyterChart()

df = pd.read_csv('ohlcv.csv')
chart.set(df)

chart.load()
```
