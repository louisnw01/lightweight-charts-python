if (!window.Chart) {
    window.pane = {
        backgroundColor: '#0c0d0f',
        hoverBackgroundColor: '#3c434c',
        clickBackgroundColor: '#50565E',
        activeBackgroundColor: 'rgba(0, 122, 255, 0.7)',
        mutedBackgroundColor: 'rgba(0, 122, 255, 0.3)',
        borderColor: '#3C434C',
        color: '#d8d9db',
        activeColor: '#ececed',
    }

    class Chart {
        constructor(chartId, innerWidth, innerHeight, position, autoSize) {
            this.makeCandlestickSeries = this.makeCandlestickSeries.bind(this)
            this.reSize = this.reSize.bind(this)
            this.id = chartId
            this.lines = []
            this.interval = null
            this.wrapper = document.createElement('div')
            this.div = document.createElement('div')
            this.scale = {
                width: innerWidth,
                height: innerHeight,
            }
            this.commandFunctions = []
            this.chart = LightweightCharts.createChart(this.div, {
                width: window.innerWidth * innerWidth,
                height: window.innerHeight * innerHeight,
                layout: {
                    textColor: pane.color,
                    background: {
                        color: '#000000',
                        type: LightweightCharts.ColorType.Solid,
                    },
                    fontSize: 12
                },
                rightPriceScale: {
                    scaleMargins: {top: 0.3, bottom: 0.25},
                },
                timeScale: {timeVisible: true, secondsVisible: false},
                crosshair: {
                    mode: LightweightCharts.CrosshairMode.Normal,
                    vertLine: {
                        labelBackgroundColor: 'rgb(46, 46, 46)'
                    },
                    horzLine: {
                        labelBackgroundColor: 'rgb(55, 55, 55)'
                    }
                },
                grid: {
                    vertLines: {color: 'rgba(29, 30, 38, 5)'},
                    horzLines: {color: 'rgba(29, 30, 58, 5)'},
                },
                handleScroll: {vertTouchDrag: true},
            })
            this.legend = new Legend(this)
            this.wrapper.style.display = 'flex'
            this.wrapper.style.flexDirection = 'column'
            this.wrapper.style.position = 'relative'
            this.wrapper.style.float = position
            this.div.style.position = 'relative'
            // this.div.style.display = 'flex'
            this.reSize()
            this.wrapper.appendChild(this.div)
            document.getElementById('wrapper').append(this.wrapper)

            document.addEventListener('keydown', (event) => {
                for (let i = 0; i < this.commandFunctions.length; i++) {
                    if (this.commandFunctions[i](event)) break
                }
            })
            if (!autoSize) return
            window.addEventListener('resize', () => this.reSize())
        }
        reSize() {
            let topBarOffset = 'topBar' in this && this.scale.height !== 0 ? this.topBar.offsetHeight : 0
            this.chart.resize(window.innerWidth * this.scale.width, (window.innerHeight * this.scale.height) - topBarOffset)
            this.wrapper.style.width = `${100 * this.scale.width}%`
            this.wrapper.style.height = `${100 * this.scale.height}%`
            if (this.legend) {
                if (this.scale.height === 0 || this.scale.width === 0) {
                    this.legend.div.style.display = 'none'
                }
                else {
                    this.legend.div.style.display = 'flex'
                }
            }

        }
        makeCandlestickSeries() {
            this.markers = []
            this.horizontal_lines = []
            this.candleData = []
            this.precision = 2
            let up = 'rgba(39, 157, 130, 100)'
            let down = 'rgba(200, 97, 100, 100)'
            this.series = this.chart.addCandlestickSeries({
                color: 'rgb(0, 120, 255)', upColor: up, borderUpColor: up, wickUpColor: up,
                downColor: down, borderDownColor: down, wickDownColor: down, lineWidth: 2,
            })
            this.volumeSeries = this.chart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {type: 'volume'},
                priceScaleId: 'volume_scale',
            })
            this.series.priceScale().applyOptions({
                scaleMargins: {top: 0.2, bottom: 0.2},
            });
            this.volumeSeries.priceScale().applyOptions({
                scaleMargins: {top: 0.8, bottom: 0},
            });
        }
        toJSON() {
            // Exclude the chart attribute from serialization
            const {chart, ...serialized} = this;
            return serialized;
        }
    }
    window.Chart = Chart

    class HorizontalLine {
        constructor(chart, lineId, price, color, width, style, axisLabelVisible, text) {
            this.updatePrice = this.updatePrice.bind(this)
            this.deleteLine = this.deleteLine.bind(this)
            this.chart = chart
            this.price = price
            this.color = color
            this.id = lineId
            this.priceLine = {
                price: this.price,
                color: this.color,
                lineWidth: width,
                lineStyle: style,
                axisLabelVisible: axisLabelVisible,
                title: text,
            }
            this.line = this.chart.series.createPriceLine(this.priceLine)
            this.chart.horizontal_lines.push(this)
        }

        toJSON() {
            // Exclude the chart attribute from serialization
            const {chart, line, ...serialized} = this;
            return serialized;
        }

        updatePrice(price) {
            this.chart.series.removePriceLine(this.line)
            this.price = price
            this.priceLine.price = this.price
            this.line = this.chart.series.createPriceLine(this.priceLine)
        }

        updateLabel(text) {
            this.chart.series.removePriceLine(this.line)
            this.priceLine.title = text
            this.line = this.chart.series.createPriceLine(this.priceLine)
        }

        updateColor(color) {
            this.chart.series.removePriceLine(this.line)
            this.color = color
            this.priceLine.color = this.color
            this.line = this.chart.series.createPriceLine(this.priceLine)
        }

        updateStyle(style) {
            this.chart.series.removePriceLine(this.line)
            this.priceLine.lineStyle = style
            this.line = this.chart.series.createPriceLine(this.priceLine)
        }

        deleteLine() {
            this.chart.series.removePriceLine(this.line)
            this.chart.horizontal_lines.splice(this.chart.horizontal_lines.indexOf(this))
            delete this
        }
    }

    window.HorizontalLine = HorizontalLine

    class Legend {
        constructor(chart) {
            this.ohlcEnabled = false
            this.percentEnabled = false
            this.linesEnabled = false

            this.div = document.createElement('div')
            this.div.style.position = 'absolute'
            this.div.style.zIndex = '3000'
            this.div.style.pointerEvents = 'none'
            this.div.style.top = '10px'
            this.div.style.left = '10px'
            this.div.style.display = 'flex'
            this.div.style.flexDirection = 'column'
            this.div.style.maxWidth = `${(chart.scale.width * 100) - 8}vw`

            this.text = document.createElement('span')
            this.text.style.lineHeight = '1.8'
            this.candle = document.createElement('div')

            this.div.appendChild(this.text)
            this.div.appendChild(this.candle)
            chart.div.appendChild(this.div)

            this.makeLines(chart)

            let legendItemFormat = (num, decimal) => num.toFixed(decimal).toString().padStart(8, ' ')

            let shorthandFormat = (num) => {
                const absNum = Math.abs(num)
                if (absNum >= 1000000) {
                    return (num / 1000000).toFixed(1) + 'M';
                } else if (absNum >= 1000) {
                    return (num / 1000).toFixed(1) + 'K';
                }
                return num.toString().padStart(8, ' ');
            }

            chart.chart.subscribeCrosshairMove((param) => {
                if (param.time) {
                    let data = param.seriesData.get(chart.series);
                    let finalString = '<span style="line-height: 1.8;">'
                    if (data) {
                        this.candle.style.color = ''
                        let ohlc = `O ${legendItemFormat(data.open, chart.precision)} 
                                | H ${legendItemFormat(data.high, chart.precision)} 
                                | L ${legendItemFormat(data.low, chart.precision)}
                                | C ${legendItemFormat(data.close, chart.precision)} `
                        let percentMove = ((data.close - data.open) / data.open) * 100
                        let percent = `| ${percentMove >= 0 ? '+' : ''}${percentMove.toFixed(2)} %`
                        finalString += this.ohlcEnabled ? ohlc : ''
                        finalString += this.percentEnabled ? percent : ''

                        let volumeData = param.seriesData.get(chart.volumeSeries)
                        if (volumeData) finalString += this.ohlcEnabled ? `<br>V ${shorthandFormat(volumeData.value)}` : ''
                    }
                    this.candle.innerHTML = finalString + '</span>'
                    this.lines.forEach((line) => {
                        if (!param.seriesData.get(line.line.series)) return
                        let price = param.seriesData.get(line.line.series).value

                        if (line.line.series._series._seriesType === 'Histogram') {
                            price = shorthandFormat(price)
                        }
                        else {
                            price = legendItemFormat(price, line.line.precision)
                        }
                        line.div.innerHTML = `<span style="color: ${line.solid};">▨</span>    ${line.line.name} : ${price}`
                    })

                } else {
                    this.candle.style.color = 'transparent'
                }
            });
        }

        toJSON() {
            // Exclude the chart attribute from serialization
            const {lines, ...serialized} = this;
            return serialized;
        }

        makeLines(chart) {
            this.lines = []
            if (this.linesEnabled) chart.lines.forEach(line => this.lines.push(this.makeLineRow(line)))
        }

        makeLineRow(line) {
            let openEye = `
        <path style="fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke:${this.color};stroke-opacity:1;stroke-miterlimit:4;" d="M 21.998437 12 C 21.998437 12 18.998437 18 12 18 C 5.001562 18 2.001562 12 2.001562 12 C 2.001562 12 5.001562 6 12 6 C 18.998437 6 21.998437 12 21.998437 12 Z M 21.998437 12 " transform="matrix(0.833333,0,0,0.833333,0,0)"/>
        <path style="fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke:${this.color};stroke-opacity:1;stroke-miterlimit:4;" d="M 15 12 C 15 13.654687 13.654687 15 12 15 C 10.345312 15 9 13.654687 9 12 C 9 10.345312 10.345312 9 12 9 C 13.654687 9 15 10.345312 15 12 Z M 15 12 " transform="matrix(0.833333,0,0,0.833333,0,0)"/>\`
        `
            let closedEye = `
        <path style="fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke:${this.color};stroke-opacity:1;stroke-miterlimit:4;" d="M 20.001562 9 C 20.001562 9 19.678125 9.665625 18.998437 10.514062 M 12 14.001562 C 10.392187 14.001562 9.046875 13.589062 7.95 12.998437 M 12 14.001562 C 13.607812 14.001562 14.953125 13.589062 16.05 12.998437 M 12 14.001562 L 12 17.498437 M 3.998437 9 C 3.998437 9 4.354687 9.735937 5.104687 10.645312 M 7.95 12.998437 L 5.001562 15.998437 M 7.95 12.998437 C 6.689062 12.328125 5.751562 11.423437 5.104687 10.645312 M 16.05 12.998437 L 18.501562 15.998437 M 16.05 12.998437 C 17.38125 12.290625 18.351562 11.320312 18.998437 10.514062 M 5.104687 10.645312 L 2.001562 12 M 18.998437 10.514062 L 21.998437 12 " transform="matrix(0.833333,0,0,0.833333,0,0)"/>
        `

            let row = document.createElement('div')
            row.style.display = 'flex'
            row.style.alignItems = 'center'
            let div = document.createElement('div')
            let toggle = document.createElement('div')
            toggle.style.borderRadius = '4px'
            toggle.style.marginLeft = '10px'
            toggle.style.pointerEvents = 'auto'


            let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("width", "22");
            svg.setAttribute("height", "16");

            let group = document.createElementNS("http://www.w3.org/2000/svg", "g");
            group.innerHTML = openEye

            let on = true
            toggle.addEventListener('click', (event) => {
                if (on) {
                    on = false
                    group.innerHTML = closedEye
                    line.series.applyOptions({
                        visible: false
                    })
                } else {
                    on = true
                    line.series.applyOptions({
                        visible: true
                    })
                    group.innerHTML = openEye
                }
            })
            toggle.addEventListener('mouseover', (event) => {
                document.body.style.cursor = 'pointer'
                toggle.style.backgroundColor = 'rgba(50, 50, 50, 0.5)'
            })
            toggle.addEventListener('mouseleave', (event) => {
                document.body.style.cursor = 'default'
                toggle.style.backgroundColor = 'transparent'
            })
            svg.appendChild(group)
            toggle.appendChild(svg);
            row.appendChild(div)
            row.appendChild(toggle)
            this.div.appendChild(row)
            return {
                div: div,
                row: row,
                toggle: toggle,
                line: line,
                solid: line.color.startsWith('rgba') ? line.color.replace(/[^,]+(?=\))/, '1') : line.color
            }
        }
    }

    window.Legend = Legend
}

function syncCharts(childChart, parentChart) {
    syncCrosshairs(childChart.chart, parentChart.chart)
    syncRanges(childChart, parentChart)
}
function syncCrosshairs(childChart, parentChart) {
    function crosshairHandler (e, thisChart, otherChart, otherHandler) {
        thisChart.applyOptions({crosshair: { horzLine: {
            visible: true,
            labelVisible: true,
        }}})
        otherChart.applyOptions({crosshair: { horzLine: {
            visible: false,
            labelVisible: false,
        }}})

        otherChart.unsubscribeCrosshairMove(otherHandler)
        if (e.time !== undefined) {
          let xx = otherChart.timeScale().timeToCoordinate(e.time);
          otherChart.setCrosshairXY(xx,300,true);
        } else if (e.point !== undefined){
          otherChart.setCrosshairXY(e.point.x,300,false);
        }
        otherChart.subscribeCrosshairMove(otherHandler)
    }
    let parent = 0
    let child = 0
    let parentCrosshairHandler = (e) => {
        parent ++
        if (parent < 10) return
        child = 0
        crosshairHandler(e, parentChart, childChart, childCrosshairHandler)
    }
    let childCrosshairHandler = (e) => {
        child ++
        if (child < 10) return
        parent = 0
        crosshairHandler(e, childChart, parentChart, parentCrosshairHandler)
    }
    parentChart.subscribeCrosshairMove(parentCrosshairHandler)
    childChart.subscribeCrosshairMove(childCrosshairHandler)
}
function syncRanges(childChart, parentChart) {
    let setChildRange = (timeRange) => childChart.chart.timeScale().setVisibleLogicalRange(timeRange)
    let setParentRange = (timeRange) => parentChart.chart.timeScale().setVisibleLogicalRange(timeRange)

    parentChart.wrapper.addEventListener('mouseover', (event) => {
        childChart.chart.timeScale().unsubscribeVisibleLogicalRangeChange(setParentRange)
        parentChart.chart.timeScale().subscribeVisibleLogicalRangeChange(setChildRange)
    })
    childChart.wrapper.addEventListener('mouseover', (event) => {
        parentChart.chart.timeScale().unsubscribeVisibleLogicalRangeChange(setChildRange)
        childChart.chart.timeScale().subscribeVisibleLogicalRangeChange(setParentRange)
    })
    parentChart.chart.timeScale().subscribeVisibleLogicalRangeChange(setChildRange)
}

function stampToDate(stampOrBusiness) {
    return new Date(stampOrBusiness*1000)
}
function dateToStamp(date) {
    return Math.floor(date.getTime()/1000)
}

function lastBar(obj) {
    return obj[obj.length-1]
}

function calculateTrendLine(startDate, startValue, endDate, endValue, chart, ray=false) {
    let reversed = false
    if (stampToDate(endDate).getTime() < stampToDate(startDate).getTime()) {
        reversed = true;
        [startDate, endDate] = [endDate, startDate];
    }
    let startIndex
    if (stampToDate(startDate).getTime() < stampToDate(chart.candleData[0].time).getTime()) {
        startIndex = 0
    }
    else {
        startIndex = chart.candleData.findIndex(item => stampToDate(item.time).getTime() === stampToDate(startDate).getTime())
    }

    if (startIndex === -1) {
        return []
    }
    let endIndex
    if (ray) {
        endIndex = chart.candleData.length+1000
        startValue = endValue
    }
    else {
        endIndex = chart.candleData.findIndex(item => stampToDate(item.time).getTime() === stampToDate(endDate).getTime())
        if (endIndex === -1) {
            let barsBetween = (endDate-lastBar(chart.candleData).time)/chart.interval
            endIndex = chart.candleData.length-1+barsBetween
        }
    }

    let numBars = endIndex-startIndex
    const rate_of_change = (endValue - startValue) / numBars;
    const trendData = [];
    let currentDate = null
    let iPastData = 0
    for (let i = 0; i <= numBars; i++) {
        if (chart.candleData[startIndex+i]) {
            currentDate = chart.candleData[startIndex+i].time
        }
        else {
            iPastData ++
            currentDate = lastBar(chart.candleData).time+(iPastData*chart.interval)
        }

        const currentValue = reversed ? startValue + rate_of_change * (numBars - i) : startValue + rate_of_change * i;
        trendData.push({ time: currentDate, value: currentValue });
    }
    return trendData;
}


if (!window.ContextMenu) {
    class ContextMenu {
        constructor() {
            this.menu = document.createElement('div')
            this.menu.style.position = 'absolute'
            this.menu.style.zIndex = '10000'
            this.menu.style.background = 'rgb(50, 50, 50)'
            this.menu.style.color = pane.activeColor
            this.menu.style.display = 'none'
            this.menu.style.borderRadius = '5px'
            this.menu.style.padding = '3px 3px'
            this.menu.style.fontSize = '13px'
            this.menu.style.cursor = 'default'
            document.body.appendChild(this.menu)
            this.hoverItem = null

            let closeMenu = (event) => {
                if (!this.menu.contains(event.target)) {
                    this.menu.style.display = 'none';
                    this.listen(false)
                }
            }

            this.onRightClick = (event) => {
                event.preventDefault();
                this.menu.style.left = event.clientX + 'px';
                this.menu.style.top = event.clientY + 'px';
                this.menu.style.display = 'block';
                document.removeEventListener('click', closeMenu)
                document.addEventListener('click', closeMenu)
            }
        }
        listen(active) {
            active ? document.addEventListener('contextmenu', this.onRightClick) : document.removeEventListener('contextmenu', this.onRightClick)
        }
        menuItem(text, action, hover=false) {
            let item = document.createElement('span')
            item.style.display = 'flex'
            item.style.alignItems = 'center'
            item.style.justifyContent = 'space-between'
            item.style.padding = '2px 10px'
            item.style.margin = '1px 0px'
            item.style.borderRadius = '3px'
            this.menu.appendChild(item)

            let elem = document.createElement('span')
            elem.innerText = text
            elem.style.pointerEvents = 'none'
            item.appendChild(elem)

            if (hover) {
                let arrow = document.createElement('span')
                arrow.innerText = `►`
                arrow.style.fontSize = '8px'
                arrow.style.pointerEvents = 'none'
                item.appendChild(arrow)
            }

            item.addEventListener('mouseover', (event) => {
                item.style.backgroundColor = 'rgba(0, 122, 255, 0.3)'
                if (this.hoverItem && this.hoverItem.closeAction) this.hoverItem.closeAction()
                this.hoverItem = {elem: elem, action: action, closeAction: hover}
            })
            item.addEventListener('mouseout', (event) => item.style.backgroundColor = 'transparent')
            if (!hover) item.addEventListener('click', (event) => {action(event); this.menu.style.display = 'none'})
            else {
                let timeout
                item.addEventListener('mouseover', () => timeout = setTimeout(() => action(item.getBoundingClientRect()), 100))
                item.addEventListener('mouseout', () => clearTimeout(timeout))
            }
        }
        separator() {
            let separator = document.createElement('div')
            separator.style.width = '90%'
            separator.style.height = '1px'
            separator.style.margin = '3px 0px'
            separator.style.backgroundColor = pane.borderColor
            this.menu.appendChild(separator)
        }

    }
    window.ContextMenu = ContextMenu
}

window.callbackFunction = () => undefined;