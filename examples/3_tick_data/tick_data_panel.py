from asyncio import sleep
from pathlib import Path
from asyncio import sleep

import pandas as pd
import panel as pn
from lightweight_charts.widgets import PanelChart

ROOT = Path(__file__).parent
df1 = pd.read_csv(ROOT/'ohlc.csv')
df2 = pd.read_csv(ROOT/'ticks.csv')

def create_chart():
    chart = PanelChart(sizing_mode="stretch_both", volume_enabled=False)
    chart.set(df1)
    return chart

async def update_chart():
    for i, tick in df2.iterrows():
        chart.update_from_tick(tick)

        await sleep(0.03)

if pn.state.served:
    pn.extension(sizing_mode="stretch_width")
    
    chart = create_chart()
    pn.state.onload(update_chart)
    
    pn.template.FastListTemplate(
        site="LightWeight Charts Python + Panel", title="Live Tick Data", main=[chart], theme="dark", theme_toggle=False
    ).servable()



    
