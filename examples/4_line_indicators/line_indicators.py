import pandas as pd
from lightweight_charts import Chart


def calculate_sma(data: pd.DataFrame, period: int = 50):
    def avg(d: pd.DataFrame):
        return d['close'].mean()
    result = []
    for i in range(period - 1, len(data)):
        val = avg(data.iloc[i - period + 1:i])
        result.append({'time': data.iloc[i]['date'], 'value': val})
    return pd.DataFrame(result)


if __name__ == '__main__':

    chart = Chart()

    df = pd.read_csv('ohlcv.csv')
    chart.set(df)

    line = chart.create_line()
    sma_data = calculate_sma(df)
    line.set(sma_data)

    chart.show(block=True)
