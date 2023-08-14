# Table
`width: int/float` | `height: int/float` | `headings: tuple[str]` | `widths: tuple[float]` | `alignments: tuple[str]` | `position: 'left'/'right'/'top'/'bottom'` | `draggable: bool` | `func: callable` 

Tables are panes that can be used to gain further functionality from charts. They are intended to be used for watchlists, order management, or position management. It should be accessed from the `create_table` common method.

The `Table` and `Row` objects act as dictionaries, and can be manipulated as such.

`width`/`height`: Either given as a percentage (a `float` between 0 and 1) or as an integer representing pixel size.

`widths`: Given as a `float` between 0 and 1.

`position`: Used as you would when creating a `SubChart`, representing how the table will float within the window.

`draggable`: If `True`, then the window can be dragged to any position within the window.

`func`: If given this will be called when a row is clicked, returning the `Row` object in question.
___

## `new_row` (Row)
`*values` | `id: int` | `-> Row`

Creates a new row within the table, and returns a `Row` object.

if `id` is passed it should be unique to all other rows. Otherwise, the `id` will be randomly generated.

Rows can be passed a string (header) item or a tuple to set multiple headings:

```python
row['Symbol'] = 'AAPL'
row['Symbol', 'Action'] = 'AAPL', 'BUY'
```

### `background_color`
`column: str` | `color: str`

Sets the background color of the row cell.

### `text_color`
`column: str` | `color: str`

Sets the foreground color of the row cell.

### `delete`
Deletes the row.
___

## `clear`
Clears and deletes all table rows.
___

## `format`
`column: str` | `format_str: str`

Sets the format to be used for the given column. `table.VALUE` should be used as a placeholder for the cell value. For example:

```python
table.format('Daily %', f'{table.VALUE} %')
table.format('PL', f'$ {table.VALUE}')
```
___

## `visible`
`visible: bool`

Sets the visibility of the Table.
___

## Footer
Tables can also have a footer containing a number of text boxes. To initialize this, call the `footer` attribute with the number of textboxes to be used:

```python
table.footer(3)  # Footer will be displayed, with 3 text boxes.
```
To edit the textboxes, treat `footer` as a list:

```python
table.footer[0] = 'Text Box 1'
table.footer[1] = 'Text Box 2'
table.footer[2] = 'Text Box 3'
```
___

## Example:

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

