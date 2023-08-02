import random
from typing import Union

from lightweight_charts.util import _js_bool


class Footer:
    def __init__(self, table):
        self._table = table
        self._chart = table._chart

    def __setitem__(self, key, value): self._chart.run_script(f'{self._table.id}.footer[{key}].innerText = "{value}"')

    def __call__(self, number_of_text_boxes): self._chart.run_script(f'{self._table.id}.makeFooter({number_of_text_boxes})')


class Row(dict):
    def __init__(self, table, id, items):
        super().__init__()
        self._table = table
        self._chart = table._chart
        self.id = id
        self.meta = {}
        self._table._chart.run_script(f'''{self._table.id}.newRow({list(items.values())}, '{self.id}')''')
        for key, val in items.items():
            self[key] = val

    def __setitem__(self, column, value):
        str_value = str(value)
        if column in self._table._formatters:
            str_value = self._table._formatters[column].replace(self._table.VALUE, str_value)
        self._chart.run_script(f'''{self._table.id}.updateCell('{self.id}', '{column}', '{str_value}')''')

        return super().__setitem__(column, value)

    def background_color(self, column, color):
        self._chart.run_script(f"{self._table.id}.rows[{self.id}]['{column}'].style.backgroundColor = '{color}'")

    def delete(self):
        self._chart.run_script(f"{self._table.id}.deleteRow('{self.id}')")
        self._table.pop(self.id)

class Table(dict):
    VALUE = 'CELL__~__VALUE__~__PLACEHOLDER'

    def __init__(self, chart, width, height, headings, widths=None, alignments=None, position='left', draggable=False, method=None):
        super().__init__()
        self._chart = chart
        self.headings = headings
        self._formatters = {}
        self.is_shown = True

        self.id = self._chart._rand.generate()
        self._chart.run_script(f'''
        {self.id} = new Table({width}, {height}, {list(headings)}, {list(widths)}, {list(alignments)}, '{position}', {_js_bool(draggable)}, '{method}', {chart.id})
        ''')
        self.footer = Footer(self)

    def new_row(self, *values, id=None) -> Row:
        row_id = random.randint(0, 99_999_999) if not id else id
        self[row_id] = Row(self, row_id, {heading: item for heading, item in zip(self.headings, values)})
        return self[row_id]

    def clear(self): self._chart.run_script(f"{self.id}.clearRows()"), super().clear()

    def get(self, __key: Union[int, str]) -> Row: return super().get(int(__key))

    def __getitem__(self, item): return super().__getitem__(int(item))

    def format(self, column: str, format_str: str): self._formatters[column] = format_str

    def visible(self, visible: bool):
        self.is_shown = visible
        self._chart.run_script(f"""
        {self.id}.container.style.display = '{'block' if visible else 'none'}'
        {self.id}.container.{'add' if visible else 'remove'}EventListener('mousedown', {self.id}.onMouseDown)
        """)
