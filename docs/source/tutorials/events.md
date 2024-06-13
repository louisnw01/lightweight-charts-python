# Topbar & Events

This section gives an overview of how events are handled across the library.

## How to use events


Take a look at this minimal example, which uses the [`search`](#AbstractChart.Events) event:

```python
from lightweight_charts import Chart


def on_search(chart, string):
    print(f'Search Text: "{string}" | Chart/SubChart ID: "{chart.id}"')
    
    
if __name__ == '__main__':
    chart = Chart()
    
    # Subscribe the function above to search event
    chart.events.search += on_search  
    
    chart.show(block=True)

```
Upon searching in a pane, the expected output would be akin to:
```
Search Text: "AAPL" | Chart/SubChart ID: "window.blyjagcr"
```
The ID shown above will change depending upon which pane was used to search, allowing for access to the object in question.

```{important}
* When using `show` rather than `show_async`, block should be set to `True` (`chart.show(block=True)`).
* Event callables can be either coroutines, methods, or functions.
```

___

## Topbar events


Events can also be emitted from the topbar:

```python
from lightweight_charts import Chart

def on_button_press(chart):
    new_button_value = 'On' if chart.topbar['my_button'].value == 'Off' else 'Off'
    chart.topbar['my_button'].set(new_button_value)
    print(f'Turned something {new_button_value.lower()}.')
    
    
if __name__ == '__main__':
    chart = Chart()
    chart.topbar.button('my_button', 'Off', func=on_button_press)
    chart.show(block=True)

```
In this example, we are passing `on_button_press` to the `func` parameter.

When the button is pressed, the function will be emitted the `chart` object as with the previous example, allowing access to the topbar dictionary.


The `switcher` is typically used for timeframe selection:

```python
from lightweight_charts import Chart

def on_timeframe_selection(chart):
    print(f'Getting data with a {chart.topbar["my_switcher"].value} timeframe.')
    
    
if __name__ == '__main__':
    chart = Chart()
    chart.topbar.switcher(
        name='my_switcher',
        options=('1min', '5min', '30min'),
        default='5min',
        func=on_timeframe_selection)
    chart.show(block=True)
```
___

## Async clock

There are many use cases where we will need to run our own code whilst the GUI loop continues to listen for events. Let's demonstrate this by using the `textbox` widget to display a clock:

```python
import asyncio
from datetime import datetime
from lightweight_charts import Chart


async def update_clock(chart):
    while chart.is_alive:
        await asyncio.sleep(1-(datetime.now().microsecond/1_000_000))
        chart.topbar['clock'].set(datetime.now().strftime('%H:%M:%S'))


async def main():
    chart = Chart()
    chart.topbar.textbox('clock')
    await asyncio.gather(chart.show_async(), update_clock(chart))


if __name__ == '__main__':
    asyncio.run(main())
```

This is how the library is intended to be used with live data (option #2 [described here]()). 
___

## Live data, topbar & events


Now we can create an asyncio program which updates chart data whilst allowing the GUI loop to continue processing events, based the [Live data](live_chart.md) example:

```python
import asyncio
import pandas as pd
from lightweight_charts import Chart


async def data_loop(chart):
    ticks = pd.read_csv('ticks.csv')
    
    for i, tick in ticks.iterrows():
        if not chart.is_alive:
            return
        chart.update_from_tick(ticks.iloc[i])
        await asyncio.sleep(0.03)
        
        
def on_new_bar(chart):
    print('New bar event!')
    
    
def on_timeframe_selection(chart):
    print(f'Selected timeframe of {chart.topbar["timeframe"].value}')


async def main():
    chart = Chart()
    chart.events.new_bar += on_new_bar
    
    chart.topbar.switcher('timeframe', ('1min', '5min'), func=on_timeframe_selection)
    
    df = pd.read_csv('ohlc.csv')
    
    chart.set(df)
    await asyncio.gather(chart.show_async(), data_loop(chart))
    

if __name__ == '__main__':
    asyncio.run(main())

```

