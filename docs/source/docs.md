# Docs


## Common Methods
These methods can be used within the `Chart`, `QtChart`, and `WxChart` objects.
___
### `set`

`data: DataFrame`

~ Sets the initial data for the chart.

The data must be given as a DataFrame, with the columns:

`time | open | high | low | close | volume`

The 'time' column can also be named 'date', and the 'volume' column can be omitted if volume is not enabled.
___

### `update`
~ Updates the chart data from a given bar.

The bar should be one 'interval' away from the last bar, given as a Series object, and contain values with labels of the same name as the columns required for using `chart.set()`.
___

### `update_from_tick`
~ Updates the chart from a tick.

This should also be given as a Series object, and contain the columns:

`time | price | volume`

As before, the 'time' column can also be named 'date, and the 'volume' column can be omitted if volume is not enabled.

The provided ticks do not need to be rounded to an interval (1 min, 5 min etc.), as the library handles this automatically.
___

### `create_line`
~ Creates and returns a [Line](#line) object.
___

### `marker`
~ Creates a new marker, and returns its UUID.

If the `time` parameter is left blank, the marker will be placed at the latest bar.
___

### `remove_marker`
~ Removes the marker with the given UUID.

Usage:
```python
marker = chart.marker(text='hello_world')
chart.remove_marker(marker)
```
___

### `horizontal_line`
~ Creates a horizontal line at the given price.
___

### `remove_horizontal_line`
~ Removes a horizontal line at the given price.
___

### `config`
~ Config options for the chart.
___

### `time_scale`
~ Options for the time scale of the chart.
___

### `layout`
~ Global layout options for the chart.
___

### `candle_style`
~  Candle styling for each of the candle's parts (border, wick).
___

### `volume_config`
~ Volume config options.
___

### `crosshair`
~ Crosshair formatting for its vertical and horizontal axes.
___

### `watermark`
~ Adds a watermark to the chart.
___

### `legend`
~ Configures the legend of the chart.
___

### `subscribe_click`
~ Subscribes the given function to a chart 'click' event.

The event returns a dictionary containing the bar object at the time clicked.

___


## `Chart`
The main object used for the normal functionality of lightweight-charts-python.
___

### `show`
~ Shows the chart window.
___

### `hide`
~ Hides the chart window, and can be later shown by calling `chart.show()`.
___

### `exit`
~ Exits and destroys the chart and window.

___

## `Line`
The `Line` object represents a 'line series' in Lightweight Charts and can be used to create indicators.

```{important}
The `line` object should only be accessed from the [create_line](#create-line) method of `Chart`.
```
___

### `set`
~ Sets the data for the line.

This should be given as a DataFrame, with the columns: `time | price`
___

### `update`
~ Updates the data for the line.

This should be given as a Series object, with labels akin to the `line.set()` function.

___

## `WxChart`
The WxChart object allows the use of charts within a `wx.Frame` object, and has similar functionality to the `Chart` object for manipulating data, configuring and styling.

It is built upon the `wx.html2.WebView` object and the instance of this object can be accessed from the `get_webview()` function. For example:

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

## `QtChart`
The `QtChart` object allows the use of charts within a `QMainWindow` object, and has similar functionality to the `Chart` object for manipulating data, configuring and styling.

It is built upon the `QWebEngineView` object and the instance of this object can be accessed from the `get_webview()` function. For example:

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

