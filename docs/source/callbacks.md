# Events

Events allow asynchronous and synchronous callbacks to be passed back into python.

___
## `chart.events`

`events.search` `->`  `chart` | `string`: Fires upon searching. Searchbox will be automatically created.

`events.new_bar` `->`  `chart`: Fires when a new candlestick is added to the chart.

`events.range_change` `->` `chart` | `bars_before` | `bars_after`: Fires when the range (visibleLogicalRange) changes.

Chart events can be subscribed to using: `chart.events.<name> += <callable>`
___

## How to use Events

Take a look at this minimal example:

```python
from lightweight_charts import Chart


def on_search(chart, string):
    print(f'Search Text: "{string}" | Chart/SubChart ID: "{chart.id}"')
    
    
if __name__ == '__main__':
    chart = Chart()
    chart.events.search += on_search
    chart.show(block=True)

```
Upon searching in a pane, the expected output would be akin to:
```
Search Text: "AAPL" | Chart/SubChart ID: "window.blyjagcr"
```
The ID shown above will change depending upon which pane was used to search, allowing for access to the object in question.

```{important}
* When using `show` rather than `show_async`, block should be set to `True` (`chart.show(block=True)`).
* Event callables can be either coroutines, methods, or functions.
```

___

## `TopBar`
The `TopBar` class represents the top bar shown on the chart:

![topbar](https://i.imgur.com/Qu2FW9Y.png)

This object is accessed from the `topbar` attribute of the chart object (`chart.topbar.<method>`).

Switchers, text boxes and buttons can be added to the top bar, and their instances can be accessed through the `topbar` dictionary. For example:

```python
chart.topbar.textbox('symbol', 'AAPL') # Declares a textbox displaying 'AAPL'.
print(chart.topbar['symbol'].value) # Prints the value within ('AAPL')

chart.topbar['symbol'].set('MSFT') # Sets the 'symbol' textbox to 'MSFT'
print(chart.topbar['symbol'].value) # Prints the value again ('MSFT')
```

Events can also be emitted from the topbar. For example:

```python
from lightweight_charts import Chart

def on_button_press(chart):
    new_button_value = 'On' if chart.topbar['my_button'].value == 'Off' else 'Off'
    chart.topbar['my_button'].set(new_button_value)
    print(f'Turned something {new_button_value.lower()}.')
    
    
if __name__ == '__main__':
    chart = Chart()
    chart.topbar.button('my_button', 'Off', func=on_button_press)
    chart.show(block=True)

```

___

### `switcher`
`name: str` | `options: tuple` | `default: str` | `func: callable`

* `name`: the name of the switcher which can be used to access it from the `topbar` dictionary.
* `options`: The options for each switcher item.
* `default`: The initial switcher option set.
___

### `textbox`
`name: str` | `initial_text: str`

* `name`: the name of the text box which can be used to access it from the `topbar` dictionary.
* `initial_text`: The text to show within the text box.
___

### `button`
`name: str` | `button_text: str` | `separator: bool` | `func: callable`

* `name`: the name of the text box to access it from the `topbar` dictionary.
* `button_text`: Text to show within the button.
* `separator`: places a separator line to the right of the button.
* `func`: The event handler which will be executed upon a button click.
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


def on_search(chart, searched_string):
    new_data = get_bar_data(searched_string, chart.topbar['timeframe'].value)
    if new_data.empty:
        return
    chart.topbar['symbol'].set(searched_string)
    chart.set(new_data)

    
def on_timeframe_selection(chart):
    new_data = get_bar_data(chart.topbar['symbol'].value, chart.topbar['timeframe'].value)
    if new_data.empty:
        return
    chart.set(new_data, True)

    
def on_horizontal_line_move(chart, line):
    print(f'Horizontal line moved to: {line.price}')


if __name__ == '__main__':
    chart = Chart(toolbox=True)
    chart.legend(True)

    chart.topbar.textbox('symbol', 'TSLA')
    chart.topbar.switcher('timeframe', ('1min', '5min', '30min'), default='5min',
                          func=on_timeframe_selection)

    df = get_bar_data('TSLA', '5min')
    chart.set(df)

    chart.horizontal_line(200, func=on_horizontal_line_move)

    chart.show(block=True)
```
