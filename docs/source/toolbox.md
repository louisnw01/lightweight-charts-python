# Toolbox
The Toolbox allows for trendlines, ray lines and horizontal lines to be drawn and edited directly on the chart.

It can be used within any Chart object, and is enabled by setting the `toolbox` parameter to `True` upon Chart declaration.

The following hotkeys can also be used when the Toolbox is enabled:
* Alt+T: Trendline
* Alt+H: Horizontal Line
* Alt+R: Ray Line
* Meta+Z or Ctrl+Z: Undo


Right-clicking on a drawing will open a context menu, allowing for color selection and deletion.

___

## `save_drawings_under`
`widget: Widget`

Saves drawings under a specific `topbar` text widget. For example:

```python
chart.toolbox.save_drawings_under(chart.topbar['symbol'])
```
___

## `load_drawings`
`tag: str`

Loads and displays drawings stored under the tag given.
___

## `import_drawings`
`file_path: str`

Imports the drawings stored at the JSON file given in `file_path`.
___

## `export_drawings`
`file_path: str`

Exports all currently saved drawings to the JSON file given in `file_path`.
___

## Example:

To get started, create a file called `drawings.json`, which should only contain `{}`.

```python
import pandas as pd
from lightweight_charts import Chart


def get_bar_data(symbol, timeframe):
    if symbol not in ('AAPL', 'GOOGL', 'TSLA'):
        print(f'No data for "{symbol}"')
        return pd.DataFrame()
    return pd.read_csv(f'bar_data/{symbol}_{timeframe}.csv')


def on_search(chart, searched_string):
    new_data = get_bar_data(searched_string, chart.topbar['timeframe'].value)
    if new_data.empty:
        return
    chart.topbar['symbol'].set(searched_string)
    chart.set(new_data)
    chart.toolbox.load_drawings(searched_string)  # Loads the drawings saved under the symbol.


def on_timeframe_selection(chart):
    new_data = get_bar_data(chart.topbar['symbol'].value, chart.topbar['timeframe'].value)
    if new_data.empty:
        return
    chart.set(new_data, render_drawings=True)  # The symbol has not changed, so we want to re-render the drawings.


if __name__ == '__main__':
    chart = Chart(toolbox=True)
    chart.legend(True)

    chart.events.search += on_search
    chart.topbar.textbox('symbol', 'TSLA')
    chart.topbar.switcher('timeframe', ('1min', '5min', '30min'), default='5min', func=on_timeframe_selection)

    df = get_bar_data('TSLA', '5min')

    chart.set(df)

    chart.toolbox.import_drawings('drawings.json')  # Imports the drawings saved in the JSON file.
    chart.toolbox.load_drawings(chart.topbar['symbol'].value)  # Loads the drawings under the default symbol.

    chart.toolbox.save_drawings_under(chart.topbar['symbol'])  # Saves drawings based on the symbol.

    chart.show(block=True)

    chart.toolbox.export_drawings('drawings.json')  # Exports the drawings to the JSON file upon close.

```
