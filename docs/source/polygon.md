# Polygon.io

[Polygon.io's](https://polygon.io/?utm_source=affiliate&utm_campaign=pythonlwcharts) market data API is directly integrated within lightweight-charts-python, and is easy to use within the library.
___
## Requirements
To use data from Polygon, there are certain libraries (not listed as requirements) that must be installed:
* Static data requires the `requests` library.
* Live data requires the `websockets` library.
___
## `polygon`
`polygon` is a [Common Method](https://lightweight-charts-python.readthedocs.io/en/latest/docs.html#common-methods), and can be accessed from within any chart type.

`chart.polygon.<method>`

The `stock`, `option`, `index`, `forex`, and `crypto` methods of `chart.polygon` have common parameters:

* `timeframe`: The timeframe to be used (`'1min'`, `'5min'`, `'H'`, `'2D'`, `'5W'` etc.)
* `start_date`: The start date given in the format `YYYY-MM-DD`.
* `end_date`: The end date given in the same format. By default this is `'now'`, which uses the time now.
* `limit`: The maximum number of base aggregates to be queried to create the aggregate results.
* `live`: When set to `True`, a websocket connection will be used to update the chart or subchart in real-time. 
* These methods will also return a boolean representing whether the request was successful.

```{important}
When using live data and the standard `show` method, the `block` parameter __must__ be set to `True` in order for the data to congregate on the chart (`chart.show(block=True)`).
If `show_async` is used with live data, `block` can be either value.

```
___

### Example:

```python
from lightweight_charts import Chart

if __name__ == '__main__':
    chart = Chart()
    chart.polygon.api_key('<API-KEY>')
    chart.polygon.stock(
        symbol='AAPL',
        timeframe='5min',
        start_date='2023-06-09'
    )
    chart.show(block=True)
```
___

### `api_key`
`key: str`

Sets the API key for the chart. Subsequent `SubChart` objects will inherit the API key given to the parent chart.
___
### `stock`
`symbol: str` | `timeframe: str` | `start_date: str` | `end_date: str` | `limit: int` | `live: bool` | `-> bool`

Requests and displays stock data pulled from Polygon.io.
___

### `option`
`symbol: str` | `timeframe: str` | `start_date: str` | `expiration` | `right: 'C' | 'P'` | `strike: int | float` | `end_date: str` | `limit: int` | `live: bool` | `-> bool`

Requests and displays option data pulled from Polygon.io.

A formatted option ticker (SPY251219C00650000) can also be given to the `symbol` parameter, allowing for `expiration`, `right`, and `strike` to be left blank.
___

### `index`
`symbol: str` | `timeframe: str` | `start_date: str` | `end_date: str` | `limit: int` | `live: bool` | `-> bool`

Requests and displays index data pulled from Polygon.io.

___

### `forex`
`fiat_pair: str` | `timeframe: str` | `start_date: str` | `end_date: str` | `limit: int` | `live: bool` | `-> bool`

Requests and displays a forex pair pulled from Polygon.io.

The two currencies should be separated by a '-' (`USD-CAD`, `GBP-JPY`, etc.).

___

### `crypto`
`crypto_pair: str` | `timeframe: str` | `start_date: str` | `end_date: str` | `limit: int` | `live: bool` | `-> bool`

Requests and displays a crypto pair pulled from Polygon.io.

The two currencies should be separated by a '-' (`BTC-USD`, `ETH-BTC`, etc.).

___

### `log`
`info: bool`

If `True`, informational log messages (connection, subscriptions etc.) will be displayed in the console.

Data errors will always be shown in the console.
___

## PolygonChart

`api_key: str` | `live: bool` | `num_bars: int`

The `PolygonChart` provides an easy and complete way to use the Polygon.io API within lightweight-charts-python.

This object requires the `requests` library for static data, and the `websockets` library for live data.

All data is requested within the chart window through searching and selectors.

As well as the parameters from the [Chart](https://lightweight-charts-python.readthedocs.io/en/latest/docs.html#chart) object, PolygonChart also has the parameters:

* `api_key`: The user's Polygon.io API key.
* `num_bars`: The target number of bars to be displayed on the chart
* `limit`: The maximum number of base aggregates to be queried to create the aggregate results.
* `end_date`: The end date of the time window.
* `timeframe_options`: The selectors to be included within the timeframe selector.
* `security_options`: The selectors to be included within the security selector.
* `live`: If True, the chart will update in real-time.
___

### Example:

```python
from lightweight_charts import PolygonChart

if __name__ == '__main__':
    chart = PolygonChart(api_key='<API-KEY>',
                         num_bars=200,
                         limit=5000,
                         live=True)
    chart.show(block=True)
```

![PolygonChart png](https://raw.githubusercontent.com/louisnw01/lightweight-charts-python/main/docs/source/polygonchart.png)

