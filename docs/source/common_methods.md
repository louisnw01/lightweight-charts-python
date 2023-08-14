# Common Methods
The methods below can be used within all chart objects.

___
## `set`
`data: pd.DataFrame` `render_drawings: bool`

Sets the initial data for the chart. The data must be given as a DataFrame, with the columns:

`time | open | high | low | close | volume`

The `time` column can also be named `date` or be the index, and the `volume` column can be omitted if volume is not enabled. Column names are not case sensitive.

If `render_drawings` is `True`, any drawings made using the `toolbox` will be redrawn with the new data. This is designed to be used when switching to a different timeframe of the same symbol.

```{important}
the `time` column must have rows all of the same timezone and locale. This is particularly noticeable for data which crosses over daylight saving hours on data with intervals of less than 1 day. Errors are likely to be raised if they are not converted beforehand.
```

An empty `DataFrame` object or `None` can also be given to this method, which will erase all candle and volume data displayed on the chart.
___

## `update`
`series: pd.Series`

Updates the chart data from a `pd.Series` object. The bar should contain values with labels akin to `set`.
___

## `update_from_tick`
`series: pd.Series` | `cumulative_volume: bool`

Updates the chart from a tick. The series should use the labels:

`time | price | volume`

As before, the `time` can also be named `date`, and the `volume` can be omitted if volume is not enabled. The `time` column can also be the name of the Series object.

```{information}
The provided ticks do not need to be rounded to an interval (1 min, 5 min etc.), as the library handles this automatically.
```

If `cumulative_volume` is used, the volume data given will be added onto the latest bar of volume data.
___

## `create_line` (Line)
`name: str` | `color: str` | `style: LINE_STYLE`| `width: int` | `price_line: bool` | `price_label: bool` | `-> Line`

Creates and returns a `Line` object, representing a `LineSeries` object in Lightweight Charts and can be used to create indicators. As well as the methods described below, the `Line` object also has access to:
[`title`](#title), [`marker`](#marker), [`horizontal_line`](#horizontal-line) [`hide_data`](#hide-data), [`show_data`](#show-data) and[`price_line`](#price-line).

Its instance should only be accessed from this method.

### `set`
`data: pd.DataFrame`

Sets the data for the line.

When a name has not been set upon declaration, the columns should be named: `time | value` (Not case sensitive).

Otherwise, the method will use the column named after the string given in `name`. This name will also be used within the legend of the chart. For example:
```python
line = chart.create_line('SMA 50')

# DataFrame with columns: date | SMA 50
df = pd.read_csv('sma50.csv')

line.set(df)
```

### `update`
`series: pd.Series`

Updates the data for the line.

This should be given as a Series object, with labels akin to the `line.set()` function.

### `delete`
Irreversibly deletes the line.

___

## `lines`
`-> List[Line]`

Returns a list of all lines for the chart or subchart.
___

## `trend_line`
`start_time: str/datetime` | `start_value: float/int` | `end_time: str/datetime` | `end_value: float/int` | `color: str` | `width: int` | `-> Line`

Creates a trend line, drawn from the first point (`start_time`, `start_value`) to the last point (`end_time`, `end_value`).
___

## `ray_line`
`start_time: str/datetime` | `value: float/int` | `color: str` | `width: int` | `-> Line`

Creates a ray line, drawn from the first point (`start_time`, `value`) and onwards.
___

## `marker`
`time: datetime` | `position: 'above'/'below'/'inside'` | `shape: 'arrow_up'/'arrow_down'/'circle'/'square'` | `color: str` | `text: str` | `-> str`

Adds a marker to the chart, and returns its id.

If the `time` parameter is not given, the marker will be placed at the latest bar.

When using multiple markers, they should be placed in chronological order or display bugs may be present.
___

## `remove_marker`
`marker_id: str`

Removes the marker with the given id.

Usage:
```python
marker = chart.marker(text='hello_world')
chart.remove_marker(marker)
```
___

## `horizontal_line` (HorizontalLine)
`price: float/int` | `color: str` | `width: int` | `style: 'solid'/'dotted'/'dashed'/'large_dashed'/'sparse_dotted'` | `text: str` | `axis_label_visible: bool` | `interactive: bool` | `-> HorizontalLine`

Places a horizontal line at the given price, and returns a `HorizontalLine` object, representing a `PriceLine` in Lightweight Charts.

If `interactive` is set to `True`, this horizontal line can be edited on the chart. Upon its movement a callback will also be emitted to an `on_horizontal_line_move` method, containing its ID and price. The toolbox should be enabled during its usage. It is designed to be used to update an order (limit, stop, etc.) directly on the chart.


### `update`
`price: float/int`

Updates the price of the horizontal line.

### `label`
`text: str`

Updates the label of the horizontal line.

### `delete`

Irreversibly deletes the horizontal line.
___

## `remove_horizontal_line`
`price: float/int`

Removes a horizontal line at the given price.
___

## `clear_markers`

Clears the markers displayed on the data.
___

## `clear_horizontal_lines`

Clears the horizontal lines displayed on the data.
___

## `precision`
`precision: int`

Sets the precision of the chart based on the given number of decimal places.
___

## `price_scale`
`mode: 'normal'/'logarithmic'/'percentage'/'index100'` | `align_labels: bool` | `border_visible: bool` | `border_color: str` | `text_color: str` | `entire_text_only: bool` | `ticks_visible: bool` | `scale_margin_top: float` | `scale_margin_bottom: float`

Price scale options for the chart.
___

## `time_scale`
`right_offset: int` | `min_bar_spacing: float` | `visible: bool` | `time_visible: bool` | `seconds_visible: bool` | `border_visible: bool` | `border_color: str`

Timescale options for the chart.
___

## `layout`
`background_color: str` | `text_color: str` | `font_size: int` | `font_family: str`

Global layout options for the chart.
___

## `grid`
`vert_enabled: bool` | `horz_enabled: bool` | `color: str` | `style: 'solid'/'dotted'/'dashed'/'large_dashed'/'sparse_dotted'`

Grid options for the chart.
___

## `candle_style`
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

## `volume_config`
`scale_margin_top: float` | `scale_margin_bottom: float` | `up_color: str` | `down_color: str`

Volume config options.

```{important}
The float values given to scale the margins must be greater than 0 and less than 1.
```
___

## `crosshair`
`mode` | `vert_visible: bool` | `vert_width: int` | `vert_color: str` | `vert_style: str` | `vert_label_background_color: str` | `horz_visible: bool` | `horz_width: int` | `horz_color: str` | `horz_style: str` | `horz_label_background_color: str`

Crosshair formatting for its vertical and horizontal axes.

`vert_style` and `horz_style` should be given as one of: `'solid'/'dotted'/'dashed'/'large_dashed'/'sparse_dotted'`
___

## `watermark`
`text: str` | `font_size: int` | `color: str`

Overlays a watermark on top of the chart.
___

## `legend`
`visible: bool` | `ohlc: bool` | `percent: bool` | `lines: bool` | `color: str` | `font_size: int` | `font_family: str`

Configures the legend of the chart.
___

## `spinner`
`visible: bool`

Shows a loading spinner on the chart, which can be used to visualise the loading of large datasets, API calls, etc.
___

## `price_line`
`label_visible: bool` | `line_visible: bool` | `title: str`

Configures the visibility of the last value price line and its label.
___

## `fit`

Attempts to fit all data displayed on the chart within the viewport (`fitContent()`).
___

## `hide_data`

Hides the candles on the chart.
___

## `show_data`

Shows the hidden candles on the chart.
___

## `hotkey`
`modifier: 'ctrl'/'shift'/'alt'/'meta'` | `key: str/int/tuple` | `func: callable`

Adds a global hotkey to the chart window, which will execute the method or function given.

When using a number in `key`, it should be given as an integer. If multiple key commands are needed for the same function, you can pass a tuple to `key`. For example:

```python
def place_buy_order(key):
    print(f'Buy {key} shares.')


def place_sell_order(key):
    print(f'Sell all shares, because I pressed {key}.')


if __name__ == '__main__':
    chart = Chart()
    chart.hotkey('shift', (1, 2, 3), place_buy_order)
    chart.hotkey('shift', 'X', place_sell_order)
    chart.show(block=True)
```

___

## `create_table`
`width: int/float` | `height: int/float` | `headings: tuple[str]` | `widths: tuple[float]` | `alignments: tuple[str]` | `position: 'left'/'right'/'top'/'bottom'` | `draggable: bool` | `func: callable` | `-> Table` 

Creates and returns a [`Table`](https://lightweight-charts-python.readthedocs.io/en/latest/tables.html) object.
___

## `create_subchart` (SubChart)
`position: 'left'/'right'/'top'/'bottom'`, `width: float` | `height: float` | `sync: bool/str` | `scale_candles_only: bool`|`toolbox: bool` | `-> SubChart`

Creates and returns a `SubChart` object, placing it adjacent to the previous `Chart` or `SubChart`. This allows for the use of multiple chart panels within the same `Chart` window. Its instance should only be accessed by using this method.

`position`: specifies how the Subchart will float.

`height` | `width`: Specifies the size of the Subchart, where `1` is the width/height of the window (100%)

`sync`: If given as `True`, the Subchart's timescale and crosshair will follow that of the declaring `Chart` or `SubChart`. If a `str` is passed, the `SubChart` will follow the panel with the given id.  Chart ids  can be accessed from the`chart.id` and `subchart.id` attributes. 

```{important}
`width` and `height` should be given as a number between 0 and 1.
```

`SubCharts` are arranged horizontally from left to right. When the available space is no longer sufficient, the subsequent `SubChart` will be positioned on a new row, starting from the left side.

### Grid of 4 Example:

```python
import pandas as pd
from lightweight_charts import Chart

if __name__ == '__main__':
    chart = Chart(inner_width=0.5, inner_height=0.5)
    chart2 = chart.create_subchart(position='right', width=0.5, height=0.5)
    chart3 = chart.create_subchart(position='left', width=0.5, height=0.5)
    chart4 = chart.create_subchart(position='right', width=0.5, height=0.5)

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

### Synced Line Chart Example:

```python
import pandas as pd
from lightweight_charts import Chart

if __name__ == '__main__':
    chart = Chart(inner_width=1, inner_height=0.8)
    chart.time_scale(visible=False)

    chart2 = chart.create_subchart(width=1, height=0.2, sync=True)
    line = chart2.create_line()
    
    df = pd.read_csv('ohlcv.csv')
    df2 = pd.read_csv('rsi.csv')

    chart.set(df)
    line.set(df2)

    chart.show(block=True)
```


