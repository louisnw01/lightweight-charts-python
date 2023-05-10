from lightweight_charts.js import LWC
try:
    import wx.html2
except ImportError:
    pass


class WxChart(LWC):
    def __init__(self, parent, width, height, volume_enabled=True):
        super().__init__(volume_enabled)
        self.webview = wx.html2.WebView.New(parent, size=(width, height))

        self.webview.Bind(wx.html2.EVT_WEBVIEW_LOADED, self._on_js_load)
        self.webview.SetPage(self._html, '')

        self.second_load = False

    def run_script(self, script): self.webview.RunScript(script)

    def _on_js_load(self, e: wx.html2.WebViewEvent):
        if not self.second_load:
            self.second_load = True
            return
        self.loaded = True
        for func, args, kwargs in self.js_queue:
            getattr(super(), func)(*args, **kwargs)

    def get_webview(self): return self.webview