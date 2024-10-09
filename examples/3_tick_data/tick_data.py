import pandas as pd
from time import sleep
from lightweight_charts_r4gn4r.lightweight_charts import Chart

if __name__ == '__main__':

    df1 = pd.read_csv('ohlc.csv')

    # Columns: time | price
    df2 = pd.read_csv('ticks.csv')

    chart = Chart()

    chart.set(df1)

    chart.show()

    for i, tick in df2.iterrows():
        chart.update_from_tick(tick)
        sleep(0.03)
