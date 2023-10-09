import asyncio

from .util import parse_event_message
from lightweight_charts import abstract

try:
    import wx.html2
except ImportError:
    wx = None

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtWebChannel import QWebChannel
    from PyQt5.QtCore import QObject, pyqtSlot as Slot
except ImportError:
    PyQt5 = None
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        from PySide6.QtWebChannel import QWebChannel
        from PySide6.QtCore import Qt, QObject, Slot
    except ImportError:
        QWebEngineView = None

if QWebEngineView:
    class Bridge(QObject):
        def __init__(self, chart):
            super().__init__()
            self.win = chart.win

        @Slot(str)
        def callback(self, message):
            emit_callback(self.win, message)

try:
    from streamlit.components.v1 import html
except ImportError:
    html = None

try:
    from IPython.display import HTML, display
except ImportError:
    HTML = None


def emit_callback(window, string):
    func, args = parse_event_message(window, string)
    asyncio.create_task(func(*args)) if asyncio.iscoroutinefunction(func) else func(*args)


class WxChart(abstract.AbstractChart):
    def __init__(self, parent, inner_width: float = 1.0, inner_height: float = 1.0,
                 scale_candles_only: bool = False, toolbox: bool = False):
        if wx is None:
            raise ModuleNotFoundError('wx.html2 was not found, and must be installed to use WxChart.')
        self.webview: wx.html2.WebView = wx.html2.WebView.New(parent)
        super().__init__(abstract.Window(self.webview.RunScript, 'window.wx_msg.postMessage.bind(window.wx_msg)'),
                         inner_width, inner_height, scale_candles_only, toolbox)

        self.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, lambda e: wx.CallLater(500, self.win.on_js_load))
        self.webview.Bind(wx.html2.EVT_WEBVIEW_SCRIPT_MESSAGE_RECEIVED, lambda e: emit_callback(self, e.GetString()))
        self.webview.AddScriptMessageHandler('wx_msg')
        self.webview.SetPage(abstract.TEMPLATE, '')
        self.webview.AddUserScript(abstract.JS['toolbox']) if toolbox else None

    def get_webview(self): return self.webview


class QtChart(abstract.AbstractChart):
    def __init__(self, widget=None, inner_width: float = 1.0, inner_height: float = 1.0,
                 scale_candles_only: bool = False, toolbox: bool = False):
        if QWebEngineView is None:
            raise ModuleNotFoundError('QWebEngineView was not found, and must be installed to use QtChart.')
        self.webview = QWebEngineView(widget)
        super().__init__(abstract.Window(self.webview.page().runJavaScript, 'window.pythonObject.callback'),
                         inner_width, inner_height, scale_candles_only, toolbox)

        self.web_channel = QWebChannel()
        self.bridge = Bridge(self)
        self.web_channel.registerObject('bridge', self.bridge)
        self.webview.page().setWebChannel(self.web_channel)
        self.webview.loadFinished.connect(self.win.on_js_load)
        if not PyQt5:
            self.webview.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._html = f'''
        {abstract.TEMPLATE[:85]}
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script>
        var bridge = new QWebChannel(qt.webChannelTransport, function(channel) {{
            var pythonObject = channel.objects.bridge;
            window.pythonObject = pythonObject
        }});
        </script>
        {abstract.TEMPLATE[85:]}
        '''
        self.webview.page().setHtml(self._html)

    def get_webview(self): return self.webview


class StaticLWC(abstract.AbstractChart):
    def __init__(self, width=None, height=None, inner_width=1, inner_height=1,
                 scale_candles_only: bool = False, toolbox=False, autosize=True):
        self._html = abstract.TEMPLATE.replace('</script>\n</body>\n</html>', '')
        super().__init__(abstract.Window(run_script=self.run_script), inner_width, inner_height,
                         scale_candles_only, toolbox, autosize)
        self.width = width
        self.height = height

    def run_script(self, script, run_last=False):
        if run_last:
            self.win.final_scripts.append(script)
        else:
            self._html += '\n' + script

    def load(self):
        if self.win.loaded:
            return
        self.win.loaded = True
        for script in self.win.final_scripts:
            self._html += '\n' + script
        self._load()

    def _load(self): pass


class StreamlitChart(StaticLWC):
    def __init__(self, width=None, height=None, inner_width=1, inner_height=1, scale_candles_only: bool = False, toolbox: bool = False):
        super().__init__(width, height, inner_width, inner_height, scale_candles_only, toolbox)

    def _load(self):
        if html is None:
            raise ModuleNotFoundError('streamlit.components.v1.html was not found, and must be installed to use StreamlitChart.')
        html(f'{self._html}</script></body></html>', width=self.width, height=self.height)


class JupyterChart(StaticLWC):
    def __init__(self, width: int = 800, height=350, inner_width=1, inner_height=1, scale_candles_only: bool = False, toolbox: bool = False):
        super().__init__(width, height, inner_width, inner_height, scale_candles_only, toolbox, False)

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
