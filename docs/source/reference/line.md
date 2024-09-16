# `Line`


````{py:class} Line(name: str, color: COLOR, style: LINE_STYLE, width: int, price_line: bool, price_label: bool, price_scale_id: str)

The `Line` object represents a `LineSeries` object in Lightweight Charts and can be used to create indicators. As well as the methods described below, the `Line` object also has access to:

[`marker`](#marker), [`horizontal_line`](#AbstractChart.horizontal_line), [`hide_data`](#hide_data), [`show_data`](#show_data) and [`price_line`](#price_line).

Its instance should only be accessed from [`create_line`](#AbstractChart.create_line).
___



```{py:method} set(data: pd.DataFrame)

Sets the data for the line.

When a name has not been set upon declaration, the columns should be named: `time | value` (Not case sensitive).

Otherwise, the method will use the column named after the string given in `name`. This name will also be used within the legend of the chart.

```
___



```{py:method} update(series: pd.Series)

Updates the data for the line.

This should be given as a Series object, with labels akin to the `line.set()` function.
```



___

```{py:method} delete()

Irreversibly deletes the line.

```
````
