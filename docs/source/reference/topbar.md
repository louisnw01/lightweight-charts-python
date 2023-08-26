# `TopBar`


````{py:class} TopBar
The `TopBar` class represents the top bar shown on the chart:

![topbar](https://i.imgur.com/Qu2FW9Y.png)

This object is accessed from the `topbar` attribute of the chart object (`chart.topbar.<method>`).

Switchers, text boxes and buttons can be added to the top bar, and their instances can be accessed through the `topbar` dictionary. For example:

```python
chart.topbar.textbox('symbol', 'AAPL') # Declares a textbox displaying 'AAPL'.
print(chart.topbar['symbol'].value) # Prints the value within ('AAPL')

chart.topbar['symbol'].set('MSFT') # Sets the 'symbol' textbox to 'MSFT'
print(chart.topbar['symbol'].value) # Prints the value again ('MSFT')
```
___



```{py:method} switcher(name: str, options: tuple: default: str, func: callable)

* `name`: the name of the switcher which can be used to access it from the `topbar` dictionary.
* `options`: The options for each switcher item.
* `default`: The initial switcher option set.

```
___



```{py:method} textbox(name: str, initial_text: str)

* `name`: the name of the text box which can be used to access it from the `topbar` dictionary.
* `initial_text`: The text to show within the text box.

```
___



```{py:method} button(name: str, button_text: str, separator: bool, func: callable)

* `name`: the name of the text box to access it from the `topbar` dictionary.
* `button_text`: Text to show within the button.
* `separator`: places a separator line to the right of the button.
* `func`: The event handler which will be executed upon a button click.

```

````