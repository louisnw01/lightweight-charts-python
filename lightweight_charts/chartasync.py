import asyncio
import multiprocessing as mp
from typing import Literal, Union

from lightweight_charts import LWC
from lightweight_charts.chart import PyWV


class LWCAsync(LWC):
    def __init__(self, volume_enabled: bool = True, inner_width: float = 1.0, inner_height: float = 1.0, dynamic_loading: bool = False):
        super().__init__(volume_enabled, inner_width, inner_height, dynamic_loading)
        self._charts = {self.id: self}

    def _make_search_box(self):
        self.run_script(f'makeSearchBox({self.id}, {self._js_api_code})')

    def corner_text(self, text: str):
        self.run_script(f'{self.id}.cornerText.innerText = "{text}"')

    def create_switcher(self, method, *options, default=None):
        self.run_script(f'''
            makeSwitcher({self.id}, {list(options)}, '{default if default else options[0]}', {self._js_api_code}, '{method.__name__}')
            {self.id}.chart.resize(window.innerWidth*{self._inner_width}, (window.innerHeight*{self._inner_height})-{self.id}.topBar.offsetHeight)
        ''')

    def create_subchart(self, top_bar: bool = True, volume_enabled: bool = True, position: Literal['left', 'right', 'top', 'bottom'] = 'left',
                         width: float = 0.5, height: float = 0.5, sync: Union[bool, str] = False):
        subchart = SubChartAsync(self, top_bar, volume_enabled, position, width, height, sync)
        self._charts[subchart.id] = subchart
        return subchart


class ChartAsync(LWCAsync):
    def __init__(self, api: object, top_bar: bool = True, search_box: bool = True, volume_enabled: bool = True, width: int = 800, height: int = 600, x: int = None, y: int = None,
                 on_top: bool = False, debug: bool = False,
                 inner_width: float = 1.0, inner_height: float = 1.0, dynamic_loading: bool = False):
        super().__init__(volume_enabled, inner_width, inner_height, dynamic_loading)
        self.api = api

        self._js_api_code = 'pywebview.api.callback'
        self._emit = mp.Queue()

        self._q = mp.Queue()
        self._script_func = self._q.put
        self._exit = mp.Event()
        self._loaded = mp.Event()
        self._process = mp.Process(target=PyWV, args=(self._q, self._exit, self._loaded, self._html,
                                                      width, height, x, y, on_top, debug, self._emit), daemon=True)
        self._process.start()

        self.run_script(ASYNC_SCRIPT)
        self._create_chart(top_bar)
        self._make_search_box() if search_box else None

    async def show(self, block=False):
        if not self.loaded:
            self._q.put('start')
            self._loaded.wait()
            self._on_js_load()
        else:
            self._q.put('show')
        if block:
            try:
                while 1:
                    while self._emit.empty() and not self._exit.is_set():
                        await asyncio.sleep(0.1)
                    if self._exit.is_set():
                        return
                    key, chart_id, args = self._emit.get()
                    self.api.chart = self._charts[chart_id]
                    await getattr(self.api, key)(args)

            except KeyboardInterrupt:
                return
        asyncio.create_task(self.show(block=True))


class SubChartAsync(LWCAsync):
    def __init__(self, parent, top_bar, volume_enabled, position, width, height, sync):
        super().__init__(volume_enabled, width, height)
        self._chart = parent._chart if isinstance(parent, SubChartAsync) else parent
        self._parent = parent
        self._position = position
        self._rand = self._chart._rand
        self.id = f'window.{self._rand.generate()}'
        self._js_api_code = self._chart._js_api_code
        self.run_script = self._chart.run_script
        self._charts = self._chart._charts
        self._create_chart(top_bar)
        self._make_search_box()
        if not sync:
            return
        sync_parent_var = self._parent.id if isinstance(sync, bool) else sync
        self.run_script(f'''
            {sync_parent_var}.chart.timeScale().subscribeVisibleLogicalRangeChange((timeRange) => {{
                {self.id}.chart.timeScale().setVisibleLogicalRange(timeRange)
            }});
        ''')


ASYNC_SCRIPT = '''
function makeSearchBox(chart, callbackFunction) {
    let searchWindow = document.createElement('div')
    searchWindow.style.position = 'absolute'
    searchWindow.style.top = '30%'
    searchWindow.style.left = '50%'
    searchWindow.style.transform = 'translate(-50%, -30%)'
    searchWindow.style.width = '200px'
    searchWindow.style.height = '200px'
    searchWindow.style.backgroundColor = 'rgba(30, 30, 30, 0.9)'
    searchWindow.style.zIndex = '1000'
    searchWindow.style.display = 'none'
    searchWindow.style.borderRadius = '10px'

    let sBox = document.createElement('input');
    sBox.type = 'text';
    sBox.placeholder = 'search';
    sBox.style.position = 'absolute';
    sBox.style.zIndex = '1000';

    sBox.style.textAlign = 'center'
    sBox.style.left = '50%';
    sBox.style.top = '30%';
    sBox.style.transform = 'translate(-50%, -30%)'
    sBox.style.width = '100px'

    sBox.style.backgroundColor = 'rgba(0, 122, 255, 0.2)'
    sBox.style.color = 'white'
    sBox.style.fontSize = '20px'            
    sBox.style.border = 'none'
    sBox.style.borderRadius = '5px'

    searchWindow.appendChild(sBox)
    chart.div.appendChild(searchWindow);
    
    let yPrice = null
    chart.chart.subscribeCrosshairMove((param) => {
        if (param.point){
            yPrice = param.point.y;
        }
    });
    
    let selectedChart = false
    chart.wrapper.addEventListener('mouseover', (event) => {
        selectedChart = true
    })
    chart.wrapper.addEventListener('mouseout', (event) => {
        selectedChart = false
    })
    document.addEventListener('keydown', function(event) {
        if (!selectedChart) {return}
        if (event.altKey && event.code === 'KeyH') {
            let price = chart.series.coordinateToPrice(yPrice)
            makeHorizontalLine(chart, price, '#FFFFFF', 1, LightweightCharts.LineStyle.Solid, true, '')
        }
        if (searchWindow.style.display === 'none') {
            if (/^[a-zA-Z0-9]$/.test(event.key)) {
                searchWindow.style.display = 'block';
                sBox.focus();
            }
        }
        else if (event.key === 'Enter') {
            callbackFunction(`on_search__${chart.id}__${sBox.value}`)
            searchWindow.style.display = 'none'
            sBox.value = ''
        }
        else if (event.key === 'Escape') {
            searchWindow.style.display = 'none'
            sBox.value = ''
        }
    });
    sBox.addEventListener('input', function() {
        sBox.value = sBox.value.toUpperCase();
    });
}
    
function makeSwitcher(chart, items, activeItem, callbackFunction, callbackName) {
    let switcherElement = document.createElement('div');
    switcherElement.style.margin = '4px 18px'
    switcherElement.style.zIndex = '1000'

    let intervalElements = items.map(function(item) {
        let itemEl = document.createElement('button');
        itemEl.style.cursor = 'pointer'
        itemEl.style.padding = '3px 6px'
        itemEl.style.margin = '0px 4px'
        itemEl.style.fontSize = '14px'
        itemEl.style.color = 'lightgrey'
        itemEl.style.backgroundColor = item === activeItem ? 'rgba(0, 122, 255, 0.7)' : 'transparent'


        itemEl.style.border = 'none'
        itemEl.style.borderRadius = '4px'
        itemEl.addEventListener('mouseenter', function() {
            itemEl.style.backgroundColor = item === activeItem ? 'rgba(0, 122, 255, 0.7)' : 'rgb(19, 40, 84)'
        })
        itemEl.addEventListener('mouseleave', function() {
            itemEl.style.backgroundColor = item === activeItem ? 'rgba(0, 122, 255, 0.7)' : 'transparent'
        })
        itemEl.innerText = item;
        itemEl.addEventListener('click', function() {
            onItemClicked(item);
        });
        switcherElement.appendChild(itemEl);
        return itemEl;
    });
    function onItemClicked(item) {
        if (item === activeItem) {
            return;
        }
        intervalElements.forEach(function(element, index) {
            element.style.backgroundColor = items[index] === item ? 'rgba(0, 122, 255, 0.7)' : 'transparent'
        });
        activeItem = item;
        callbackFunction(`${callbackName}__${chart.id}__${item}`);
    }
    chart.topBar.appendChild(switcherElement)
    makeSeperator(chart.topBar)
    return switcherElement;
}
function makeTopBar(chart) {
    chart.topBar = document.createElement('div')
    chart.topBar.style.backgroundColor = '#191B1E'
    chart.topBar.style.borderBottom = '3px solid #3C434C'
    chart.topBar.style.borderRadius = '2px'
    chart.topBar.style.display = 'flex'
    chart.topBar.style.alignItems = 'center'
    chart.wrapper.prepend(chart.topBar)

    chart.cornerText = document.createElement('div')
    chart.cornerText.style.margin = '0px 18px'
    chart.cornerText.style.position = 'relative'
    chart.cornerText.style.fontFamily = 'SF Pro'
    chart.cornerText.style.color = 'lightgrey'
    chart.topBar.appendChild(chart.cornerText)

    makeSeperator(chart.topBar)
}
function makeSeperator(topBar) {
    let seperator = document.createElement('div')
        seperator.style.width = '1px'
        seperator.style.height = '20px'
        seperator.style.backgroundColor = '#3C434C'
        topBar.appendChild(seperator)
    }
'''
