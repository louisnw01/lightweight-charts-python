
# `AbstractChart`

`````{py:class} AbstractChart(width, height)
Abstracted chart used to create child classes.

___



```{py:method} set(data: pd.DataFrame, keep_drawings: bool = False)
Sets the initial data for the chart.


Columns should be named:
: `time | open | high | low | close | volume`

Time can be given in the index rather than a column, and volume can be omitted if volume is not used. Column names are not case sensitive.

If `keep_drawings` is `True`, any drawings made using the `toolbox` will be redrawn with the new data. This is designed to be used when switching to a different timeframe of the same symbol.

`None` can also be given, which will erase all candle and volume data displayed on the chart.

You can also add columns to color the candles (https://tradingview.github.io/lightweight-charts/tutorials/customization/data-points)
```


___



```{py:method} update(series: pd.Series, keep_drawings: bool = False)
Updates the chart data from a bar.

Series labels should be akin to [`set`](#AbstractChart.set).

```


___


```{py:method} update_from_tick(series: pd.Series, cumulative_volume: bool = False)
Updates the chart from a tick.

Labels should be named:
: `time | price | volume`

As before, the `time` can also be named `date`, and the `volume` can be omitted if volume is not enabled. The `time` column can also be the name of the Series object.

The provided ticks do not need to be rounded to an interval (1 min, 5 min etc.), as the library handles this automatically.

If `cumulative_volume` is used, the volume data given will be added onto the latest bar of volume data.
```
___



```{py:method} create_line(name: str, color: COLOR, style: LINE_STYLE, width: int, price_line: bool, price_label: bool) -> Line

Creates and returns a Line object, representing a `LineSeries` object in Lightweight Charts and can be used to create indicators. As well as the methods described below, the `Line` object also has access to:

[`marker`](#marker), [`horizontal_line`](#AbstractChart.horizontal_line), [`hide_data`](#hide_data), [`show_data`](#show_data) and [`price_line`](#price_line).

Its instance should only be accessed from this method.
```
___



```{py:method} create_histogram(name: str, color: COLOR, price_line: bool, price_label: bool, scale_margin_top: float, scale_margin_bottom: float) -> Histogram

Creates and returns a Histogram object, representing a `HistogramSeries` object in Lightweight Charts and can be used to create indicators. As well as the methods described below, the object also has access to:

[`horizontal_line`](#AbstractChart.horizontal_line), [`hide_data`](#hide_data), [`show_data`](#show_data) and [`price_line`](#price_line).

Its instance should only be accessed from this method.
```
___



```{py:method} lines() -> List[Line]

Returns a list of all lines for the chart.

```
___



```{py:method} trend_line(start_time: str | datetime, start_value: NUM, end_time: str | datetime, end_value: NUM, color: COLOR, width: int, style: LINE_STYLE, round: bool) -> Line

Creates a trend line, drawn from the first point (`start_time`, `start_value`) to the last point (`end_time`, `end_value`).

```
___



```{py:method} ray_line(start_time: str | datetime, value: NUM, color: COLOR, width: int, style: LINE_STYLE, round: bool) -> Line

Creates a ray line, drawn from the first point (`start_time`, `value`) and onwards.

```
___



```{py:method} vertical_span(start_time: TIME | list | tuple, end_time: TIME = None, color: COLOR = 'rgba(252, 219, 3, 0.2)', round: bool = False)

Creates and returns a `VerticalSpan` object.

If `end_time` is not given, then a single vertical line will be placed at `start_time`.

If a list/tuple is passed to `start_time`, vertical lines will be placed at each time.

This should be used after calling [`set`](#AbstractChart.set).
```
___



```{py:method} set_visible_range(self, start_time: TIME, end_time: TIME)

Sets the visible range of the chart.
```
___



```{py:method} resize(self, width: float = None, height: float = None)

Resizes the chart within the window.

Dimensions should be given as a float between or equal to 0 and 1.

Both `width` and `height` do not need to be provided if only one axis is to be changed.
```
___



```{py:method} marker(time: datetime, position: MARKER_POSITION, shape: MARKER_SHAPE, color: COLOR, text: str) -> str

Adds a marker to the chart, and returns its id.

If the `time` parameter is not given, the marker will be placed at the latest bar.

When using multiple markers, they should be placed in chronological order or display bugs may be present.

```
___



```{py:method} marker_list(markers: list) -> List[str]

Creates multiple markers and returns a list of marker ids.

```


```{py:method} remove_marker(marker_id: str)

Removes the marker with the given id.

```
___



```{py:method} horizontal_line(price: NUM, color: COLOR, width: int, style: LINE_STYLE, text: str, axis_label_visible: bool, func: callable= None) -> HorizontalLine

Places a horizontal line at the given price, and returns a [`HorizontalLine`] object.

If a `func` is given, the horizontal line can be edited on the chart. Upon its movement a callback will also be emitted to the callable given, containing the HorizontalLine object. The toolbox should be enabled during its usage. It is designed to be used to update an order (limit, stop, etc.) directly on the chart.

```
___



```{py:method} clear_markers()

Clears the markers displayed on the data.
```
___



```{py:method} precision(precision: int)

Sets the precision of the chart based on the given number of decimal places.

```
___



```{py:method} price_scale(auto_scale: bool, mode: PRICE_SCALE_MODE, invert_scale: bool, align_labels: bool, scale_margin_top: float, scale_margin_bottom: float, border_visible: bool, border_color: COLOR, text_color: COLOR, entire_text_only: bool, visible: bool, ticks_visible: bool, minimum_width: float)

Price scale options for the chart.
```
___



```{py:method} time_scale(right_offset: int, min_bar_spacing: float, visible: bool, time_visible: bool, seconds_visible: bool, border_visible: bool, border_color: COLOR)

Timescale options for the chart.
```
___



```{py:method} layout(background_color: COLOR, text_color: COLOR, font_size: int, font_family: str)

Global layout options for the chart.
```
___



```{py:method} grid(vert_enabled: bool, horz_enabled: bool, color: COLOR, style: LINE_STYLE)

Grid options for the chart.
```
___



```{py:method} candle_style(up_color: COLOR, down_color: COLOR, wick_enabled: bool, border_enabled: bool, border_up_color: COLOR, border_down_color: COLOR, wick_up_color: COLOR, wick_down_color: COLOR)

Candle styling for each of the candle's parts (border, wick).
```
___



```{py:method} volume_config(scale_margin_top: float, scale_margin_bottom: float, up_color: COLOR, down_color: COLOR)

Volume config options.

```{important}
The float values given to scale the margins must be greater than 0 and less than 1.
```
___



```{py:method} crosshair(mode, vert_visible: bool, vert_width: int, vert_color: COLOR, vert_style: LINE_STYLE, vert_label_background_color: COLOR, horz_visible: bool, horz_width: int, horz_color: COLOR, horz_style: LINE_STYLE, horz_label_background_color: COLOR)

Crosshair formatting for its vertical and horizontal axes.
```
___



```{py:method} watermark(text: str, font_size: int, color: COLOR)

Overlays a watermark on top of the chart.
```
___



```{py:method} legend(visible: bool, ohlc: bool, percent: bool, lines: bool, color: COLOR, font_size: int, font_family: str, text: str, color_based_on_candle: bool)

Configures the legend of the chart.
```
___



```{py:method} spinner(visible: bool)

Shows a loading spinner on the chart, which can be used to visualise the loading of large datasets, API calls, etc.

```{important}
This method must be used in conjunction with the search event.
```
___



```{py:method} price_line(label_visible: bool, line_visible: bool, title: str)

Configures the visibility of the last value price line and its label.
```
___



```{py:method} fit()

Attempts to fit all data displayed on the chart within the viewport (`fitContent()`).
```
___



```{py:method} show_data()

Shows the hidden candles on the chart.
```
___



```{py:method} hide_data()

Hides the candles on the chart.
```
___



```{py:method} hotkey(modifier: 'ctrl' | 'alt' | 'shift' | 'meta' | None, key: 'str' | 'int' | 'tuple', func: callable)

Adds a global hotkey to the chart window, which will execute the method or function given.

If multiple key commands are needed for the same function, a tuple can be passed to `key`.
```
___



```{py:method} create_table(width: NUM, height: NUM, headings: Tuple[str], widths: Tuple[float], alignments: Tuple[str], position: FLOAT, draggable: bool, return_clicked_cells: bool, func: callable) -> Table

Creates and returns a [`Table`](https://lightweight-charts-python.readthedocs.io/en/latest/tables.html) object.

```
___



````{py:method} create_subchart(position: FLOAT, width: float, height: float, sync: bool | str, sync_crosshairs_only: bool, scale_candles_only: bool, toolbox: bool) -> AbstractChart 

Creates and returns a Chart object, placing it adjacent to the previous Chart. This allows for the use of multiple chart panels within the same window.

`position`
: specifies how the Subchart will float.

`height` | `width`
: Specifies the size of the Subchart, where `1` is the width/height of the window (100%)

`sync`
: If given as `True`, the Subchart's timescale and crosshair will follow that of the declaring Chart. If a `str` is passed, the Chart will follow the panel with the given id.  Chart ids  can be accessed from the `chart.id` attribute. 

`sync_crosshairs_only`
: If given as `True`, only the crosshairs will be synced and movement will remain independant.

```{important}
`width` and `height` should be given as a number between 0 and 1.
```

Charts are arranged horizontally from left to right. When the available space is no longer sufficient, the subsequent Chart will be positioned on a new row, starting from the left side.

[Subchart examples](../examples/subchart.md)

```{important}
Price axis scales vary depending on the precision of the data used, and there is no way to perfectly 'align' two seperate price scales if they contain differing price data.
```

````
`````








