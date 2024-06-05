import { GlobalParams } from "./global-params";
import { Handler } from "./handler";
import { Menu } from "./menu";

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

    makeTextBoxWidget(text: string, align='left', callbackName=null) {
        if (callbackName) {
            const textBox = document.createElement('input');
            textBox.classList.add('topbar-textbox-input');
            textBox.value = text
            textBox.style.width = `${(textBox.value.length+2)}ch`
            textBox.addEventListener('focus', () => {
                window.textBoxFocused = true;
            })
            textBox.addEventListener('input', (e) => {
                e.preventDefault();
                textBox.style.width = `${(textBox.value.length+2)}ch`;
            });
            textBox.addEventListener('keydown', (e) => {
                if (e.key == 'Enter') {
                    e.preventDefault();
                    textBox.blur();
                }
            });
            textBox.addEventListener('blur', () => {
                window.callbackFunction(`${callbackName}_~_${textBox.value}`)
                window.textBoxFocused = false;
            });
            this.appendWidget(textBox, align, true)
            return textBox
        } else {
            const textBox = document.createElement('div');
            textBox.classList.add('topbar-textbox');
            textBox.innerText = text
            this.appendWidget(textBox, align, true)
            return textBox
        }
    }

    makeMenu(items: string[], activeItem: string, separator: boolean, callbackName: string, align: 'right'|'left') {
        return new Menu(this.makeButton.bind(this), callbackName, items, activeItem, separator, align)
    }

    makeButton(defaultText: string, callbackName: string | null, separator: boolean, append=true, align='left', toggle=false) {
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
            let handler;
            if (toggle) {
                let state = false;
                handler = () => {
                    state = !state
                    window.callbackFunction(`${widget.callbackName}_~_${state}`)
                    button.style.backgroundColor = state ? 'var(--active-bg-color)' : '';
                    button.style.color = state ? 'var(--active-color)' : '';
                }
            } else {
                handler = () => window.callbackFunction(`${widget.callbackName}_~_${button.innerText}`)
            }
            button.addEventListener('click', handler);
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


