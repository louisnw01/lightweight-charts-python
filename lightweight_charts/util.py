import re
from random import choices
from string import ascii_lowercase
from typing import Literal


class MissingColumn(KeyError):
    def __init__(self, message):
        super().__init__(message)
        self.msg = message

    def __str__(self):
        return f'{self.msg}'


class ColorError(ValueError):
    def __init__(self, message):
        super().__init__(message)
        self.msg = message

    def __str__(self):
        return f'{self.msg}'


class IDGen(list):
    def generate(self):
        var = ''.join(choices(ascii_lowercase, k=8))
        if var not in self:
            self.append(var)
            return f'window.{var}'
        self.generate()


def _valid_color(string):
    if string[:3] == 'rgb' or string[:4] == 'rgba' or string[0] == '#':
        return True
    raise ColorError('Colors must be in the format of either rgb, rgba or hex.')


def _js_bool(b: bool): return 'true' if b is True else 'false' if b is False else None


LINE_STYLE = Literal['solid', 'dotted', 'dashed', 'large_dashed', 'sparse_dotted']

MARKER_POSITION = Literal['above', 'below', 'inside']

MARKER_SHAPE = Literal['arrow_up', 'arrow_down', 'circle', 'square']

CROSSHAIR_MODE = Literal['normal', 'magnet']

PRICE_SCALE_MODE = Literal['normal', 'logarithmic', 'percentage', 'index100']


def _line_style(line: LINE_STYLE):
    js = 'LightweightCharts.LineStyle.'
    return js+line[:line.index('_')].title() + line[line.index('_') + 1:].title() if '_' in line else js+line.title()


def _crosshair_mode(mode: CROSSHAIR_MODE):
    return f'LightweightCharts.CrosshairMode.{mode.title()}' if mode else None


def _price_scale_mode(mode: PRICE_SCALE_MODE):
    return f"LightweightCharts.PriceScaleMode.{'IndexedTo100' if mode == 'index100' else mode.title() if mode else None}"


def _marker_shape(shape: MARKER_SHAPE):
    return shape[:shape.index('_')]+shape[shape.index('_')+1:].title() if '_' in shape else shape.title()


def _marker_position(p: MARKER_POSITION):
    return {
        'above': 'aboveBar',
        'below': 'belowBar',
        'inside': 'inBar',
        None: None,
    }[p]


def _convert_timeframe(timeframe):
    spans = {
        'min': 'minute',
        'H': 'hour',
        'D': 'day',
        'W': 'week',
        'M': 'month',
    }
    try:
        multiplier = re.findall(r'\d+', timeframe)[0]
    except IndexError:
        return 1, spans[timeframe]
    timespan = spans[timeframe.replace(multiplier, '')]
    return multiplier, timespan
