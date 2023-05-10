import pandas as pd
from lightweight_charts import Chart


def on_click(bar: dict):
    print(f"Time: {bar['time']} | Close: {bar['close']}")


if __name__ == '__main__':

    chart = Chart()

    df = pd.read_csv('ohlcv.csv')
    chart.set(df)

    chart.subscribe_click(on_click)

    chart.show(block=True)
