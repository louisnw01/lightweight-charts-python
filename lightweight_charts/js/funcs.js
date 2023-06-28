function makeChart(innerWidth, innerHeight, autoSize=true) {
    let chart = {
        markers: [],
        horizontal_lines: [],
        wrapper: document.createElement('div'),
        div: document.createElement('div'),
        legend: document.createElement('div'),
        scale: {
            width: innerWidth,
            height: innerHeight
        },
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
    chart.legend.style.position = 'absolute'
    chart.legend.style.zIndex = 1000
    chart.legend.style.width = `${(chart.scale.width*100)-8}vw`
    chart.legend.style.top = '10px'
    chart.legend.style.left = '10px'
    chart.legend.style.fontFamily = 'Monaco'
    chart.legend.style.fontSize = '11px'
    chart.legend.style.color = 'rgb(191, 195, 203)'

    chart.wrapper.style.width = `${100*innerWidth}%`
    chart.wrapper.style.height = `${100*innerHeight}%`
    chart.wrapper.style.display = 'flex'
    chart.wrapper.style.flexDirection = 'column'

    chart.div.style.position = 'relative'
    chart.div.style.display = 'flex'

    chart.div.appendChild(chart.legend)
    chart.wrapper.appendChild(chart.div)
    document.getElementById('wrapper').append(chart.wrapper)

    if (!autoSize) {
        return chart
    }
    let topBarOffset = 0
    window.addEventListener('resize', function() {
        if ('topBar' in chart) {
        topBarOffset = chart.topBar.offsetHeight
        }
        chart.chart.resize(window.innerWidth*innerWidth, (window.innerHeight*innerHeight)-topBarOffset)
        });
    return chart
}
function makeHorizontalLine(chart, lineId, price, color, width, style, axisLabelVisible, text) {
    let priceLine = {
       price: price,
       color: color,
       lineWidth: width,
       lineStyle: style,
       axisLabelVisible: axisLabelVisible,
       title: text,
    };
    let line = {
       line: chart.series.createPriceLine(priceLine),
       price: price,
       id: lineId,
    };
    chart.horizontal_lines.push(line)
}
function legendItemFormat(num) {
return num.toFixed(2).toString().padStart(8, ' ')
}
function syncCrosshairs(childChart, parentChart) {
    let parent = 0
    let child = 0

    let parentCrosshairHandler = (e) => {
        parent ++
        if (parent < 10) {
            return
        }
        child = 0
        parentChart.applyOptions({crosshair: { horzLine: {
            visible: true,
            labelVisible: true,
        }}})
        childChart.applyOptions({crosshair: { horzLine: {
            visible: false,
            labelVisible: false,
        }}})

        childChart.unsubscribeCrosshairMove(childCrosshairHandler)
        if (e.time !== undefined) {
          let xx = childChart.timeScale().timeToCoordinate(e.time);
          childChart.setCrosshairXY(xx,300,true);
        } else if (e.point !== undefined){
          childChart.setCrosshairXY(e.point.x,300,false);
        }
        childChart.subscribeCrosshairMove(childCrosshairHandler)
    }

    let childCrosshairHandler = (e) => {
        child ++
        if (child < 10) {
            return
        }
        parent = 0
        childChart.applyOptions({crosshair: {horzLine: {
            visible: true,
            labelVisible: true,
        }}})
        parentChart.applyOptions({crosshair: {horzLine: {
            visible: false,
            labelVisible: false,
        }}})

        parentChart.unsubscribeCrosshairMove(parentCrosshairHandler)
        if (e.time !== undefined) {
          let xx = parentChart.timeScale().timeToCoordinate(e.time);
          parentChart.setCrosshairXY(xx,300,true);
        } else if (e.point !== undefined){
          parentChart.setCrosshairXY(e.point.x,300,false);
        }
        parentChart.subscribeCrosshairMove(parentCrosshairHandler)
    }
    parentChart.subscribeCrosshairMove(parentCrosshairHandler)
    childChart.subscribeCrosshairMove(childCrosshairHandler)
}