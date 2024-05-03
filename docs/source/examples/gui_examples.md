# Alternative GUI's


## PyQt5 / PySide6

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



## WxPython

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
## Jupyter

```python
import pandas as pd
from lightweight_charts import JupyterChart

chart = JupyterChart()

df = pd.read_csv('ohlcv.csv')
chart.set(df)

chart.load()
```
___

## Streamlit

```python
import pandas as pd
from lightweight_charts.widgets import StreamlitChart

chart = StreamlitChart(width=900, height=600)

df = pd.read_csv('ohlcv.csv')
chart.set(df)

chart.load()
```
___

## Flask

```python
from lightweight_charts.widgets import FlaskChart
from flask import Flask
import pandas as pd

app = Flask(__name__)

@app.route('/')
def static_chart():
    df = pd.read_csv('ohlcv.csv')

    chart = FlaskChart(title='My Static Chart')
    chart.set(df)
    return chart.load()

if __name__ == '__main__':
    app.run()
```
