function makeSearchBox(chart) {
    let searchWindow = document.createElement('div')
    searchWindow.style.position = 'absolute'
    searchWindow.style.top = '0'
    searchWindow.style.bottom = '200px'
    searchWindow.style.left = '0'
    searchWindow.style.right = '0'
    searchWindow.style.margin = 'auto'
    searchWindow.style.width = '150px'
    searchWindow.style.height = '30px'
    searchWindow.style.padding = '5px'
    searchWindow.style.zIndex = '1000'
    searchWindow.style.alignItems = 'center'
    searchWindow.style.alignItems = 'center'
    searchWindow.style.backgroundColor = 'rgba(30, 30, 30, 0.9)'
    searchWindow.style.border = '2px solid #3C434C'
    searchWindow.style.borderRadius = '5px'
    searchWindow.style.display = 'none'

    let magnifyingGlass = document.createElement('div');
    magnifyingGlass.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="24px" height="24px" viewBox="0 0 24 24" version="1.1"><path style="fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;stroke:lightgray;stroke-opacity:1;stroke-miterlimit:4;" d="M 15 15 L 21 21 M 10 17 C 6.132812 17 3 13.867188 3 10 C 3 6.132812 6.132812 3 10 3 C 13.867188 3 17 6.132812 17 10 C 17 13.867188 13.867188 17 10 17 Z M 10 17 "/></svg>`

    let sBox = document.createElement('input');
    sBox.type = 'text';
    sBox.style.textAlign = 'center'
    sBox.style.width = '100px'
    sBox.style.marginLeft = '10px'
    sBox.style.backgroundColor = 'rgba(0, 122, 255, 0.3)'
    sBox.style.color = 'rgb(240,240,240)'
    sBox.style.fontSize = '20px'
    sBox.style.border = 'none'
    sBox.style.outline = 'none'
    sBox.style.borderRadius = '2px'

    searchWindow.appendChild(magnifyingGlass)
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
    chart.commandFunctions.push((event) => {
        if (!selectedChart) return
        if (searchWindow.style.display === 'none') {
            if (/^[a-zA-Z0-9]$/.test(event.key)) {
                searchWindow.style.display = 'flex';
                sBox.focus();
                return true
            }
            else return false
        }
        else if (event.key === 'Enter') {
            chart.callbackFunction(`on_search_~_${chart.id}_~_${sBox.value}`)
            searchWindow.style.display = 'none'
            sBox.value = ''
            return true
        }
        else if (event.key === 'Escape') {
            searchWindow.style.display = 'none'
            sBox.value = ''
            return true
        }
        else return false
    })
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
    chart.spinner.style.zIndex = '1000'
    chart.spinner.style.transform = 'translate(-50%, -50%)'
    chart.spinner.style.display = 'none'
    chart.wrapper.appendChild(chart.spinner)
    let rotation = 0;
    const speed = 10;
    function animateSpinner() {
        rotation += speed
        chart.spinner.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`
        requestAnimationFrame(animateSpinner)
    }
    animateSpinner();
}

function makeSwitcher(chart, items, activeItem, callbackName, activeBackgroundColor, activeColor, inactiveColor, hoverColor) {
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
        chart.callbackFunction(`${callbackName}_~_${chart.id}_~_${item}`);
    }
    chart.topBar.appendChild(switcherElement)
    makeSeperator(chart.topBar)
    return switcherElement;
}

function makeTextBoxWidget(chart, text) {
    let textBox = document.createElement('div')
    textBox.style.margin = '0px 18px'
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
