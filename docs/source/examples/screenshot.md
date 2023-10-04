# Screenshot & Save


```python
import pandas as pd
from lightweight_charts import Chart


if __name__ == '__main__':
    chart = Chart()
    df = pd.read_csv('ohlcv.csv')
    chart.set(df)
    chart.show()
    
    img = chart.screenshot()
    with open('screenshot.png', 'wb') as f:
        f.write(img)
```

```{important}
The `screenshot` command can only be executed after the chart window is open. Therefore, either `block` must equal `False`, the screenshot should be triggered with a callback, or `async_show` should be used. 
```

```{important}
This example can only be used with the standard `Chart` object.
```

