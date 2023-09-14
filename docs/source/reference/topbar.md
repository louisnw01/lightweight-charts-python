# `TopBar`


````{py:class} TopBar
The `TopBar` class represents the top bar shown on the chart:

![topbar](https://i.imgur.com/Qu2FW9Y.png)

This object is accessed from the `topbar` attribute of the chart object (`chart.topbar.<method>`).

Switchers, text boxes and buttons can be added to the top bar, and their instances can be accessed through the `topbar` dictionary. For example:

```python
chart.topbar.textbox('symbol', 'AAPL') # Declares a textbox displaying 'AAPL'.
print(chart.topbar['symbol'].value) # Prints the value within 'symbol' -> 'AAPL'

chart.topbar['symbol'].set('MSFT') # Sets the 'symbol' textbox to 'MSFT'
print(chart.topbar['symbol'].value) # Prints the value again -> 'MSFT'
```

Topbar widgets share common parameters:
* `name`: The name of the widget which can be used to access it from the `topbar` dictionary.
* `align`: The alignment of the widget (either `'left'` or `'right'` which determines which side of the topbar the widget will be placed upon.

___



```{py:method} switcher(name: str, options: tuple: default: str, align: ALIGN, func: callable)

* `options`: The options for each switcher item.
* `default`: The initial switcher option set.

```
___



```{py:method} menu(name: str, options: tuple: default: str, separator: bool, align: ALIGN, func: callable)

* `options`: The options for each menu item.
* `default`: The initial menu option set.
* `separator`: places a separator line to the right of the menu.

```
___



```{py:method} textbox(name: str, initial_text: str, align: ALIGN)

* `initial_text`: The text to show within the text box.

```
___



```{py:method} button(name: str, button_text: str, separator: bool, align: ALIGN, func: callable)

* `button_text`: Text to show within the button.
* `separator`: places a separator line to the right of the button.
* `func`: The event handler which will be executed upon a button click.

```

````