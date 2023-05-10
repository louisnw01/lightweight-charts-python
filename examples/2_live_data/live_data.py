import pandas as pd
from time import sleep
from lightweight_charts import Chart

if __name__ == '__main__':

    chart = Chart()

    df1 = pd.read_csv('ohlcv.csv')
    df2 = pd.read_csv('next_ohlcv.csv')

    chart.set(df1)

    chart.show()

    last_close = df1.iloc[-1]

    for i, series in df2.iterrows():
        chart.update(series)

        if series['close'] > 20 and last_close < 20:
            chart.marker(text='The price crossed $20!')

        last_close = series['close']
        sleep(0.1)
