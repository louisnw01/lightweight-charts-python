try:
    import wx.html2
except ImportError:
    pass
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    from PyQt5.QtWebChannel import QWebChannel
    from PyQt5.QtCore import QObject
except ImportError:
    pass

from lightweight_charts.js import LWC


class WxChart(LWC):
    def __init__(self, parent, volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0):
        try:
            self.webview: wx.html2.WebView = wx.html2.WebView.New(parent)
        except NameError:
            raise ModuleNotFoundError('wx.html2 was not found, and must be installed to use WxChart.')

        super().__init__(volume_enabled, inner_width=inner_width, inner_height=inner_height)

        self.webview.AddScriptMessageHandler('wx_msg')
        self._js_api_code = 'window.wx_msg.postMessage'
        self.webview.Bind(wx.html2.EVT_WEBVIEW_SCRIPT_MESSAGE_RECEIVED, lambda e: self._js_api.onClick(eval(e.GetString())))

        self.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, self._on_js_load)
        self.webview.SetPage(self._html, '')

    def run_script(self, script): self.webview.RunScript(script)

    def _on_js_load(self, e):
        self.loaded = True
        for func, args, kwargs in self.js_queue:
            if 'SUB' in func:
                c_id = args[0]
                args = args[1:]
                getattr(self._subcharts[c_id], func.replace('SUB', ''))(*args)
            else:
                getattr(self, func)(*args)

    def get_webview(self): return self.webview


class QtChart(LWC):
    def __init__(self, widget=None, volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0):
        try:
            self.webview = QWebEngineView(widget)
        except NameError:
            raise ModuleNotFoundError('QWebEngineView was not found, and must be installed to use QtChart.')

        super().__init__(volume_enabled, inner_width=inner_width, inner_height=inner_height)

        self.webview.loadFinished.connect(self._on_js_load)
        self.webview.page().setHtml(self._html)

    def run_script(self, script): self.webview.page().runJavaScript(script)

    def _on_js_load(self):
        self.loaded = True
        for func, args, kwargs in self.js_queue:
            getattr(super(), func)(*args, **kwargs)

    def get_webview(self): return self.webview

