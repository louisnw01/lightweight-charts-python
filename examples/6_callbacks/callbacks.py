import asyncio
import pandas as pd

from lightweight_charts import Chart


def get_bar_data(symbol, timeframe):
    if symbol not in ('AAPL', 'GOOGL', 'TSLA'):
        print(f'No data for "{symbol}"')
        return pd.DataFrame()
    return pd.read_csv(f'bar_data/{symbol}_{timeframe}.csv')


class API:
    def __init__(self):
        self.chart = None  # Changes after each callback.

    async def on_search(self, searched_string):  # Called when the user searches.
        new_data = get_bar_data(searched_string, self.chart.topbar['timeframe'].value)
        if new_data.empty:
            return
        self.chart.topbar['symbol'].set(searched_string)
        self.chart.set(new_data)

    async def on_timeframe_selection(self):  # Called when the user changes the timeframe.
        new_data = get_bar_data(self.chart.topbar['symbol'].value, self.chart.topbar['timeframe'].value)
        if new_data.empty:
            return
        self.chart.set(new_data)


async def main():
    api = API()

    chart = Chart(api=api, topbar=True, searchbox=True)
    chart.legend(True)

    chart.topbar.textbox('symbol', 'TSLA')
    chart.topbar.switcher('timeframe', api.on_timeframe_selection, '1min', '5min', '30min', default='5min')

    df = get_bar_data('TSLA', '5min')
    chart.set(df)

    await chart.show_async(block=True)


if __name__ == '__main__':
    asyncio.run(main())
