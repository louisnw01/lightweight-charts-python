if (!window.TopBar) {
    class TopBar {
        constructor(chart, hoverBackgroundColor, clickBackgroundColor, activeBackgroundColor, textColor, activeTextColor) {
            this.makeSwitcher = this.makeSwitcher.bind(this)
            this.hoverBackgroundColor = hoverBackgroundColor
            this.clickBackgroundColor = clickBackgroundColor
            this.activeBackgroundColor = activeBackgroundColor
            this.textColor = textColor
            this.activeTextColor = activeTextColor

            this.topBar = document.createElement('div')
            this.topBar.style.backgroundColor = '#0c0d0f'
            this.topBar.style.borderBottom = '2px solid #3C434C'
            this.topBar.style.display = 'flex'
            this.topBar.style.alignItems = 'center'
            chart.wrapper.prepend(this.topBar)
            chart.topBar = this.topBar
            this.reSize = () => chart.reSize()
            this.reSize()
        }
        makeSwitcher(items, activeItem, callbackName) {
            let switcherElement = document.createElement('div');
            switcherElement.style.margin = '4px 12px'
            let widget = {
                elem: switcherElement,
                callbackName: callbackName,
            }
            let intervalElements = items.map((item)=> {
                let itemEl = document.createElement('button');
                itemEl.style.border = 'none'
                itemEl.style.padding = '2px 5px'
                itemEl.style.margin = '0px 2px'
                itemEl.style.fontSize = '13px'
                itemEl.style.borderRadius = '4px'
                itemEl.style.backgroundColor = item === activeItem ? this.activeBackgroundColor : 'transparent'
                itemEl.style.color = item === activeItem ? this.activeTextColor : this.textColor
                itemEl.innerText = item;
                document.body.appendChild(itemEl)
                itemEl.style.minWidth = itemEl.clientWidth + 1 + 'px'
                document.body.removeChild(itemEl)

                itemEl.addEventListener('mouseenter', () => itemEl.style.backgroundColor = item === activeItem ? this.activeBackgroundColor : this.hoverBackgroundColor)
                itemEl.addEventListener('mouseleave', () => itemEl.style.backgroundColor = item === activeItem ? this.activeBackgroundColor : 'transparent')
                itemEl.addEventListener('mousedown', () => itemEl.style.backgroundColor = item === activeItem ? this.activeBackgroundColor : this.clickBackgroundColor)
                itemEl.addEventListener('mouseup', () => itemEl.style.backgroundColor = item === activeItem ? this.activeBackgroundColor : this.hoverBackgroundColor)
                itemEl.addEventListener('click', () => onItemClicked(item))

                switcherElement.appendChild(itemEl);
                return itemEl;
            });
            widget.intervalElements = intervalElements

            let onItemClicked = (item)=> {
                if (item === activeItem) return
                intervalElements.forEach((element, index) => {
                    element.style.backgroundColor = items[index] === item ? this.activeBackgroundColor : 'transparent'
                    element.style.color = items[index] === item ? this.activeTextColor : this.textColor
                    element.style.fontWeight = items[index] === item ? '500' : 'normal'
                })
                activeItem = item;
                window.callbackFunction(`${widget.callbackName}_~_${item}`);
            }

            this.topBar.appendChild(switcherElement)
            this.makeSeparator(this.topBar)
            this.reSize()
            return widget
        }
        makeTextBoxWidget(text) {
            let textBox = document.createElement('div')
            textBox.style.margin = '0px 18px'
            textBox.style.fontSize = '16px'
            textBox.style.color = 'rgb(220, 220, 220)'
            textBox.innerText = text
            this.topBar.append(textBox)
            this.makeSeparator(this.topBar)
            this.reSize()
            return textBox
        }
        makeButton(defaultText, callbackName, separator) {
            let button = document.createElement('button')
            button.style.border = 'none'
            button.style.padding = '2px 5px'
            button.style.margin = '4px 18px'
            button.style.fontSize = '13px'
            button.style.backgroundColor = 'transparent'
            button.style.color = this.textColor
            button.style.borderRadius = '4px'
            button.innerText = defaultText;
            document.body.appendChild(button)
            button.style.minWidth = button.clientWidth+1+'px'
            document.body.removeChild(button)

            let widget = {
                elem: button,
                callbackName: callbackName
            }

            button.addEventListener('mouseenter', () => button.style.backgroundColor = this.hoverBackgroundColor)
            button.addEventListener('mouseleave', () => button.style.backgroundColor = 'transparent')
            button.addEventListener('click', () => window.callbackFunction(`${widget.callbackName}_~_${button.innerText}`));
            button.addEventListener('mousedown', () => {
                button.style.backgroundColor = this.activeBackgroundColor
                button.style.color = this.activeTextColor
                button.style.fontWeight = '500'
            })
            button.addEventListener('mouseup', () => {
                button.style.backgroundColor = this.hoverBackgroundColor
                button.style.color = this.textColor
                button.style.fontWeight = 'normal'
            })
            if (separator) this.makeSeparator()
            this.topBar.appendChild(button)
            this.reSize()
            return widget
        }

        makeSeparator() {
            let seperator = document.createElement('div')
            seperator.style.width = '1px'
            seperator.style.height = '20px'
            seperator.style.backgroundColor = '#3C434C'
            this.topBar.appendChild(seperator)
        }
    }
    window.TopBar = TopBar
}

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
        if (param.point) yPrice = param.point.y;
    })
    window.selectedChart = chart
    chart.wrapper.addEventListener('mouseover', (event) => window.selectedChart = chart)
    chart.commandFunctions.push((event) => {
        if (selectedChart !== chart) return false
        if (searchWindow.style.display === 'none') {
            if (/^[a-zA-Z0-9]$/.test(event.key)) {
                searchWindow.style.display = 'flex';
                sBox.focus();
                return true
            }
            else return false
        }
        else if (event.key === 'Enter' || event.key === 'Escape') {
            if (event.key === 'Enter') window.callbackFunction(`search${chart.id}_~_${sBox.value}`)
            searchWindow.style.display = 'none'
            sBox.value = ''
            return true
        }
        else return false
    })
    sBox.addEventListener('input', () => sBox.value = sBox.value.toUpperCase())
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


