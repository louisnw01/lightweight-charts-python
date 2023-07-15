import asyncio
from pathlib import Path

import pandas as pd
import panel as pn
from lightweight_charts.widgets import PanelChart

ROOT = Path(__file__).parent

@pn.cache
def get_bar_data(symbol, timeframe):
    if symbol not in ('AAPL', 'GOOGL', 'TSLA'):
        print(f'No data for "{symbol}"')
        return pd.DataFrame()
    return pd.read_csv(ROOT/f'bar_data/{symbol}_{timeframe}.csv')


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


def create_chart():
    api = API()

    chart = PanelChart(api=api, topbar=True, searchbox=True, sizing_mode="stretch_both")
    chart.legend(True)

    chart.topbar.textbox('symbol', 'TSLA')
    chart.topbar.switcher('timeframe', api.on_timeframe_selection, '1min', '5min', '30min', default='5min')

    df = get_bar_data('TSLA', '5min')
    # Columns: | time | open | high | low | close | volume (if volume is enabled) |
    df = get_bar_data('TSLA', '5min')
    chart.set(df)
    return chart

if pn.state.served:
    pn.extension(sizing_mode="stretch_width")
    
    chart = create_chart()
    
    pn.template.FastListTemplate(
        site="LightWeight Charts Python + Panel", title="Setting Data", main=[chart], theme="dark", theme_toggle=False
    ).servable()
