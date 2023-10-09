# `Table`

`````{py:class} Table(width: NUM, height: NUM, headings: Tuple[str], widths: Tuple[float], alignments: Tuple[str], position: FLOAT, draggable: bool, return_clicked_cells: bool, func: callable)

Tables are panes that can be used to gain further functionality from charts. They are intended to be used for watchlists, order management, or position management. It should be accessed from the `create_table` common method.

The `Table` and `Row` objects act as dictionaries, and can be manipulated as such.

`width`/`height`
: Either given as a percentage (a `float` between 0 and 1) or as an integer representing pixel size.

`widths`
: Given as a `float` between 0 and 1.

`position`
: Used as you would with [`create_subchart`](#AbstractChart.create_subchart), representing how the table will float within the window.

`draggable`
: If `True`, then the window can be dragged to any position within the window.

`return_clicked_cells`
: If `True`, an additional parameter will be emitted to the `func` given, containing the heading name of the clicked cell.

`func`
: If given, this will be called when a row is clicked, returning the `Row` object in question.
___



````{py:method} new_row(*values, id: int) -> Row

Creates a new row within the table, and returns a `Row` object.

if `id` is passed it should be unique to all other rows. Otherwise, the `id` will be randomly generated.

Rows can be passed a string (header) item or a tuple to set multiple headings:

```python
row['Symbol'] = 'AAPL'
row['Symbol', 'Action'] = 'AAPL', 'BUY'
```

````
___



```{py:method} clear()

Clears and deletes all table rows.
```
___



````{py:method} format(column: str, format_str: str)

Sets the format to be used for the given column. `Table.VALUE` should be used as a placeholder for the cell value. For example:

```python
table.format('Daily %', f'{table.VALUE} %')
table.format('PL', f'$ {table.VALUE}')
```

````
___



```{py:method} visible(visible: bool)

Sets the visibility of the Table.

```
`````
___



````{py:class} Row()

```{py:method} background_color(column: str, color: COLOR)

Sets the background color of the row cell.
```
___



```{py:method} text_color(column: str, color: COLOR)

Sets the foreground color of the row cell.
```
___



```{py:method} delete()

Deletes the row.
```
````
___


````{py:class} Footer

```{tip}
All of these methods can be applied to the `header` parameter.
```

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

When calling footer, the `func` parameter can also be used to convert each textbox into a button:

```python
def on_footer_click(table, box_index):
    print(f'Box number {box_index+1} was pressed.')

table.footer(3, func=on_footer_click)
```

````








