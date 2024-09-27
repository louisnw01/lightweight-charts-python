import asyncio
from typing import Dict, Literal

from .util import jbool, Pane


ALIGN = Literal['left', 'right']


class Widget(Pane):
    def __init__(self, topbar, value, func: callable = None, right_click_func: callable = None, font_size: str = '16px', convert_boolean=False):
        super().__init__(topbar.win)
        self.value = value

        if func and not callable(func):
            raise TypeError(f"The provided 'func' is not callable: {func}")
        
        # Left-click wrapper
        def wrapper(v):
            if convert_boolean:
                self.value = False if v == 'false' else True
            else:
                self.value = v
            if func:
                func(topbar._chart)
        
        # Right-click wrapper
        def right_click_wrapper(v):
            if right_click_func:
                right_click_func(topbar._chart)
        
        async def async_wrapper(v):
            self.value = v
            await func(topbar._chart)
        
        self.win.handlers[self.id] = async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
        if right_click_func:
            self.win.handlers[self.id + '_right'] = right_click_wrapper


class TextWidget(Widget):
    def __init__(self, topbar, initial_text, align, func):
        super().__init__(topbar, value=initial_text, func=func)
        callback_name = f'"{self.id}"' if func else ''
        self.run_script(f'{self.id} = {topbar.id}.makeTextBoxWidget("{initial_text}", "{align}", {callback_name})')

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
        self.value = option


class MenuWidget(Widget):
    def __init__(self, topbar, options, default, separator, align, func):
        super().__init__(topbar, value=default, func=func)
        self.options = list(options)
        self.run_script(f'''
        {self.id} = {topbar.id}.makeMenu({list(options)}, "{default}", {jbool(separator)}, "{self.id}", "{align}")
        ''')

    # TODO this will probably need to be fixed
    def set(self, option):
        if option not in self.options:
            raise ValueError(f"Option {option} not in menu options ({self.options})")
        self.value = option
        self.run_script(f'''
            {self.id}.updateMenu("{option}")
        ''')
        self.win.handlers[self.id](option)

    def update_items(self, *items: str):
        self.options = list(items)
        self.run_script(f'{self.id}.updateMenuItems({self.options})')


class ButtonWidget(Widget):
    def __init__(self, topbar, button, separator, align, toggle, disabled: bool = False, func=None, right_click_func=None, font_size: str = '16px'):
        super().__init__(topbar, value=False, func=func, convert_boolean=toggle)
        self.disabled = disabled
        self.font_size = font_size
        self.right_click_func = right_click_func

        self.run_script(
            f'{self.id} = {topbar.id}.makeButton("{button}", "{self.id}", {jbool(separator)}, true, "{align}", {jbool(toggle)})'
        )
        self.update_disabled()
        if right_click_func:
            self.enable_right_click()

    def set(self, string):
        self.run_script(f'{self.id}.elem.innerText = "{string}"')

    def update_disabled(self):
        """Update the button's disabled state and text opacity in the UI."""
        unique_button_elem = f'buttonElem_{self.id.replace(".", "_")}'  # Unique reference for each button
        self.run_script(f'''
            const {unique_button_elem} = {self.id}.elem;
            {unique_button_elem}.disabled = {jbool(self.disabled)};
            {unique_button_elem}.style.opacity = {0.5 if self.disabled else 1};
            {unique_button_elem}.style.fontSize = "{self.font_size}";
        ''')
    def enable_right_click(self):
        """Enable right-click functionality for the button."""
        unique_button_elem = f'buttonElem_{self.id.replace(".", "_")}_right'  # Unique reference for each button

        self.run_script(f'''
            const {unique_button_elem} = {self.id}.elem;
            {unique_button_elem}.addEventListener('contextmenu', (event) => {{
                event.preventDefault();  // Prevent the default right-click context menu
                if ({unique_button_elem}.disabled) return;  // Ignore right-click if button is disabled
                window.callbackFunction(`right_click_{self.id}_~_` + event.button);
            }});
        ''')

        # Check if right_click_func is callable before assigning
        if callable(self.right_click_func):
            self.win.handlers[f'right_click_{self.id}'] = self.right_click_func

    def disable(self):
        """Disable the button."""
        self.disabled = True
        self.update_disabled()

    def enable(self):
        """Enable the button."""
        self.disabled = False
        self.update_disabled()


class TopBar(Pane):
    def __init__(self, chart):
        super().__init__(chart.win)
        self._chart = chart
        self._widgets: Dict[str, Widget] = {}
        self._created = False

    def _create(self):
        if self._created:
            return
        self._created = True
        self.run_script(f'{self.id} = {self._chart.id}.createTopBar()')

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
                align: ALIGN = 'left', func: callable = None):
        self._create()
        self._widgets[name] = TextWidget(self, initial_text, align, func)

    def button(self, name, button_text: str, separator: bool = True,
           align: ALIGN = 'left', toggle: bool = False, disabled: bool = False, 
           font_size: str = '16px', func: callable = None, right_click_func: callable = None):
        self._create()
        self._widgets[name] = ButtonWidget(self, button_text, separator, align, toggle, disabled, func, right_click_func, font_size)
