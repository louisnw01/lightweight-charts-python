import asyncio
import pandas as pd

from lightweight_charts import ChartAsync


def get_bar_data(symbol, timeframe):
    return pd.read_csv(f'bar_data/{symbol}_{timeframe}.csv')


class API:
    def __init__(self):
        self.chart = None  # Changes after each callback.
        self.symbol = 'TSLA'
        self.timeframe = '5min'

    async def on_search(self, searched_string):  # Called when the user searches.
        self.symbol = searched_string
        new_data = await self.get_data()
        if new_data.empty:
            return
        self.chart.set(new_data)
        self.chart.corner_text(searched_string)

    async def on_timeframe_selection(self, timeframe):  # Called when the user changes the timeframe.
        self.timeframe = timeframe
        new_data = await self.get_data()
        if new_data.empty:
            return
        self.chart.set(new_data)

    async def get_data(self):
        if self.symbol not in ('AAPL', 'GOOGL', 'TSLA'):
            print(f'No data for "{self.symbol}"')
            return pd.DataFrame()
        data = get_bar_data(self.symbol, self.timeframe)
        return data


async def main():
    api = API()

    chart = ChartAsync(api=api, debug=True)
    chart.legend(True)

    chart.create_switcher(api.on_timeframe_selection, '1min', '5min', '30min', default='5min')
    chart.corner_text(api.symbol)

    df = get_bar_data(api.symbol, api.timeframe)
    chart.set(df)

    await chart.show(block=True)


if __name__ == '__main__':
    asyncio.run(main())
