import asyncio
from typing import Dict, Literal

from .util import jbool, Pane


ALIGN = Literal['left', 'right']


class Widget(Pane):
    def __init__(self, topbar, value, func=None):
        super().__init__(topbar.win)
        self.value = value

        def wrapper(v):
            self.value = v
            func(topbar._chart)

        async def async_wrapper(v):
            self.value = v
            await func(topbar._chart)

        self.win.handlers[self.id] = async_wrapper if asyncio.iscoroutinefunction(func) else wrapper


class TextWidget(Widget):
    def __init__(self, topbar, initial_text, align):
        super().__init__(topbar, value=initial_text)
        self.run_script(f'{self.id} = {topbar.id}.makeTextBoxWidget("{initial_text}", "{align}")')

    def set(self, string):
        self.value = string
        self.run_script(f'{self.id}.innerText = "{string}"')


class SwitcherWidget(Widget):
    def __init__(self, topbar, options, default, align, func):
        super().__init__(topbar, value=default, func=func)
        self.options = list(options)
        self.run_script(f'{self.id} = {topbar.id}.makeSwitcher({self.options}, "{default}", "{self.id}", "{align}")')

    def set(self, option):
        if option not in self.options:
            raise ValueError(f"option '{option}' does not exist within {self.options}.")
        self.run_script(f'{self.id}.onItemClicked("{option}")')


class MenuWidget(Widget):
    def __init__(self, topbar, options, default, separator, align, func):
        super().__init__(topbar, value=default, func=func)
        self.run_script(f'''
        {self.id} = {topbar.id}.makeMenu({list(options)}, "{default}", {jbool(separator)}, "{self.id}", "{align}")
        ''')


class ButtonWidget(Widget):
    def __init__(self, topbar, button, separator, align, func):
        super().__init__(topbar, value=button, func=func)
        self.run_script(
            f'{self.id} = {topbar.id}.makeButton("{button}", "{self.id}", {jbool(separator)}, true, "{align}")')

    def set(self, string):
        self.value = string
        self.run_script(f'{self.id}.elem.innerText = "{string}"')


class TopBar(Pane):
    def __init__(self, chart):
        super().__init__(chart.win)
        self._chart = chart
        self._widgets: Dict[str, Widget] = {}
        self._created = False

    def _create(self):
        if self._created:
            return
        from lightweight_charts.abstract import JS
        self._created = True
        self.run_script(JS['callback'])
        self.run_script(f'{self.id} = new TopBar({self._chart.id})')

    def __getitem__(self, item):
        if widget := self._widgets.get(item):
            return widget
        raise KeyError(f'Topbar widget "{item}" not found.')

    def get(self, widget_name):
        return self._widgets.get(widget_name)

    def switcher(self, name, options: tuple, default: str = None,
                 align: ALIGN = 'left', func: callable = None):
        self._create()
        self._widgets[name] = SwitcherWidget(self, options, default if default else options[0], align, func)

    def menu(self, name, options: tuple, default: str = None, separator: bool = True,
             align: ALIGN = 'left', func: callable = None):
        self._create()
        self._widgets[name] = MenuWidget(self, options, default if default else options[0], separator, align, func)

    def textbox(self, name: str, initial_text: str = '',
                align: ALIGN = 'left'):
        self._create()
        self._widgets[name] = TextWidget(self, initial_text, align)

    def button(self, name, button_text: str, separator: bool = True,
               align: ALIGN = 'left', func: callable = None):
        self._create()
        self._widgets[name] = ButtonWidget(self, button_text, separator, align, func)
