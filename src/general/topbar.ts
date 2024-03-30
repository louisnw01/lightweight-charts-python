import { GlobalParams } from "./global-params";
import { Handler } from "./handler";

declare const window: GlobalParams

interface Widget {
    elem: HTMLDivElement;
    callbackName: string;
    intervalElements: HTMLButtonElement[];
    onItemClicked: Function;
}

export class TopBar {
    private _handler: Handler;
    public _div: HTMLDivElement;

    private left: HTMLDivElement;
    private right: HTMLDivElement;

    constructor(handler: Handler) {
        this._handler = handler;

        this._div = document.createElement('div');
        this._div.classList.add('topbar');

        const createTopBarContainer = (justification: string) => {
            const div = document.createElement('div')
            div.classList.add('topbar-container')
            div.style.justifyContent = justification
            this._div.appendChild(div)
            return div
        }
        this.left = createTopBarContainer('flex-start')
        this.right = createTopBarContainer('flex-end')
    }
    
    makeSwitcher(items: string[], defaultItem: string, callbackName: string, align='left') {
        const switcherElement = document.createElement('div');
        switcherElement.style.margin = '4px 12px'

        let activeItemEl: HTMLButtonElement;

        const createAndReturnSwitcherButton = (itemName: string) => {
            const button = document.createElement('button');
            button.classList.add('topbar-button');
            button.classList.add('switcher-button');
            button.style.margin = '0px 2px';
            button.innerText = itemName;

            if (itemName == defaultItem) {
                activeItemEl = button;
                button.classList.add('active-switcher-button');
            }

            const buttonWidth = TopBar.getClientWidth(button)
            button.style.minWidth = buttonWidth + 1 + 'px'
            button.addEventListener('click', () => widget.onItemClicked(button))

            switcherElement.appendChild(button);
            return button;
        }

        const widget: Widget = {
            elem: switcherElement,
            callbackName: callbackName,
            intervalElements: items.map(createAndReturnSwitcherButton),
            onItemClicked: (item: HTMLButtonElement) => {
                if (item == activeItemEl) return
                activeItemEl.classList.remove('active-switcher-button');
                item.classList.add('active-switcher-button');
                activeItemEl = item;
                window.callbackFunction(`${widget.callbackName}_~_${item.innerText}`);
            }
        }

        this.appendWidget(switcherElement, align, true)
        return widget
    }

    makeTextBoxWidget(text: string, align='left') {
        const textBox = document.createElement('div');
        textBox.classList.add('topbar-textbox');
        textBox.innerText = text
        this.appendWidget(textBox, align, true)
        return textBox
    }

    makeMenu(items: string[], activeItem: string, separator: boolean, callbackName: string, align='right') {
        let menu = document.createElement('div')
        menu.classList.add('topbar-menu');

        let menuOpen = false;
        items.forEach(text => {
            let button = this.makeButton(text, null, false, false)
            button.elem.addEventListener('click', () => {
                widget.elem.innerText = button.elem.innerText+' ↓'
                window.callbackFunction(`${callbackName}_~_${button.elem.innerText}`)
                menu.style.display = 'none'
                menuOpen = false
            });
            button.elem.style.margin = '4px 4px'
            button.elem.style.padding = '2px 2px'
            menu.appendChild(button.elem)
        })
        let widget =
            this.makeButton(activeItem+' ↓', null, separator, true, align)

        widget.elem.addEventListener('click', () => {
            menuOpen = !menuOpen
            if (!menuOpen) {
                menu.style.display = 'none';
                return;
            }
            let rect = widget.elem.getBoundingClientRect()
            menu.style.display = 'flex'
            menu.style.flexDirection = 'column'

            let center = rect.x+(rect.width/2)
            menu.style.left = center-(menu.clientWidth/2)+'px'
            menu.style.top = rect.y+rect.height+'px'
        })
        document.body.appendChild(menu)
    }

    makeButton(defaultText: string, callbackName: string | null, separator: boolean, append=true, align='left') {
        let button = document.createElement('button')
        button.classList.add('topbar-button');
        // button.style.color = window.pane.color
        button.innerText = defaultText;
        document.body.appendChild(button)
        button.style.minWidth = button.clientWidth+1+'px'
        document.body.removeChild(button)

        let widget = {
            elem: button,
            callbackName: callbackName
        }

        if (callbackName) {
            button.addEventListener('click', () => window.callbackFunction(`${widget.callbackName}_~_${button.innerText}`));
        }
        if (append) this.appendWidget(button, align, separator)
        return widget
    }

    makeSeparator(align='left') {
        const separator = document.createElement('div')
        separator.classList.add('topbar-seperator')
        const div = align == 'left' ? this.left : this.right
        div.appendChild(separator)
    }

    appendWidget(widget: HTMLElement, align: string, separator: boolean) {
        const div = align == 'left' ? this.left : this.right
        if (separator) {
            if (align == 'left') div.appendChild(widget)
            this.makeSeparator(align)
            if (align == 'right') div.appendChild(widget)
        } else div.appendChild(widget)
        this._handler.reSize();
    }

    private static getClientWidth(element: HTMLElement) {
        document.body.appendChild(element);
        const width = element.clientWidth;
        document.body.removeChild(element);
        return width;
    }
}


