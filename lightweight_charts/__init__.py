from .chart import Chart
from .js import LWC

try:
    import wx.html2
    from .widgets import WxChart
except:
    pass
