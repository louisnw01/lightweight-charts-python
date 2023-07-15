from pathlib import Path

import pandas as pd
import panel as pn
from lightweight_charts.widgets import PanelChart

ROOT = Path(__file__).parent

def create_chart():
    
    chart = PanelChart(sizing_mode="stretch_both")
    
    df = pd.read_csv(ROOT/'ohlcv.csv')

    chart.layout(background_color='#090008', text_color='#FFFFFF', font_size=16, font_family='Helvetica')

    chart.candle_style(up_color='#00ff55', down_color='#ed4807', border_up_color='#FFFFFF', border_down_color='#FFFFFF',
                       wick_up_color='#FFFFFF', wick_down_color='#FFFFFF')

    chart.volume_config(up_color='#00ff55', down_color='#ed4807')

    chart.watermark('1D', color='rgba(180, 180, 240, 0.7)')

    chart.crosshair(mode='normal', vert_color='#FFFFFF', vert_style='dotted', horz_color='#FFFFFF', horz_style='dotted')

    chart.legend(visible=True, font_size=14)

    chart.set(df)

    return chart

if pn.state.served:
    pn.extension(sizing_mode="stretch_width")
    
    chart = create_chart()
    
    pn.template.FastListTemplate(
        site="LightWeight Charts Python + Panel", title="Styling", main=[chart], theme="dark", theme_toggle=False
    ).servable()
