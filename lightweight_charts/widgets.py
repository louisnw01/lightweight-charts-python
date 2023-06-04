import asyncio
from inspect import iscoroutinefunction

try:
    import wx.html2
except ImportError:
    pass
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
    pass
try:
    from streamlit.components.v1 import html
except ImportError:
    pass
try:
    from IPython.display import HTML, display
except ImportError:
    pass

from lightweight_charts.js import LWC, TopBar, CALLBACK_SCRIPT


def _widget_message(chart, string):
    messages = string.split('__')
    name, chart_id = messages[:2]
    args = messages[2:]
    chart.api.chart = chart._charts[chart_id]
    method = getattr(chart.api, name)
    asyncio.create_task(getattr(chart.api, name)(*args)) if iscoroutinefunction(method) else method(*args)


class WxChart(LWC):
    def __init__(self, parent, volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0,
                 api: object = None, topbar: bool = False, searchbox: bool = False):
        try:
            self.webview: wx.html2.WebView = wx.html2.WebView.New(parent)
        except NameError:
            raise ModuleNotFoundError('wx.html2 was not found, and must be installed to use WxChart.')

        super().__init__(volume_enabled, inner_width=inner_width, inner_height=inner_height)
        self.api = api
        self._script_func = self.webview.RunScript
        self._js_api_code = 'window.wx_msg.postMessage.bind(window.wx_msg)'

        self.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, lambda e: wx.CallLater(500, self._on_js_load))
        self.webview.Bind(wx.html2.EVT_WEBVIEW_SCRIPT_MESSAGE_RECEIVED, lambda e: _widget_message(self, e.GetString()))
        self.webview.AddScriptMessageHandler('wx_msg')
        self.webview.SetPage(self._html, '')

        self.webview.AddUserScript(CALLBACK_SCRIPT)
        self._create_chart()
        self.topbar = TopBar(self) if topbar else None
        self._make_search_box() if searchbox else None

    def get_webview(self): return self.webview


class QtChart(LWC):
    def __init__(self, widget=None, api: object = None, topbar: bool = False, searchbox: bool = False,
                 volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0):
        try:
            self.webview = QWebEngineView(widget)
        except NameError:
            raise ModuleNotFoundError('QWebEngineView was not found, and must be installed to use QtChart.')
        super().__init__(volume_enabled, inner_width=inner_width, inner_height=inner_height)
        self.api = api
        self._script_func = self.webview.page().runJavaScript
        self._js_api_code = 'window.pythonObject.callback'

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

        self.run_script(CALLBACK_SCRIPT)
        self._create_chart()
        self.topbar = TopBar(self) if topbar else None
        self._make_search_box() if searchbox else None

    def get_webview(self): return self.webview


class StaticLWC(LWC):
    def __init__(self, volume_enabled=True, width=None, height=None, inner_width=1, inner_height=1):
        super().__init__(volume_enabled, inner_width, inner_height)
        self.width = width
        self.height = height
        self._html = self._html.replace('</script>\n</body>\n</html>', '')

    def run_script(self, script): self._html += '\n' + script

    def load(self):
        if self.loaded:
            return
        self.loaded = True
        self._load()

    def _load(self): pass


class StreamlitChart(StaticLWC):
    def __init__(self, volume_enabled=True, width=None, height=None, inner_width=1, inner_height=1):
        super().__init__(volume_enabled, width, height, inner_width, inner_height)
        self._create_chart()

    def _load(self):
        try:
            html(f'{self._html}</script></body></html>', width=self.width, height=self.height)
        except NameError:
            raise ModuleNotFoundError('streamlit.components.v1.html was not found, and must be installed to use StreamlitChart.')


class JupyterChart(StaticLWC):
    def __init__(self, volume_enabled=True, width=800, height=350, inner_width=1, inner_height=1):
        super().__init__(volume_enabled, width, height, inner_width, inner_height)
        self._position = ""

        self._create_chart(autosize=False)
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
        try:
            display(HTML(f'{self._html}</script></body></html>'))
        except NameError:
            raise ModuleNotFoundError('IPython.display.HTML was not found, and must be installed to use JupyterChart.')

