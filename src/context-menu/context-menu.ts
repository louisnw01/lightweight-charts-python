import { Drawing } from "../drawing/drawing";
import { GlobalParams } from "../general/global-params";

interface Item {
    elem: HTMLSpanElement;
    action: Function;
    closeAction: Function | null;
}

declare const window: GlobalParams;


export class ContextMenu {
    private div: HTMLDivElement
    private hoverItem: Item | null;

    constructor() {
        this._onRightClick = this._onRightClick.bind(this);
        this.div = document.createElement('div');
        this.div.classList.add('context-menu');
        document.body.appendChild(this.div);
        this.hoverItem = null;
        document.body.addEventListener('contextmenu', this._onRightClick);
    }

    _handleClick = (ev: MouseEvent) => this._onClick(ev);

    private _onClick(ev: MouseEvent) {
        if (!ev.target) return;
        if (!this.div.contains(ev.target as Node)) {
            this.div.style.display = 'none';
            document.body.removeEventListener('click', this._handleClick);
        }
    }

    private _onRightClick(ev: MouseEvent) {
        if (!Drawing.hoveredObject) return;
        ev.preventDefault();
        this.div.style.left = ev.clientX + 'px';
        this.div.style.top = ev.clientY + 'px';
        this.div.style.display = 'block';
        document.body.addEventListener('click', this._handleClick);
    }

    public menuItem(text: string, action: Function, hover: Function | null = null) {
        const item = document.createElement('span');
        item.classList.add('context-menu-item');
        this.div.appendChild(item);

        const elem = document.createElement('span');
        elem.innerText = text;
        elem.style.pointerEvents = 'none';
        item.appendChild(elem);

        if (hover) {
            let arrow = document.createElement('span')
            arrow.innerText = `►`
            arrow.style.fontSize = '8px'
            arrow.style.pointerEvents = 'none'
            item.appendChild(arrow)
        }

        item.addEventListener('mouseover', () => {
            if (this.hoverItem && this.hoverItem.closeAction) this.hoverItem.closeAction()
            this.hoverItem = {elem: elem, action: action, closeAction: hover}
        })
        if (!hover) item.addEventListener('click', (event) => {action(event); this.div.style.display = 'none'})
        else {
            let timeout: number;
            item.addEventListener('mouseover', () => timeout = setTimeout(() => action(item.getBoundingClientRect()), 100))
            item.addEventListener('mouseout', () => clearTimeout(timeout))
        }
    }
    public separator() {
        const separator = document.createElement('div')
        separator.style.width = '90%'
        separator.style.height = '1px'
        separator.style.margin = '3px 0px'
        separator.style.backgroundColor = window.pane.borderColor
        this.div.appendChild(separator)
    }

}
