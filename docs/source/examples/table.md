# Table

```python
import pandas as pd
from lightweight_charts import Chart

def on_row_click(row):
    row['PL'] = round(row['PL']+1, 2)
    row.background_color('PL', 'green' if row['PL'] > 0 else 'red')

    table.footer[1] = row['Ticker']

if __name__ == '__main__':
    chart = Chart(width=1000, inner_width=0.7, inner_height=1)
    subchart = chart.create_subchart(width=0.3, height=0.5)
    df = pd.read_csv('ohlcv.csv')
    chart.set(df)
    subchart.set(df)

    table = chart.create_table(width=0.3, height=0.2,
                  headings=('Ticker', 'Quantity', 'Status', '%', 'PL'),
                  widths=(0.2, 0.1, 0.2, 0.2, 0.3),
                  alignments=('center', 'center', 'right', 'right', 'right'),
                  position='left', func=on_row_click)

    table.format('PL', f'£ {table.VALUE}')
    table.format('%', f'{table.VALUE} %')

    table.new_row('SPY', 3, 'Submitted', 0, 0)
    table.new_row('AMD', 1, 'Filled', 25.5, 105.24)
    table.new_row('NVDA', 2, 'Filled', -0.5, -8.24)

    table.footer(2)
    table.footer[0] = 'Selected:'

    chart.show(block=True)

```
