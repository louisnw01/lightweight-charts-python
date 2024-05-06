import asyncio
import json
import pandas as pd

from typing import Union, Optional

from lightweight_charts.util import js_json

from .util import NUM, Pane, as_enum, LINE_STYLE, TIME


class Drawing(Pane):
    def __init__(self, chart, color, width, style, func=None):
        super().__init__(chart.win)
        self.chart = chart

    def update(self, *points):
        js_json_string = f'JSON.parse({json.dumps(points)})'
        self.run_script(f'{self.id}.updatePoints(...{js_json_string})')

    def delete(self):
        """
        Irreversibly deletes the drawing.
        """
        self.run_script(f'''
        if ({self.chart.id}.toolBox) {self.chart.id}.toolBox.delete({self.id})
        else {self.id}.detach()
        ''')

class TwoPointDrawing(Drawing):
    def __init__(
        self,
        drawing_type,
        chart,
        start_time: TIME,
        start_value: NUM,
        end_time: TIME,
        end_value: NUM,
        round: bool,
        color,
        width,
        style,
        func=None
    ):
        super().__init__(chart, color, width, style, func)


        def make_js_point(time, price):
            formatted_time = self.chart._single_datetime_format(time)
            return f'''{{
                "time": {formatted_time},
                "logical": {self.chart.id}.chart.timeScale()
                            .coordinateToLogical(
                                {self.chart.id}.chart.timeScale()
                                .timeToCoordinate({formatted_time})
                            ),
                "price": {price}
            }}'''

        self.run_script(f'''
        {self.id} = new {drawing_type}(
            {make_js_point(start_time, start_value)},
            {make_js_point(end_time, end_value)},
            {{
                lineColor: '{color}',
                lineStyle: {as_enum(style, LINE_STYLE)},
                width: {width},
            }}
        )
        {chart.id}.series.attachPrimitive({self.id})
        ''')


class HorizontalLine(Drawing):
    def __init__(self, chart, price, color, width, style, text, axis_label_visible, func):
        super().__init__(chart, color, width, style, func)
        self.price = price
        self.run_script(f'''

        {self.id} = new HorizontalLine(
            {{price: {price}}},
            {{
                lineColor: '{color}',
                lineStyle: {as_enum(style, LINE_STYLE)},
            }},
            callbackName={f"'{self.id}'" if func else 'null'}
        )
        {chart.id}.series.attachPrimitive({self.id})
        ''')
        if not func:
            return

        def wrapper(p):
            self.price = float(p)
            func(chart, self)

        async def wrapper_async(p):
            self.price = float(p)
            await func(chart, self)

        self.win.handlers[self.id] = wrapper_async if asyncio.iscoroutinefunction(func) else wrapper
        self.run_script(f'{chart.id}.toolBox?.addNewDrawing({self.id})')

    def update(self, price: float):
        """
        Moves the horizontal line to the given price.
        """
        self.run_script(f'{self.id}.updatePoints({{price: {price}}})')
        # self.run_script(f'{self.id}.updatePrice({price})')
        self.price = price

    def label(self, text: str): # TODO
        self.run_script(f'{self.id}.updateLabel("{text}")')



class VerticalLine(Drawing):
    def __init__(self, chart, time, color, width, style, text, axis_label_visible, func):
        super().__init__(chart, color, width, style, func)
        self.time = time
        self.run_script(f'''

        {self.id} = new HorizontalLine(
            {{time: {time}}},
            {{
                lineColor: '{color}',
                lineStyle: {as_enum(style, LINE_STYLE)},
            }},
            callbackName={f"'{self.id}'" if func else 'null'}
        )
        {chart.id}.series.attachPrimitive({self.id})
        ''')

    def update(self, time: TIME):
        self.run_script(f'{self.id}.updatePoints({{time: {time}}})')
        # self.run_script(f'{self.id}.updatePrice({price})')
        self.price = price

    def label(self, text: str): # TODO
        self.run_script(f'{self.id}.updateLabel("{text}")')

    
class VerticalSpan(Pane):
    def __init__(self, series: 'SeriesCommon', start_time: Union[TIME, tuple, list], end_time: Optional[TIME] = None,
                 color: str = 'rgba(252, 219, 3, 0.2)'):
        self._chart = series._chart
        super().__init__(self._chart.win)
        start_time, end_time = pd.to_datetime(start_time), pd.to_datetime(end_time)
        self.run_script(f'''
        {self.id} = {self._chart.id}.chart.addHistogramSeries({{
                color: '{color}',
                priceFormat: {{type: 'volume'}},
                priceScaleId: 'vertical_line',
                lastValueVisible: false,
                priceLineVisible: false,
        }})
        {self.id}.priceScale('').applyOptions({{
            scaleMargins: {{top: 0, bottom: 0}}
        }})
        ''')
        if end_time is None:
            if isinstance(start_time, pd.DatetimeIndex):
                data = [{'time': time.timestamp(), 'value': 1} for time in start_time]
            else:
                data = [{'time': start_time.timestamp(), 'value': 1}]
            self.run_script(f'{self.id}.setData({data})')
        else:
            self.run_script(f'''
            {self.id}.setData(calculateTrendLine(
            {start_time.timestamp()}, 1, {end_time.timestamp()}, 1, {series.id}))
            ''')

    def delete(self):
        """
        Irreversibly deletes the vertical span.
        """
        self.run_script(f'{self._chart.id}.chart.removeSeries({self.id})')
