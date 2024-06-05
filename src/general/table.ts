import { GlobalParams } from "./global-params";

declare const window: GlobalParams


interface RowDictionary {
    [key: number]: HTMLTableRowElement;
}


export class Table {
    private _div: HTMLDivElement;
    private callbackName: string | null;

    private borderColor: string;
    private borderWidth: number;
    private table: HTMLTableElement;
    private rows: RowDictionary = {};
    private headings: string[];
    private widths: string[];
    private alignments: string[];

    public footer: HTMLDivElement[] | undefined;
    public header: HTMLDivElement[] | undefined;

    constructor(width: number, height: number, headings: string[], widths: number[], alignments: string[], position: string, draggable = false,
                tableBackgroundColor: string, borderColor: string, borderWidth: number, textColors: string[], backgroundColors: string[]) {
        this._div = document.createElement('div')
        this.callbackName = null
        this.borderColor = borderColor
        this.borderWidth = borderWidth

        if (draggable) {
            this._div.style.position = 'absolute'
            this._div.style.cursor = 'move'
        } else {
            this._div.style.position = 'relative'
            this._div.style.float = position
        }
        this._div.style.zIndex = '2000'
        this.reSize(width, height)
        this._div.style.display = 'flex'
        this._div.style.flexDirection = 'column'
        // this._div.style.justifyContent = 'space-between'

        this._div.style.borderRadius = '5px'
        this._div.style.color = 'white'
        this._div.style.fontSize = '12px'
        this._div.style.fontVariantNumeric = 'tabular-nums'

        this.table = document.createElement('table')
        this.table.style.width = '100%'
        this.table.style.borderCollapse = 'collapse'
        this._div.style.overflow = 'hidden';

        this.headings = headings
        this.widths = widths.map((width) => `${width * 100}%`)
        this.alignments = alignments

        let head = this.table.createTHead()
        let row = head.insertRow()

        for (let i = 0; i < this.headings.length; i++) {
            let th = document.createElement('th')
            th.textContent = this.headings[i]
            th.style.width = this.widths[i]
            th.style.letterSpacing = '0.03rem'
            th.style.padding = '0.2rem 0px'
            th.style.fontWeight = '500'
            th.style.textAlign = 'center'
            if (i !== 0) th.style.borderLeft = borderWidth+'px solid '+borderColor
            th.style.position = 'sticky'
            th.style.top = '0'
            th.style.backgroundColor = backgroundColors.length > 0 ? backgroundColors[i] : tableBackgroundColor
            th.style.color = textColors[i]
            row.appendChild(th)
        }

        let overflowWrapper = document.createElement('div')
        overflowWrapper.style.overflowY = 'auto'
        overflowWrapper.style.overflowX = 'hidden'
        overflowWrapper.style.backgroundColor = tableBackgroundColor
        overflowWrapper.appendChild(this.table)
        this._div.appendChild(overflowWrapper)
        window.containerDiv.appendChild(this._div)

        if (!draggable) return

        let offsetX: number, offsetY: number;

        let onMouseDown = (event: MouseEvent) => {
            offsetX = event.clientX - this._div.offsetLeft;
            offsetY = event.clientY - this._div.offsetTop;

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        }

        let onMouseMove = (event: MouseEvent) => {
            this._div.style.left = (event.clientX - offsetX) + 'px';
            this._div.style.top = (event.clientY - offsetY) + 'px';
        }

        let onMouseUp = () => {
            // Remove the event listeners for dragging
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        }

        this._div.addEventListener('mousedown', onMouseDown);
    }

    divToButton(div: HTMLDivElement, callbackString: string) {
        div.addEventListener('mouseover', () => div.style.backgroundColor = 'rgba(60, 60, 60, 0.6)')
        div.addEventListener('mouseout', () => div.style.backgroundColor = 'transparent')
        div.addEventListener('mousedown', () => div.style.backgroundColor = 'rgba(60, 60, 60)')
        div.addEventListener('click', () => window.callbackFunction(callbackString))
        div.addEventListener('mouseup', () => div.style.backgroundColor = 'rgba(60, 60, 60, 0.6)')
    }

    newRow(id: number, returnClickedCell=false) {
        let row = this.table.insertRow()
        row.style.cursor = 'default'

        for (let i = 0; i < this.headings.length; i++) {
            let cell = row.insertCell()
            cell.style.width = this.widths[i];
            cell.style.textAlign = this.alignments[i];
            cell.style.border = this.borderWidth+'px solid '+this.borderColor
            if (returnClickedCell) {
                this.divToButton(cell, `${this.callbackName}_~_${id};;;${this.headings[i]}`)
            }
        }
        if (!returnClickedCell) {
            this.divToButton(row, `${this.callbackName}_~_${id}`)
        }
        this.rows[id] = row
    }

    deleteRow(id: number) {
        this.table.deleteRow(this.rows[id].rowIndex)
        delete this.rows[id]
    }

    clearRows() {
        let numRows = Object.keys(this.rows).length
        for (let i = 0; i < numRows; i++)
            this.table.deleteRow(-1)
        this.rows = {}
    }

    private _getCell(rowId: number, column: string) {
        return this.rows[rowId].cells[this.headings.indexOf(column)];
    }

    updateCell(rowId: number, column: string, val: string) {
        this._getCell(rowId, column).textContent = val;
    }

    styleCell(rowId: number, column: string, styleAttribute: string, value: string) {
        const style = this._getCell(rowId, column).style;
        (style as any)[styleAttribute] = value;
    }

    makeSection(id: string, type: string, numBoxes: number, func=false) {
        let section = document.createElement('div')
        section.style.display = 'flex'
        section.style.width = '100%'
        section.style.padding = '3px 0px'
        section.style.backgroundColor = 'rgb(30, 30, 30)'
        type === 'footer' ? this._div.appendChild(section) : this._div.prepend(section)

        const textBoxes = []
        for (let i = 0; i < numBoxes; i++) {
            let textBox = document.createElement('div')
            section.appendChild(textBox)
            textBox.style.flex = '1'
            textBox.style.textAlign = 'center'
            if (func) {
                this.divToButton(textBox, `${id}_~_${i}`)
                textBox.style.borderRadius = '2px'
            }
            textBoxes.push(textBox)
        }

        if (type === 'footer') {
            this.footer = textBoxes;
        }
        else {
            this.header = textBoxes;
        }

    }

    reSize(width: number, height: number) {
        this._div.style.width = width <= 1 ? width * 100 + '%' : width + 'px'
        this._div.style.height = height <= 1 ? height * 100 + '%' : height + 'px'
    }
}
