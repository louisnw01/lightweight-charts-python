import panel as pn
import param
from panel.reactive import ReactiveHTML

from lightweight_charts.abstract import JS, LWC, TopBar
from lightweight_charts.util import _js_bool, _widget_message

JS_FUNCS = JS["funcs"] + JS["callback"]
JS_FUNCS = JS_FUNCS.replace("document.getElementById('wrapper')", "wrapper")

HTML = """
<div id="wrapper" class="pn-wrapper"></div>
"""

CSS = """
.pn-wrapper {height: 100%;width: 100%;}
"""



class PanelChart(ReactiveHTML, LWC):
    _template = HTML

    js_funcs = param.String(JS_FUNCS)
    js_load = param.Boolean(default=False)
    js_event = param.String()

    _js = param.String()

    stylesheets = [CSS]
    _child_config = {'js_funcs': 'literal'}
    __javascript__ = [
        "https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"
    ]
    
    _scripts = {
        "render": """
function clean(value){
    return value.replaceAll("&lt;","<").replaceAll("&gt;",">").replaceAll("&amp;", "&")
}
function callback(value){
    data.js_event = value
}
state.clean = clean
state.callback = callback
id = "pnx-lightweight-charts-script"
script = document.getElementById(id)
if (script===null){
    script = document.createElement("script")
    script.id = id
    script.innerHTML = clean(data.js_funcs)
    body = document.getElementsByTagName('body')[0];
    body.appendChild(script)
}
data.js_load = true
""",
    "_js": """
var clean_js = state.clean(data._js)
new Function("wrapper", "state", clean_js)(wrapper, state)
""",
    "after_layout": """
setTimeout(function(){ window.dispatchEvent(new Event('resize')); }, 200);
"""
    }
    def __init__(self, volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0,
                 scale_candles_only: bool = False, api: object = None, topbar: bool = False, searchbox: bool = False, **kwargs):
        LWC.__init__(self, volume_enabled, inner_width=inner_width, inner_height=inner_height, scale_candles_only=scale_candles_only)
        self.id = "state.chart"
        self._charts = {self.id: self}
        
        ReactiveHTML.__init__(self, **kwargs)
        self.api = api
        self._script_func = self._script_func_core
        self._js_api_code = 'state.callback'
        
        # self.webview.Bind(wx.html2.EVT_WEBVIEW_SCRIPT_MESSAGE_RECEIVED, lambda e: _widget_message(self, e.GetString()))
        # self.webview.AddScriptMessageHandler('wx_msg')
        # self.webview.SetPage(self._html, '')

        # self.webview.AddUserScript(JS['callback'])
        self._create_chart()
        self.topbar = TopBar(self) if topbar else None
        self._make_search_box() if searchbox else None

    def _script_func_core(self, js):
        if self._js == js:
            self.param.trigger("_js")
        else:
            self._js = js        

    @pn.depends("js_load", watch=True)
    def _on_js_load(self):
        LWC._on_js_load(self)

    def _create_chart(self, autosize=True):
        self.run_script(f'''
            {self.id} = makeChartCore(wrapper, {self._inner_width}, {self._inner_height}, autoSize={_js_bool(autosize)})
            {self.id}.id = '{self.id}'
            {self.id}.wrapper.style.float = "{self._position}"
            ''')

    @pn.depends("js_event", watch=True)
    def _handle_js_event(self):
        print(self.js_event)
        _widget_message(self, self.js_event)
