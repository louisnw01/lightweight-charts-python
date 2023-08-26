import asyncio
from typing import Dict

from .util import jbool, Pane


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
    def __init__(self, topbar, initial_text):
        super().__init__(topbar, value=initial_text)
        self.run_script(f'{self.id} = {topbar.id}.makeTextBoxWidget("{initial_text}")')

    def set(self, string):
        self.value = string
        self.run_script(f'{self.id}.innerText = "{string}"')


class SwitcherWidget(Widget):
    def __init__(self, topbar, options, default, func):
        super().__init__(topbar, value=default, func=func)
        self.run_script(f'{self.id} = {topbar.id}.makeSwitcher({list(options)}, "{default}", "{self.id}")')


class ButtonWidget(Widget):
    def __init__(self, topbar, button, separator, func):
        super().__init__(topbar, value=button, func=func)
        self.run_script(f'{self.id} = {topbar.id}.makeButton("{button}", "{self.id}", {jbool(separator)})')

    def set(self, string):
        self.value = string
        self.run_script(f'{self.id}.elem.innerText = "{string}"')


class TopBar(Pane):
    def __init__(self, chart):
        super().__init__(chart.win)
        self._chart = chart
        self._widgets: Dict[str, Widget] = {}

        self.click_bg_color = '#50565E'
        self.hover_bg_color = '#3c434c'
        self.active_bg_color = 'rgba(0, 122, 255, 0.7)'
        self.active_text_color = '#ececed'
        self.text_color = '#d8d9db'
        self._created = False

    def _create(self):
        if self._created:
            return
        from lightweight_charts.abstract import JS
        self._created = True
        self.run_script(JS['callback'])
        self.run_script(f'''
        {self.id} = new TopBar( {self._chart.id}, '{self.hover_bg_color}', '{self.click_bg_color}',
                                '{self.active_bg_color}', '{self.text_color}', '{self.active_text_color}')
        ''')

    def __getitem__(self, item):
        if widget := self._widgets.get(item):
            return widget
        raise KeyError(f'Topbar widget "{item}" not found.')

    def get(self, widget_name): return self._widgets.get(widget_name)

    def switcher(self, name, options: tuple, default: str = None, func: callable = None):
        self._create()
        self._widgets[name] = SwitcherWidget(self, options, default if default else options[0], func)

    def textbox(self, name: str, initial_text: str = ''):
        self._create()
        self._widgets[name] = TextWidget(self, initial_text)

    def button(self, name, button_text: str, separator: bool = True, func: callable = None):
        self._create()
        self._widgets[name] = ButtonWidget(self, button_text, separator, func)