# YFinance

```python
import datetime as dt
import yfinance as yf
from lightweight_charts import Chart


def get_bar_data(symbol, timeframe):
    if timeframe in ('1m', '5m', '30m'):
        days = 7 if timeframe == '1m' else 60
        start_date = dt.datetime.now()-dt.timedelta(days=days)
    else:
        start_date = None

    chart.spinner(True)
    data = yf.download(symbol, start_date, interval=timeframe)
    chart.spinner(False)

    if data.empty:
        return False
    chart.set(data)
    return True


def on_search(chart, searched_string):
    if get_bar_data(searched_string, chart.topbar['timeframe'].value):
        chart.topbar['symbol'].set(searched_string)


def on_timeframe_selection(chart):
    get_bar_data(chart.topbar['symbol'].value, chart.topbar['timeframe'].value)


if __name__ == '__main__':
    chart = Chart(toolbox=True, debug=True)
    chart.legend(True)
    chart.events.search += on_search
    chart.topbar.textbox('symbol', 'n/a')
    chart.topbar.switcher(
        'timeframe',
        ('1m', '5m', '30m', '1d', '1wk'),
        default='5m',
        func=on_timeframe_selection
    )

    chart.show(block=True)
```