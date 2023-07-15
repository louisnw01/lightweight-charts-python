from pathlib import Path

import pandas as pd
import panel as pn
from lightweight_charts.widgets import PanelChart

ROOT = Path(__file__).parent

def create_chart():
    
    chart = PanelChart(sizing_mode="stretch_both")

    # Columns: | time | open | high | low | close | volume (if volume is enabled) |
    df = pd.read_csv(ROOT/'ohlcv.csv')
    chart.set(df)
    return chart

if pn.state.served:
    pn.extension(sizing_mode="stretch_width")
    
    chart = create_chart()
    
    pn.template.FastListTemplate(
        site="LightWeight Charts Python + Panel", title="Setting Data", main=[chart], theme="dark", theme_toggle=False
    ).servable()
