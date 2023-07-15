from asyncio import sleep
from pathlib import Path

import pandas as pd
import panel as pn
from lightweight_charts.widgets import PanelChart

ROOT = Path(__file__).parent
df = pd.read_csv(ROOT/'ohlcv.csv')

def calculate_sma(data: pd.DataFrame, period: int = 50):
    def avg(d: pd.DataFrame):
        return d['close'].mean()
    result = []
    for i in range(period - 1, len(data)):
        val = avg(data.iloc[i - period + 1:i])
        result.append({'time': data.iloc[i]['date'], 'value': val})
    return pd.DataFrame(result)

def create_chart():
    chart = PanelChart(sizing_mode="stretch_both", volume_enabled=False)
    chart.set(df)

    line = chart.create_line()
    sma_data = calculate_sma(df)
    line.set(sma_data)

    return chart

if pn.state.served:
    pn.extension(sizing_mode="stretch_width")
    
    chart = create_chart()
    
    pn.template.FastListTemplate(
        site="LightWeight Charts Python + Panel", title="SMA Line Indicator", main=[chart], theme="dark", theme_toggle=False
    ).servable()
