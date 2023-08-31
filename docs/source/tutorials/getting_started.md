# Getting Started

## Installation

To install the library, use pip:

```text
pip install lightweight-charts
```

Pywebview's installation can differ depending on OS. Please refer to their [documentation](https://pywebview.flowrl.com/guide/installation.html#installation).

When using Docker or WSL, you may need to update your language tags; see [this](https://github.com/louisnw01/lightweight-charts-python/issues/63#issuecomment-1670473651) issue.

___

## A simple static chart

```python
import pandas as pd
from lightweight_charts import Chart
```

Download this
[`ohlcv.csv`](../../../examples/1_setting_data/ohlcv.csv)
file for this tutorial.

In this example, we are reading a csv file using pandas:
```text
           date    open    high     low   close       volume
0    2010-06-29  1.2667  1.6667  1.1693  1.5927  277519500.0
1    2010-06-30  1.6713  2.0280  1.5533  1.5887  253039500.0
2    2010-07-01  1.6627  1.7280  1.3513  1.4640  121461000.0
3    2010-07-02  1.4700  1.5500  1.2473  1.2800   75871500.0
4..
```
..which can be used as data for the `Chart` object:


```python
if __name__ == '__main__':
    chart = Chart()
    
    df = pd.read_csv('ohlcv.csv')
    chart.set(df)
    
    chart.show(block=True)
```

The `block` parameter is set to `True` in this case, as we do not want the program to exit.

```{warning}
Due to the library's use of multiprocessing, instantiations of `Chart` should be encapsulated within an   `if __name__ == '__main__'` block.
```


## Adding a line

Now lets add a moving average to the chart using the following function: 
```python
def calculate_sma(df, period: int = 50):
    return pd.DataFrame({
        'time': df['date'],
        f'SMA {period}': df['close'].rolling(window=period).mean()
    }).dropna()
```

`calculate_sma` derives the data column from `f'SMA {period}'`, which we will use as the name of our line:

```python
if __name__ == '__main__':
    chart = Chart()
    line = chart.create_line(name='SMA 50')

    df = pd.read_csv('ohlcv.csv')
    sma_df = calculate_sma(df, period=50)

    chart.set(df)
    line.set(sma_df)
    
    chart.show(block=True)
```





