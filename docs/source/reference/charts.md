# Charts

This page contains a reference to all chart objects that can be used within the library.

They inherit from [AbstractChart](#AbstractChart).

___

`````{py:class} Chart(width: int, height: int, x: int, y: int, title: str, screen: int, on_top: bool, maximize: bool, debug: bool, toolbox: bool, inner_width: float, inner_height: float, scale_candles_only: bool)

The main object used for the normal functionality of lightweight-charts-python, built on the pywebview library.

The `screen` parameter defines which monitor the chart window will open on, given as an index (primary monitor = 0).

```{important}
The `Chart` object should be defined within an `if __name__ == '__main__'` block.
```
___



```{py:method} show(block: bool)

Shows the chart window, blocking until the chart has loaded. If `block` is enabled, the method will block code execution until the window is closed.

```
___



```{py:method} hide()

Hides the chart window, which can be later shown by calling `chart.show()`.
```
___



```{py:method} exit()

Exits and destroys the chart window.

```
___



```{py:method} show_async()
:async:

Show the chart asynchronously.

```
___



````{py:method} screenshot(block: bool) -> bytes

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
````

`````
___



````{py:class} QtChart(widget: QWidget)

The `QtChart` object allows the use of charts within a `QMainWindow` object, and has similar functionality to the `Chart` object for manipulating data, configuring and styling.

Either the `PyQt5`, `PyQt6` or `PySide6` libraries will work with this chart.

Callbacks can be received through the Qt event loop.
___



```{py:method} get_webview() -> QWebEngineView

Returns the `QWebEngineView` object.

```
````
___



````{py:class} WxChart(parent: WxPanel)
The WxChart object allows the use of charts within a `wx.Frame` object, and has similar functionality to the `Chart` object for manipulating data, configuring and styling.

Callbacks can be received through the Wx event loop.
___



```{py:method} get_webview() -> wx.html2.WebView

Returns a `wx.html2.WebView` object which can be used to for positioning and styling within wxPython.


```
````
___



````{py:class} StreamlitChart
The `StreamlitChart` object allows the use of charts within a Streamlit app, and has similar functionality to the `Chart` object for manipulating data, configuring and styling.

This object only supports the displaying of **static** data, and should not be used with the `update_from_tick` or `update` methods. Every call to the chart object must occur **before** calling `load`.

___



```{py:method} load()

Loads the chart into the Streamlit app. This should be called after setting, styling, and configuring the chart, as no further calls to the `StreamlitChart` will be acknowledged.

```
````
___



````{py:class} JupyterChart

The `JupyterChart` object allows the use of charts within a notebook, and has similar functionality to the `Chart` object for manipulating data, configuring and styling.

This object only supports the displaying of **static** data, and should not be used with the `update_from_tick` or `update` methods. Every call to the chart object must occur **before** calling `load`.
___



```{py:method} load()

Renders the chart. This should be called after setting, styling, and configuring the chart, as no further calls to the `JupyterChart` will be acknowledged. 

```
````
