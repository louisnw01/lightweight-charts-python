import asyncio
import json
from datetime import datetime
from random import choices
from typing import Literal, Union
import pandas as pd


class Pane:
    def __init__(self, window):
        from lightweight_charts import Window
        self.win: Window = window
        self.run_script = window.run_script
        if hasattr(self, 'id'):
            return
        self.id = Window._id_gen.generate()


class IDGen(list):
    ascii = 'abcdefghijklmnopqrstuvwxyz'

    def generate(self):
        var = ''.join(choices(self.ascii, k=8))
        if var not in self:
            self.append(var)
            return f'window.{var}'
        self.generate()


def parse_event_message(window, string):
    name, args = string.split('_~_')
    args = args.split(';;;')
    func = window.handlers[name]
    return func, args


def js_data(data: Union[pd.DataFrame, pd.Series]):
    if isinstance(data, pd.DataFrame):
        d = data.to_dict(orient='records')
        filtered_records = [{k: v for k, v in record.items() if v is not None} for record in d]
    else:
        d = data.to_dict()
        filtered_records = {k: v for k, v in d.items()}
    return json.dumps(filtered_records, indent=2)


def jbool(b: bool): return 'true' if b is True else 'false' if b is False else None


LINE_STYLE = Literal['solid', 'dotted', 'dashed', 'large_dashed', 'sparse_dotted']

MARKER_POSITION = Literal['above', 'below', 'inside']

MARKER_SHAPE = Literal['arrow_up', 'arrow_down', 'circle', 'square']

CROSSHAIR_MODE = Literal['normal', 'magnet']

PRICE_SCALE_MODE = Literal['normal', 'logarithmic', 'percentage', 'index100']

TIME = Union[datetime, pd.Timestamp, str]

NUM = Union[float, int]

FLOAT = Literal['left', 'right', 'top', 'bottom']


def line_style(line: LINE_STYLE):
    js = 'LightweightCharts.LineStyle.'
    return js+line[:line.index('_')].title() + line[line.index('_') + 1:].title() if '_' in line else js+line.title()


def crosshair_mode(mode: CROSSHAIR_MODE):
    return f'LightweightCharts.CrosshairMode.{mode.title()}' if mode else None


def price_scale_mode(mode: PRICE_SCALE_MODE):
    return f"LightweightCharts.PriceScaleMode.{'IndexedTo100' if mode == 'index100' else mode.title() if mode else None}"


def marker_shape(shape: MARKER_SHAPE):
    return shape[:shape.index('_')]+shape[shape.index('_')+1:].title() if '_' in shape else shape


def marker_position(p: MARKER_POSITION):
    return {
        'above': 'aboveBar',
        'below': 'belowBar',
        'inside': 'inBar',
        None: None,
    }[p]


class Emitter:
    def __init__(self):
        self._callable = None

    def __iadd__(self, other):
        self._callable = other
        return self

    def _emit(self, *args):
        if self._callable:
            if asyncio.iscoroutinefunction(self._callable):
                asyncio.create_task(self._callable(*args))
            else:
                self._callable(*args)


class JSEmitter:
    def __init__(self, chart, name, on_iadd, wrapper=None):
        self._on_iadd = on_iadd
        self._chart = chart
        self._name = name
        self._wrapper = wrapper

    def __iadd__(self, other):
        def final_wrapper(*arg):
            other(self._chart, *arg) if not self._wrapper else self._wrapper(other, self._chart, *arg)
        async def final_async_wrapper(*arg):
            await other(self._chart, *arg) if not self._wrapper else await self._wrapper(other, self._chart, *arg)

        self._chart.win.handlers[self._name] = final_async_wrapper if asyncio.iscoroutinefunction(other) else final_wrapper
        self._on_iadd(other)
        return self


class Events:
    def __init__(self, chart):
        self.new_bar = Emitter()
        from lightweight_charts.abstract import JS
        self.search = JSEmitter(chart, f'search{chart.id}',
            lambda o: chart.run_script(f'''
            {JS['callback']}
            makeSpinner({chart.id})
            {chart.id}.search = makeSearchBox({chart.id})
            ''')
        )
        salt = chart.id[chart.id.index('.')+1:]
        self.range_change = JSEmitter(chart, f'range_change{salt}',
            lambda o: chart.run_script(f'''
            let checkLogicalRange{salt} = (logical) => {{
                {chart.id}.chart.timeScale().unsubscribeVisibleLogicalRangeChange(checkLogicalRange{salt})
                
                let barsInfo = {chart.id}.series.barsInLogicalRange(logical)
                if (barsInfo) window.callbackFunction(`range_change{salt}_~_${{barsInfo.barsBefore}};;;${{barsInfo.barsAfter}}`)
                    
                setTimeout(() => {chart.id}.chart.timeScale().subscribeVisibleLogicalRangeChange(checkLogicalRange{salt}), 50)
            }}
            {chart.id}.chart.timeScale().subscribeVisibleLogicalRangeChange(checkLogicalRange{salt})
            '''),
            wrapper=lambda o, c, *arg: o(c, *[float(a) for a in arg])
        )
        self.mouse_move = JSEmitter(chart, f'mouse_move{salt}',
            lambda o: chart.run_script(f'''
            let checkMouseMove = (param) => {{
                {chart.id}.chart.unsubscribeCrosshairMove(checkMouseMove)
                if (
                    param.point === undefined ||
                    !param.time ||
                    param.point.x < 0 ||
                    param.point.y < 0
                ) {{
                    window.callbackFunction(`mouse_move{salt}_~_${{0}};;;${{0}};;;${{0}};;;${{0}};;;${{0}};;;${{0}}`)
                }} else {{
                let x = param.point.x;
                let dateStr = param.time;
                let data = param.seriesData.get({chart.id}.series);
                let open = data.open;
                let high = data.high;
                let low = data.low;
                let close = data.close;
                window.callbackFunction(`mouse_move{chart.id}_~_${{x}};;;${{dateStr}};;;${{open}};;;${{high}};;;${{low}};;;${{close}}`)
                }}
                setTimeout(() => {chart.id}.chart.subscribeCrosshairMove(checkMouseMove{salt}), 50)
            }}
            {chart.id}.chart.subscribeCrosshairMove(checkMouseMove{salt})
            '''),
            wrapper=lambda o, c, *arg: o(c, *[float(a) for a in arg]))
        self.click = JSEmitter(chart, f'click{salt}',
            lambda o: chart.run_script(f'''
            let checkClick = (param) => {{
                {salt}.chart.unsubscribeClick(checkClick)
                if (
                    param.point === undefined ||
                    !param.time ||
                    param.point.x < 0 ||
                    param.point.y < 0
                ) {{
                    window.callbackFunction(`click{salt}_~_${{0}};;;${{0}};;;${{0}};;;${{0}};;;${{0}};;;${{0}}`)
                }} else {{
                let x = param.point.x;
                let dateStr = param.time;
                let data = param.seriesData.get({chart.id}.series);
                let open = data.open;
                let high = data.high;
                let low = data.low;
                let close = data.close;
                let y = param.point.y
                let price = {chart.id}.series.coordinateToPrice(param.point.y);
                window.callbackFunction(`click{salt}_~_${{x}};;;${{dateStr}};;;${{open}};;;${{high}};;;${{low}};;;${{close}};;;${{y}};;;${{price}}`)
                }}
                setTimeout(() => {chart.id}.chart.subscribeClick(checkClick{salt}), 50)
            }}
            {chart.id}.chart.subscribeClick(checkClick{salt})
            '''),
            wrapper=lambda o, c, *arg: o(c, *[float(a) for a in arg]))


class BulkRunScript:
    def __init__(self, script_func):
        self.enabled = False
        self.scripts = []
        self.script_func = script_func

    def __enter__(self):
        self.enabled = True

    def __exit__(self, *args):
        self.enabled = False
        self.script_func('\n'.join(self.scripts))
        self.scripts = []

    def add_script(self, script):
        self.scripts.append(script)
