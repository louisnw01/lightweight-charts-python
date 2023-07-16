import pandas as pd
from lightweight_charts import Chart


def calculate_sma(data: pd.DataFrame, period: int = 50):
    def avg(d: pd.DataFrame):
        return d['close'].mean()
    result = []
    for i in range(period - 1, len(data)):
        val = avg(data.iloc[i - period + 1:i])
        result.append({'time': data.iloc[i]['date'], f'SMA {period}': val})
    return pd.DataFrame(result)


if __name__ == '__main__':

    chart = Chart(debug=True)
    chart.legend(visible=True)

    df = pd.read_csv('ohlcv.csv')
    chart.set(df)

    line = chart.create_line()
    sma_data = calculate_sma(df, period=50)
    line.set(sma_data, name='SMA 50')

    chart.show(block=True)
