function makeSearchBox(chart, callbackFunction) {
    let searchWindow = document.createElement('div')
    searchWindow.style.position = 'absolute'
    searchWindow.style.top = '0'
    searchWindow.style.bottom = '200px'
    searchWindow.style.left = '0'
    searchWindow.style.right = '0'
    searchWindow.style.margin = 'auto'
    searchWindow.style.width = '150px'
    searchWindow.style.height = '30px'
    searchWindow.style.padding = '10px'
    searchWindow.style.backgroundColor = 'rgba(30, 30, 30, 0.9)'
    searchWindow.style.border = '2px solid #3C434C'
    searchWindow.style.zIndex = '1000'
    searchWindow.style.display = 'none'
    searchWindow.style.borderRadius = '5px'

    let magnifyingGlass = document.createElement('span');
    magnifyingGlass.style.display = 'inline-block';
    magnifyingGlass.style.width = '12px';
    magnifyingGlass.style.height = '12px';
    magnifyingGlass.style.border = '2px solid rgb(240, 240, 240)';
    magnifyingGlass.style.borderRadius = '50%';
    magnifyingGlass.style.position = 'relative';
    let handle = document.createElement('span');
    handle.style.display = 'block';
    handle.style.width = '7px';
    handle.style.height = '2px';
    handle.style.backgroundColor = 'rgb(240, 240, 240)';
    handle.style.position = 'absolute';
    handle.style.top = 'calc(50% + 7px)';
    handle.style.right = 'calc(50% - 11px)';
    handle.style.transform = 'rotate(45deg)';

    let sBox = document.createElement('input');
    sBox.type = 'text';
    sBox.style.position = 'relative';
    sBox.style.display = 'inline-block';
    sBox.style.zIndex = '1000';
    sBox.style.textAlign = 'center'
    sBox.style.width = '100px'
    sBox.style.marginLeft = '15px'
    sBox.style.backgroundColor = 'rgba(0, 122, 255, 0.3)'
    sBox.style.color = 'rgb(240,240,240)'
    sBox.style.fontSize = '20px'
    sBox.style.border = 'none'
    sBox.style.outline = 'none'
    sBox.style.borderRadius = '2px'

    searchWindow.appendChild(magnifyingGlass)
    magnifyingGlass.appendChild(handle)
    searchWindow.appendChild(sBox)
    chart.div.appendChild(searchWindow);

    let yPrice = null
    chart.chart.subscribeCrosshairMove((param) => {
        if (param.point){
            yPrice = param.point.y;
        }
    });
    let selectedChart = true
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

            let colorList = [
                'rgba(228, 0, 16, 0.7)',
                'rgba(255, 133, 34, 0.7)',
                'rgba(164, 59, 176, 0.7)',
                'rgba(129, 59, 102, 0.7)',
                'rgba(91, 20, 248, 0.7)',
                'rgba(32, 86, 249, 0.7)',
            ]
            let color = colorList[Math.floor(Math.random()*colorList.length)]

            makeHorizontalLine(chart, 0, price, color, 2, LightweightCharts.LineStyle.Solid, true, '')
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
    return {
        window: searchWindow,
        box: sBox,
    }
}

function makeSpinner(chart) {
    chart.spinner = document.createElement('div')
    chart.spinner.style.width = '30px'
    chart.spinner.style.height = '30px'
    chart.spinner.style.border = '4px solid rgba(255, 255, 255, 0.6)'
    chart.spinner.style.borderTop = '4px solid rgba(0, 122, 255, 0.8)'
    chart.spinner.style.borderRadius = '50%'
    chart.spinner.style.position = 'absolute'
    chart.spinner.style.top = '50%'
    chart.spinner.style.left = '50%'
    chart.spinner.style.zIndex = 1000
    chart.spinner.style.transform = 'translate(-50%, -50%)'
    chart.spinner.style.display = 'none'
    chart.wrapper.appendChild(chart.spinner)
    let rotation = 0;
    const speed = 10; // Adjust this value to change the animation speed
    function animateSpinner() {
        rotation += speed
        chart.spinner.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`
        requestAnimationFrame(animateSpinner)
    }
    animateSpinner();
}
function makeSwitcher(chart, items, activeItem, callbackFunction, callbackName, activeBackgroundColor, activeColor, inactiveColor, hoverColor) {
    let switcherElement = document.createElement('div');
    switcherElement.style.margin = '4px 14px'
    switcherElement.style.zIndex = '1000'

    let intervalElements = items.map(function(item) {
        let itemEl = document.createElement('button');
        itemEl.style.cursor = 'pointer'
        itemEl.style.padding = '2px 5px'
        itemEl.style.margin = '0px 4px'
        itemEl.style.fontSize = '13px'
        itemEl.style.backgroundColor = item === activeItem ? activeBackgroundColor : 'transparent'
        itemEl.style.color = item === activeItem ? activeColor : inactiveColor
        itemEl.style.border = 'none'
        itemEl.style.borderRadius = '4px'

        itemEl.addEventListener('mouseenter', function() {
            itemEl.style.backgroundColor = item === activeItem ? activeBackgroundColor : hoverColor
            itemEl.style.color = activeColor
        })
        itemEl.addEventListener('mouseleave', function() {
            itemEl.style.backgroundColor = item === activeItem ? activeBackgroundColor : 'transparent'
            itemEl.style.color = item === activeItem ? activeColor : inactiveColor
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
            element.style.backgroundColor = items[index] === item ? activeBackgroundColor : 'transparent'
            element.style.color = items[index] === item ? 'activeColor' : inactiveColor
        });
        activeItem = item;
        callbackFunction(`${callbackName}__${chart.id}__${item}`);
    }
    chart.topBar.appendChild(switcherElement)
    makeSeperator(chart.topBar)
    return switcherElement;
}

function makeTextBoxWidget(chart, text) {
    let textBox = document.createElement('div')
    textBox.style.margin = '0px 18px'
    textBox.style.position = 'relative'
    textBox.style.fontSize = '16px'
    textBox.style.color = 'rgb(220, 220, 220)'
    textBox.innerText = text
    chart.topBar.append(textBox)
    makeSeperator(chart.topBar)
    return textBox
}
function makeTopBar(chart) {
    chart.topBar = document.createElement('div')
    chart.topBar.style.backgroundColor = '#191B1E'
    chart.topBar.style.borderBottom = '2px solid #3C434C'
    chart.topBar.style.display = 'flex'
    chart.topBar.style.alignItems = 'center'
    chart.wrapper.prepend(chart.topBar)
}

function makeSeperator(topBar) {
    let seperator = document.createElement('div')
        seperator.style.width = '1px'
        seperator.style.height = '20px'
        seperator.style.backgroundColor = '#3C434C'
        topBar.appendChild(seperator)
    }


