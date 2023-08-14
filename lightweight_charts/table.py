import random
from typing import Union

from .util import jbool


class Footer:
    def __init__(self, table): self._table = table

    def __setitem__(self, key, value): self._table._run_script(f'{self._table.id}.footer[{key}].innerText = "{value}"')

    def __call__(self, number_of_text_boxes): self._table._run_script(f'{self._table.id}.makeFooter({number_of_text_boxes})')


class Row(dict):
    def __init__(self, table, id, items):
        super().__init__()
        self._table = table
        self._run_script = table._run_script
        self.id = id
        self.meta = {}
        self._run_script(f'''{self._table.id}.newRow({list(items.values())}, '{self.id}')''')
        for key, val in items.items():
            self[key] = val

    def __setitem__(self, column, value):
        if isinstance(column, tuple):
            return [self.__setitem__(col, val) for col, val in zip(column, value)]
        original_value = value
        if column in self._table._formatters:
            value = self._table._formatters[column].replace(self._table.VALUE, str(value))
        self._run_script(f'{self._table.id}.updateCell("{self.id}", "{column}", "{value}")')

        return super().__setitem__(column, original_value)

    def background_color(self, column, color): self._style('backgroundColor', column, color)

    def text_color(self, column, color): self._style('textColor', column, color)

    def _style(self, style, column, arg):
        self._run_script(f"{self._table.id}.rows[{self.id}]['{column}'].style.{style} = '{arg}'")

    def delete(self):
        self._run_script(f"{self._table.id}.deleteRow('{self.id}')")
        self._table.pop(self.id)

class Table(dict):
    VALUE = 'CELL__~__VALUE__~__PLACEHOLDER'

    def __init__(self, chart, width, height, headings, widths=None, alignments=None, position='left', draggable=False, func=None):
        super().__init__()
        self._run_script = chart.run_script
        self._chart = chart
        self.headings = headings
        self._formatters = {}
        self.is_shown = True

        self.id = chart._rand.generate()
        chart._handlers[self.id] = lambda rId: func(self[rId])
        self._run_script(f'''
        {self.id} = new Table({width}, {height}, {list(headings)}, {list(widths) if widths else []}, {list(alignments) if alignments else []},
                            '{position}', {jbool(draggable)}, {chart.id})
        ''')
        self._run_script(f'{self.id}.callbackName = "{self.id}"') if func else None
        self.footer = Footer(self)

    def new_row(self, *values, id=None) -> Row:
        row_id = random.randint(0, 99_999_999) if not id else id
        self[row_id] = Row(self, row_id, {heading: item for heading, item in zip(self.headings, values)})
        return self[row_id]

    def clear(self): self._run_script(f"{self.id}.clearRows()"), super().clear()

    def get(self, __key: Union[int, str]) -> Row: return super().get(int(__key))

    def __getitem__(self, item): return super().__getitem__(int(item))

    def format(self, column: str, format_str: str): self._formatters[column] = format_str

    def visible(self, visible: bool):
        self.is_shown = visible
        self._run_script(f"""
        {self.id}.container.style.display = '{'block' if visible else 'none'}'
        {self.id}.container.{'add' if visible else 'remove'}EventListener('mousedown', {self.id}.onMouseDown)
        """)
