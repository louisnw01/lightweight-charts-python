import pygments.styles


bulb = pygments.styles.get_style_by_name('lightbulb')
sas = pygments.styles.get_style_by_name('sas')


class DarkStyle(bulb):
    background_color = '#1e2124ff'


class LightStyle(sas):
    background_color = '#efeff4ff'



