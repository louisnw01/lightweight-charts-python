# `Histogram`


````{py:class} Histogram(name: str, color: COLOR, style: LINE_STYLE, width: int, price_line: bool, price_label: bool)

The `Histogram` object represents a `HistogramSeries` object in Lightweight Charts and can be used to create indicators. As well as the methods described below, the `Line` object also has access to:

[`horizontal_line`](#AbstractChart.horizontal_line), [`hide_data`](#hide_data), [`show_data`](#show_data) and [`price_line`](#price_line).

Its instance should only be accessed from [`create_histogram`](#AbstractChart.create_histogram).
___



```{py:method} set(data: pd.DataFrame) 

Sets the data for the histogram.

When a name has not been set upon declaration, the columns should be named: `time | value` (Not case sensitive).

The column containing the data should be named after the string given in the `name`.

A `color` column can be used within the dataframe to specify the color of individual bars.

```
___



```{py:method} update(series: pd.Series)

Updates the data for the histogram.

This should be given as a Series object, with labels akin to the `histogram.set` method.
```
___


```{py:method} scale(scale_margin_top: float, scale_margin_bottom: float)
Scales the margins of the histogram, as used within [`volume_config`](#AbstractChart.volume_config).
```


___

```{py:method} delete()

Irreversibly deletes the histogram.

```
````