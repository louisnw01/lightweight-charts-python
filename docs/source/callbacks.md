# Callbacks

The `Chart` object allows for asynchronous and synchronous callbacks to be passed back to python, allowing for more sophisticated chart layouts including searching, timeframe selectors text boxes, and hotkeys using the `add_hotkey` method.

`QtChart`and `WxChart` can also use callbacks.

A variety of the parameters below should be passed to the Chart upon decaration.
* `api`: The class object that the fixed callbacks will always be emitted to.
* `topbar`: Adds a [TopBar](#topbar) to the `Chart` or `SubChart` and allows use of the `create_switcher` method.
* `searchbox`: Adds a search box onto the `Chart` or `SubChart` that is activated by typing.

___
## How to use Callbacks

Fixed Callbacks are emitted to the class given as the `api` parameter shown above.

Take a look at this minimal example:

```python
class API:
    def __init__(self):
        self.chart = None

    def on_search(self, string):
        print(f'Search Text: "{string}" | Chart/SubChart ID: "{self.chart.id}"')
```
Upon searching in a pane, the expected output would be akin to:
```
Search Text: "AAPL" | Chart/SubChart ID: "window.blyjagcr"
```
The ID shown above will change depending upon which pane was used to search, due to the instance of `self.chart` dynamically updating to the latest pane which triggered the callback.
`self.chart` will update upon each callback, allowing for access to the specific pane in question.

```{important}
* When using `show` rather than `show_async`, block should be set to `True` (`chart.show(block=True)`).
* `API` class methods can be either coroutines or normal methods.
* Non fixed callbacks (switchers, hotkeys) can be methods, coroutines, or regular functions.
```

There are certain callbacks which are always emitted to a specifically named method of API:
* Search callbacks: `on_search`
* Interactive Horizontal Line callbacks: `on_horizontal_line_move`

___

## `TopBar`
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

## Callbacks Example:

```python
import pandas as pd
from lightweight_charts import Chart


def get_bar_data(symbol, timeframe):
    if symbol not in ('AAPL', 'GOOGL', 'TSLA'):
        print(f'No data for "{symbol}"')
        return pd.DataFrame()
    return pd.read_csv(f'../examples/6_callbacks/bar_data/{symbol}_{timeframe}.csv')


class API:
    def __init__(self):
        self.chart = None  # Changes after each callback.

    def on_search(self, searched_string):  # Called when the user searches.
        new_data = get_bar_data(searched_string, self.chart.topbar['timeframe'].value)
        if new_data.empty:
            return
        self.chart.topbar['symbol'].set(searched_string)
        self.chart.set(new_data)

    def on_timeframe_selection(self):  # Called when the user changes the timeframe.
        new_data = get_bar_data(self.chart.topbar['symbol'].value, self.chart.topbar['timeframe'].value)
        if new_data.empty:
            return
        self.chart.set(new_data, True)

    def on_horizontal_line_move(self, line_id, price):
        print(f'Horizontal line moved to: {price}')


if __name__ == '__main__':
    api = API()

    chart = Chart(api=api, topbar=True, searchbox=True, toolbox=True)
    chart.legend(True)

    chart.topbar.textbox('symbol', 'TSLA')
    chart.topbar.switcher('timeframe', api.on_timeframe_selection, '1min', '5min', '30min', default='5min')

    df = get_bar_data('TSLA', '5min')
    chart.set(df)

    chart.horizontal_line(200, interactive=True)

    chart.show(block=True)
```
