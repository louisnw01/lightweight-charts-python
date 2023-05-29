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

from lightweight_charts.chartasync import LWCAsync, ASYNC_SCRIPT
from lightweight_charts.js import LWC


def _widget_message(chart, string):
    messages = string.split('__')
    name, chart_id = messages[:2]
    args = messages[2:]
    chart.api.chart = chart._charts[chart_id]
    getattr(chart.api, name)(*args)


class WxChart(LWCAsync):
    def __init__(self, parent, api: object = None, top_bar: bool = False, search_box: bool = False,
                 volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0):
        try:
            self.webview: wx.html2.WebView = wx.html2.WebView.New(parent)
        except NameError:
            raise ModuleNotFoundError('wx.html2 was not found, and must be installed to use WxChart.')

        super().__init__(volume_enabled, inner_width=inner_width, inner_height=inner_height)
        self.api = api
        self._script_func = self.webview.RunScript
        self._js_api_code = 'window.wx_msg.postMessage.bind(window.wx_msg)'

        self.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, lambda e: wx.CallLater(200, self._on_js_load))
        self.webview.Bind(wx.html2.EVT_WEBVIEW_SCRIPT_MESSAGE_RECEIVED, lambda e: _widget_message(self, e.GetString()))
        self.webview.AddScriptMessageHandler('wx_msg')

        self.webview.SetPage(self._html, '')
        self.webview.AddUserScript(ASYNC_SCRIPT)
        self._create_chart(top_bar)
        self._make_search_box() if search_box else None

    def get_webview(self): return self.webview


class QtChart(LWCAsync):
    def __init__(self, widget=None, api: object = None, top_bar: bool = False, search_box: bool = False,
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
        self.run_script(ASYNC_SCRIPT)
        self._create_chart(top_bar)
        self._make_search_box() if search_box else None

    def get_webview(self): return self.webview


class StreamlitChart(LWC):
    def __init__(self, volume_enabled=True, width=None, height=None, inner_width=1, inner_height=1):
        super().__init__(volume_enabled, inner_width, inner_height)

        self.width = width
        self.height = height

        self._html = self._html.replace('</script>\n</body>\n</html>', '')
        self._create_chart()

    def run_script(self, script): self._html += '\n' + script

    def load(self):
        if self.loaded:
            return
        self.loaded = True
        try:
            html(f'{self._html}</script></body></html>', width=self.width, height=self.height)
        except NameError:
            raise ModuleNotFoundError('streamlit.components.v1.html was not found, and must be installed to use StreamlitChart.')

