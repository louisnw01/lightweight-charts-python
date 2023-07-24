function makeChart(callbackFunction, innerWidth, innerHeight, autoSize=true) {
    let chart = {
        markers: [],
        horizontal_lines: [],
        lines: [],
        wrapper: document.createElement('div'),
        div: document.createElement('div'),
        scale: {
            width: innerWidth,
            height: innerHeight,
        },
        callbackFunction: callbackFunction,
        candleData: [],
        commandFunctions: []
    }
    chart.chart = LightweightCharts.createChart(chart.div, {
        width: window.innerWidth*innerWidth,
        height: window.innerHeight*innerHeight,
        layout: {
            textColor: '#d1d4dc',
            background: {
                color:'#000000',
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
    let up = 'rgba(39, 157, 130, 100)'
    let down = 'rgba(200, 97, 100, 100)'
    chart.series = chart.chart.addCandlestickSeries({
        color: 'rgb(0, 120, 255)', upColor: up, borderUpColor: up, wickUpColor: up,
        downColor: down, borderDownColor: down, wickDownColor: down, lineWidth: 2,
    })
    chart.volumeSeries = chart.chart.addHistogramSeries({
                        color: '#26a69a',
                        priceFormat: {type: 'volume'},
                        priceScaleId: '',
                        })
    chart.series.priceScale().applyOptions({
        scaleMargins: {top: 0.2, bottom: 0.2},
    });
    chart.volumeSeries.priceScale().applyOptions({
        scaleMargins: {top: 0.8, bottom: 0},
    });
    chart.wrapper.style.width = `${100*innerWidth}%`
    chart.wrapper.style.height = `${100*innerHeight}%`
    chart.wrapper.style.display = 'flex'
    chart.wrapper.style.flexDirection = 'column'

    chart.div.style.position = 'relative'
    chart.div.style.display = 'flex'
    chart.wrapper.appendChild(chart.div)
    document.getElementById('wrapper').append(chart.wrapper)

    document.addEventListener('keydown', (event) => {
        for (let i=0; i<chart.commandFunctions.length; i++) {
            if (chart.commandFunctions[i](event)) break
        }
    })

    if (!autoSize) return chart
    window.addEventListener('resize', () => reSize(chart))
    return chart
}

function reSize(chart) {
    let topBarOffset = 'topBar' in chart ? chart.topBar.offsetHeight : 0
    chart.chart.resize(window.innerWidth*chart.scale.width, (window.innerHeight*chart.scale.height)-topBarOffset)
}

if (!window.HorizontalLine) {
    class HorizontalLine {
        constructor(chart, lineId, price, color, width, style, axisLabelVisible, text) {
            this.updatePrice = this.updatePrice.bind(this)
            this.deleteLine = this.deleteLine.bind(this)
            this.chart = chart
            this.price = price
            this.id = lineId
            this.priceLine = {
                price: this.price,
                color: color,
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

        deleteLine() {
            this.chart.series.removePriceLine(this.line)
            this.chart.horizontal_lines.splice(this.chart.horizontal_lines.indexOf(this))
            delete this
        }
    }

    window.HorizontalLine = HorizontalLine

    class Legend {
        constructor(chart, ohlcEnabled = true, percentEnabled = true, linesEnabled = true,
                    color = 'rgb(191, 195, 203)', fontSize = '11', fontFamily = 'Monaco') {
            this.div = document.createElement('div')
            this.div.style.position = 'absolute'
            this.div.style.zIndex = '3000'
            this.div.style.top = '10px'
            this.div.style.left = '10px'
            this.div.style.display = 'flex'
            this.div.style.flexDirection = 'column'
            this.div.style.width = `${(chart.scale.width * 100) - 8}vw`
            this.div.style.color = color
            this.div.style.fontSize = fontSize + 'px'
            this.div.style.fontFamily = fontFamily
            this.candle = document.createElement('div')

            this.div.appendChild(this.candle)
            chart.div.appendChild(this.div)

            this.color = color

            this.linesEnabled = linesEnabled
            this.makeLines(chart)

            let legendItemFormat = (num) => num.toFixed(2).toString().padStart(8, ' ')

            chart.chart.subscribeCrosshairMove((param) => {
                if (param.time) {
                    let data = param.seriesData.get(chart.series);
                    let finalString = '<span style="line-height: 1.8;">'
                    if (data) {
                        this.candle.style.color = ''
                        let ohlc = `O ${legendItemFormat(data.open)} 
                                | H ${legendItemFormat(data.high)} 
                                | L ${legendItemFormat(data.low)}
                                | C ${legendItemFormat(data.close)} `
                        let percentMove = ((data.close - data.open) / data.open) * 100
                        let percent = `| ${percentMove >= 0 ? '+' : ''}${percentMove.toFixed(2)} %`

                        finalString += ohlcEnabled ? ohlc : ''
                        finalString += percentEnabled ? percent : ''

                    }
                    this.candle.innerHTML = finalString + '</span>'
                    this.lines.forEach((line) => {
                        if (!param.seriesData.get(line.line.series)) return
                        let price = legendItemFormat(param.seriesData.get(line.line.series).value)
                        line.div.innerHTML = `<span style="color: ${line.line.color};">▨</span>    ${line.line.name} : ${price}`
                    })

                } else {
                    this.candle.style.color = 'transparent'
                }
            });
        }

        makeLines(chart) {
            this.lines = []
            if (this.linesEnabled) {
                chart.lines.forEach((line) => {
                    this.lines.push(this.makeLineRow(line))
                })
            }
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
            }
        }
    }

    window.Legend = Legend
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

function chartTimeToDate(stampOrBusiness) {
    if (typeof stampOrBusiness === 'number') {
        stampOrBusiness = new Date(stampOrBusiness*1000)
    }
    else if (typeof stampOrBusiness === 'string') {
        let [year, month, day] = stampOrBusiness.split('-').map(Number)
        stampOrBusiness = new Date(Date.UTC(year, month-1, day))
    }
    else {
        stampOrBusiness = new Date(Date.UTC(stampOrBusiness.year, stampOrBusiness.month - 1, stampOrBusiness.day))
    }
    return stampOrBusiness
}

function dateToChartTime(date, interval) {
    if (interval >= 24*60*60*1000) {
        return {day: date.getUTCDate(), month: date.getUTCMonth()+1, year: date.getUTCFullYear()}
    }
    return Math.floor(date.getTime()/1000)
}

function calculateTrendLine(startDate, startValue, endDate, endValue, interval, chart, ray=false) {
    let reversed = false
    if (chartTimeToDate(endDate).getTime() < chartTimeToDate(startDate).getTime()) {
        reversed = true;
        [startDate, endDate] = [endDate, startDate];
    }
    let startIndex
    if (chartTimeToDate(startDate).getTime() < chartTimeToDate(chart.candleData[0].time).getTime()) {
        startIndex = 0
    }
    else {
        startIndex = chart.candleData.findIndex(item => chartTimeToDate(item.time).getTime() === chartTimeToDate(startDate).getTime())
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
        endIndex = chart.candleData.findIndex(item => chartTimeToDate(item.time).getTime() === chartTimeToDate(endDate).getTime())
        if (endIndex === -1) {
            let barsBetween = (chartTimeToDate(endDate)-chartTimeToDate(chart.candleData[chart.candleData.length-1].time))/interval
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
            currentDate = dateToChartTime(new Date(chartTimeToDate(chart.candleData[chart.candleData.length-1].time).getTime()+(iPastData*interval)), interval)

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
            this.menu.style.color = 'lightgrey'
            this.menu.style.display = 'none'
            this.menu.style.borderRadius = '5px'
            this.menu.style.padding = '3px 3px'
            this.menu.style.fontSize = '14px'
            this.menu.style.cursor = 'default'
            document.body.appendChild(this.menu)

            let closeMenu = (event) => {
                if (!this.menu.contains(event.target)) this.menu.style.display = 'none';
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
        menuItem(text, action) {
            let elem = document.createElement('div')
            elem.innerText = text
            elem.style.padding = '0px 10px'
            elem.style.borderRadius = '3px'
            this.menu.appendChild(elem)
            elem.addEventListener('mouseover', (event) => elem.style.backgroundColor = 'rgba(0, 122, 255, 0.3)')
            elem.addEventListener('mouseout', (event) => elem.style.backgroundColor = 'transparent')
            elem.addEventListener('click', (event) => {action(); this.menu.style.display = 'none'})
        }
    }
    window.ContextMenu = ContextMenu
}
