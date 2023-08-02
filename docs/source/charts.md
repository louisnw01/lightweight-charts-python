# Charts

This page contains a reference to all chart objects that can be used within the library. They all have access to the common methods.

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

Show the chart asynchronously.
___

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

## QtChart
`widget: QWidget` | `volume_enabled: bool`

The `QtChart` object allows the use of charts within a `QMainWindow` object, and has similar functionality to the `Chart` and `ChartAsync` objects for manipulating data, configuring and styling.

Callbacks can be recieved through the Qt event loop.
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

Callbacks can be recieved through the Wx event loop.
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
