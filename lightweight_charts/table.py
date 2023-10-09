import random
from typing import Union

from .util import jbool, Pane, NUM


class Section(Pane):
    def __init__(self, table, section_type):
        super().__init__(table.win)
        self._table = table
        self.type = section_type

    def __call__(self, number_of_text_boxes: int, func: callable = None):
        if func:
            self.win.handlers[self.id] = lambda boxId: func(self._table, int(boxId))
        self.run_script(f'''
        {self._table.id}.makeSection("{self.id}", "{self.type}", {number_of_text_boxes}, {"true" if func else ""})
        ''')

    def __setitem__(self, key, value):
        self.run_script(f'{self._table.id}.{self.type}[{key}].innerText = "{value}"')


class Row(dict):
    def __init__(self, table, id, items):
        super().__init__()
        self.run_script = table.run_script
        self._table = table
        self.id = id
        self.meta = {}
        self.run_script(f'{self._table.id}.newRow("{self.id}", {jbool(table.return_clicked_cells)})')
        for key, val in items.items():
            self[key] = val

    def __setitem__(self, column, value):
        if isinstance(column, tuple):
            return [self.__setitem__(col, val) for col, val in zip(column, value)]
        original_value = value
        if column in self._table._formatters:
            value = self._table._formatters[column].replace(self._table.VALUE, str(value))
        self.run_script(f'{self._table.id}.updateCell("{self.id}", "{column}", "{value}")')
        return super().__setitem__(column, original_value)

    def background_color(self, column, color): self._style('backgroundColor', column, color)

    def text_color(self, column, color): self._style('textColor', column, color)

    def _style(self, style, column, arg):
        self.run_script(f"{self._table.id}.rows[{self.id}]['{column}'].style.{style} = '{arg}'")

    def delete(self):
        self.run_script(f"{self._table.id}.deleteRow('{self.id}')")
        self._table.pop(self.id)


class Table(Pane, dict):
    VALUE = 'CELL__~__VALUE__~__PLACEHOLDER'

    def __init__(
            self, window, width: NUM, height: NUM, headings: tuple, widths: tuple = None,
            alignments: tuple = None, position='left', draggable: bool = False,
            background_color: str = '#121417', border_color: str = 'rgb(70, 70, 70)',
            border_width: int = 1, heading_text_colors: tuple = None,
            heading_background_colors: tuple = None, return_clicked_cells: bool = False,
            func: callable = None
    ):
        dict.__init__(self)
        Pane.__init__(self, window)
        self._formatters = {}
        self.headings = headings
        self.is_shown = True
        if return_clicked_cells:
            self.win.handlers[self.id] = lambda rId, cId: func(self[rId], cId)
        else:
            self.win.handlers[self.id] = lambda rId: func(self[rId])
        self.return_clicked_cells = return_clicked_cells

        headings = list(headings)
        widths = list(widths) if widths else []
        alignments = list(alignments) if alignments else []
        heading_text_colors = list(heading_text_colors) if heading_text_colors else []
        heading_background_colors = list(heading_background_colors) if heading_background_colors else []

        self.run_script(f'''
        {self.id} = new Table(
        {width}, {height}, {headings}, {widths}, {alignments}, '{position}', {jbool(draggable)},
        '{background_color}', '{border_color}', {border_width}, {heading_text_colors},
        {heading_background_colors} 
        )''')
        self.run_script(f'{self.id}.callbackName = "{self.id}"') if func else None
        self.footer = Section(self, 'footer')
        self.header = Section(self, 'header')

    def new_row(self, *values, id=None) -> Row:
        row_id = random.randint(0, 99_999_999) if not id else id
        self[row_id] = Row(self, row_id, {heading: item for heading, item in zip(self.headings, values)})
        return self[row_id]

    def clear(self): self.run_script(f"{self.id}.clearRows()"), super().clear()

    def get(self, __key: Union[int, str]) -> Row: return super().get(int(__key))

    def __getitem__(self, item): return super().__getitem__(int(item))

    def format(self, column: str, format_str: str): self._formatters[column] = format_str

    def resize(self, width: NUM, height: NUM): self.run_script(f'{self.id}.reSize({width}, {height})')

    def visible(self, visible: bool):
        self.is_shown = visible
        self.run_script(f"""
        {self.id}.container.style.display = '{'block' if visible else 'none'}'
        {self.id}.container.{'add' if visible else 'remove'}EventListener('mousedown', {self.id}.onMouseDown)
        """)
