import asyncio
from inspect import iscoroutinefunction

try:
    import wx.html2
except ImportError:
    wx = None
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtWebChannel import QWebChannel
    from PyQt5.QtCore import QObject, pyqtSlot

    class Bridge(QObject):
        def __init__(self, chart):
            super().__init__()
            self.chart = chart

        @pyqtSlot(str)
        def callback(self, message):
            _widget_message(self.chart, message)
except ImportError:
    QWebEngineView = None
try:
    from streamlit.components.v1 import html
except ImportError:
    html = None
try:
    from IPython.display import HTML, display
except ImportError:
    HTML = None

from lightweight_charts.abstract import LWC, JS


def _widget_message(chart, string):
    messages = string.split('_~_')
    name, chart_id = messages[:2]
    arg = messages[2]
    chart.api.chart = chart._charts[chart_id]
    fixed_callbacks = ('on_search', 'on_horizontal_line_move')
    func = chart._methods[name] if name not in fixed_callbacks else getattr(chart._api, name)
    if hasattr(chart._api.chart, 'topbar') and (widget := chart._api.chart.topbar._widget_with_method(name)):
        widget.value = arg
        asyncio.create_task(func()) if asyncio.iscoroutinefunction(func) else func()
    else:
        asyncio.create_task(func(*arg.split(';;;'))) if asyncio.iscoroutinefunction(func) else func(*arg.split(';;;'))


class WxChart(LWC):
    def __init__(self, parent, volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0,
                 scale_candles_only: bool = False, api: object = None, topbar: bool = False, searchbox: bool = False,
                 toolbox: bool = False):
        if wx is None:
            raise ModuleNotFoundError('wx.html2 was not found, and must be installed to use WxChart.')
        self.webview: wx.html2.WebView = wx.html2.WebView.New(parent)

        super().__init__(volume_enabled, inner_width=inner_width, inner_height=inner_height,
                         scale_candles_only=scale_candles_only, topbar=topbar, searchbox=searchbox, toolbox=toolbox,
                         _js_api_code='window.wx_msg.postMessage.bind(window.wx_msg)')
        self.api = api
        self._script_func = self.webview.RunScript

        self.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, lambda e: wx.CallLater(500, self._on_js_load))
        self.webview.Bind(wx.html2.EVT_WEBVIEW_SCRIPT_MESSAGE_RECEIVED, lambda e: _widget_message(self, e.GetString()))
        self.webview.AddScriptMessageHandler('wx_msg')
        self.webview.SetPage(self._html, '')
        self.webview.AddUserScript(JS['callback']) if topbar or searchbox else None
        self.webview.AddUserScript(JS['toolbox']) if toolbox else None

    def get_webview(self): return self.webview


class QtChart(LWC):
    def __init__(self, widget=None, volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0,
                 scale_candles_only: bool = False, api: object = None, topbar: bool = False, searchbox: bool = False,
                 toolbox: bool = False):
        if QWebEngineView is None:
            raise ModuleNotFoundError('QWebEngineView was not found, and must be installed to use QtChart.')
        self.webview = QWebEngineView(widget)

        super().__init__(volume_enabled, inner_width=inner_width, inner_height=inner_height,
                         scale_candles_only=scale_candles_only, topbar=topbar, searchbox=searchbox, toolbox=toolbox,
                         _js_api_code='window.pythonObject.callback')
        self.api = api
        self._script_func = self.webview.page().runJavaScript

        self.web_channel = QWebChannel()
        self.bridge = Bridge(self)
        self.web_channel.registerObject('bridge', self.bridge)
        self.webview.page().setWebChannel(self.web_channel)
        self.webview.loadFinished.connect(self._on_js_load)
        self._html = f'''
        {self._html[:85]}
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script>
        var bridge = new QWebChannel(qt.webChannelTransport, function(channel) {{
            var pythonObject = channel.objects.bridge;
            window.pythonObject = pythonObject
        }});
        </script>
        {self._html[85:]}
        '''
        self.webview.page().setHtml(self._html)

    def get_webview(self): return self.webview


class StaticLWC(LWC):
    def __init__(self, volume_enabled=True, width=None, height=None, inner_width=1, inner_height=1, scale_candles_only: bool = False, toolbox=False, autosize=True):
        super().__init__(volume_enabled, inner_width, inner_height, scale_candles_only=scale_candles_only, toolbox=toolbox, autosize=autosize)
        self.width = width
        self.height = height
        self._html = self._html.replace('</script>\n</body>\n</html>', '')

    def run_script(self, script, run_last=False):
        if run_last:
            self._final_scripts.append(script)
        else:
            self._html += '\n' + script

    def load(self):
        if self.loaded:
            return
        self.loaded = True
        for script in self._final_scripts:
            self._html += '\n' + script
        self._load()

    def _load(self): pass


class StreamlitChart(StaticLWC):
    def __init__(self, volume_enabled=True, width=None, height=None, inner_width=1, inner_height=1, scale_candles_only: bool = False, toolbox: bool = False):
        super().__init__(volume_enabled, width, height, inner_width, inner_height, scale_candles_only, toolbox)

    def _load(self):
        if html is None:
            raise ModuleNotFoundError('streamlit.components.v1.html was not found, and must be installed to use StreamlitChart.')
        html(f'{self._html}</script></body></html>', width=self.width, height=self.height)


class JupyterChart(StaticLWC):
    def __init__(self, volume_enabled=True, width: int = 800, height=350, inner_width=1, inner_height=1, scale_candles_only: bool = False, toolbox: bool = False):
        super().__init__(volume_enabled, width, height, inner_width, inner_height, scale_candles_only, toolbox, autosize=False)
        self._position = ""

        self.run_script(f'''
            for (var i = 0; i < document.getElementsByClassName("tv-lightweight-charts").length; i++) {{
                    var element = document.getElementsByClassName("tv-lightweight-charts")[i];
                    element.style.overflow = "visible"
                }}
            document.getElementById('wrapper').style.overflow = 'hidden'
            document.getElementById('wrapper').style.borderRadius = '10px'
            document.getElementById('wrapper').style.width = '{self.width}px'
            document.getElementById('wrapper').style.height = '100%'
            ''')
        self.run_script(f'{self.id}.chart.resize({width}, {height})')

    def _load(self):
        if HTML is None:
            raise ModuleNotFoundError('IPython.display.HTML was not found, and must be installed to use JupyterChart.')
        display(HTML(f'{self._html}</script></body></html>'))
