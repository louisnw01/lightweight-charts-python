try:
    import wx.html2
except ImportError:
    pass
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except ImportError:
    pass

from lightweight_charts.js import LWC


class WxChart(LWC):
    def __init__(self, parent, volume_enabled=True):
        super().__init__(volume_enabled)
        try:
            self.webview = wx.html2.WebView.New(parent)
        except NameError:
            raise ModuleNotFoundError('wx.html2 was not found, and must be installed to use WxChart.')

        self.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, self._on_js_load)
        self.webview.SetPage(self._html, '')

        self.second_load = False

    def run_script(self, script): self.webview.RunScript(script)

    def _on_js_load(self, e):
        if not self.second_load:
            self.second_load = True
            return
        self.loaded = True
        for func, args, kwargs in self.js_queue:
            getattr(super(), func)(*args, **kwargs)

    def get_webview(self): return self.webview


class QtChart(LWC):
    def __init__(self, widget=None, volume_enabled=True):
        super().__init__(volume_enabled)
        try:
            self.webview = QWebEngineView(widget)
        except NameError:
            raise ModuleNotFoundError('QWebEngineView was not found, and must be installed to use QtChart.')

        self.webview.loadFinished.connect(self._on_js_load)
        self.webview.page().setHtml(self._html)

    def run_script(self, script): self.webview.page().runJavaScript(script)

    def _on_js_load(self):
        self.loaded = True
        for func, args, kwargs in self.js_queue:
            getattr(super(), func)(*args, **kwargs)

    def get_webview(self): return self.webview

