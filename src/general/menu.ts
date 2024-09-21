import { GlobalParams } from "./global-params";

declare const window: GlobalParams

export class Menu {
    private div: HTMLDivElement;
    private isOpen: boolean = false;
    private widget: any;

    constructor(
        private makeButton: Function,
        private callbackName: string,
        items: string[],
        activeItem: string,
        separator: boolean,
        align: 'right'|'left') {

        this.div = document.createElement('div')
        this.div.classList.add('topbar-menu');

        this.widget = this.makeButton(activeItem+' ↓', null, separator, true, align)

        this.updateMenuItems(items)

        this.widget.elem.addEventListener('click', () => {
            this.isOpen = !this.isOpen;
            if (!this.isOpen) {
                this.div.style.display = 'none';
                return;
            }
            let rect = this.widget.elem.getBoundingClientRect()
            this.div.style.display = 'flex'
            this.div.style.flexDirection = 'column'

            let center = rect.x+(rect.width/2)
            this.div.style.left = center-(this.div.clientWidth/2)+'px'
            this.div.style.top = rect.y+rect.height+'px'
        })
        document.body.appendChild(this.div)
    }

    updateMenuItems(items: string[]) {
        this.div.innerHTML = '';

        items.forEach(text => {
            let button = this.makeButton(text, null, false, false)
            button.elem.addEventListener('click', () => {
                this._clickHandler(button.elem.innerText);
            });
            button.elem.style.margin = '4px 4px'
            button.elem.style.padding = '2px 2px'
            this.div.appendChild(button.elem)
        })
        this.widget.elem.innerText = items[0]+' ↓';
    }
    
    private _clickHandler(name: string) {
        this.widget.elem.innerText = name+' ↓'
        window.callbackFunction(`${this.callbackName}_~_${name}`)
        this.div.style.display = 'none'
        this.isOpen = false
    }
}