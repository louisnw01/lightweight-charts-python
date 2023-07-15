from asyncio import sleep
from pathlib import Path

import pandas as pd
import panel as pn
from lightweight_charts import Chart
from lightweight_charts.widgets import PanelChart

ROOT = Path(__file__).parent
df1 = pd.read_csv(ROOT/'ohlcv.csv')
df2 = pd.read_csv(ROOT/'next_ohlcv.csv')

def create_chart():
    chart = PanelChart(sizing_mode="stretch_both")
    chart.set(df1)
    return chart

async def update_chart():
    last_close = df1.iloc[-1]

    for i, series in df2.iterrows():
        chart.update(series)

        if series['close'] > 20 and last_close < 20:
            chart.marker(text='The price crossed $20!')

        last_close = series['close']
        await sleep(0.1)

if pn.state.served:
    pn.extension(sizing_mode="stretch_width")
    
    chart = create_chart()
    pn.state.onload(update_chart)
    
    pn.template.FastListTemplate(
        site="LightWeight Charts Python + Panel", title="Live Data", main=[chart], theme="dark", theme_toggle=False
    ).servable()
