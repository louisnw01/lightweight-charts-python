import { Drawing } from "../drawing/drawing";
import { DrawingOptions } from "../drawing/options";
import { GlobalParams } from "../general/global-params";

declare const window: GlobalParams;


export class ColorPicker {
    private static readonly colors = [
        '#EBB0B0','#E9CEA1','#E5DF80','#ADEB97','#A3C3EA','#D8BDED',
        '#E15F5D','#E1B45F','#E2D947','#4BE940','#639AE1','#D7A0E8',
        '#E42C2A','#E49D30','#E7D827','#3CFF0A','#3275E4','#B06CE3',
        '#F3000D','#EE9A14','#F1DA13','#2DFC0F','#1562EE','#BB00EF',
        '#B50911','#E3860E','#D2BD11','#48DE0E','#1455B4','#6E009F',
        '#7C1713','#B76B12','#8D7A13','#479C12','#165579','#51007E',
    ]

    public _div: HTMLDivElement;
    private saveDrawings: Function;

    private opacity: number = 0;
    private _opacitySlider: HTMLInputElement;
    private _opacityLabel: HTMLDivElement;
    private rgba: number[] | undefined;

    constructor(saveDrawings: Function,
        private colorOption: keyof DrawingOptions,
    ) {
        this.saveDrawings = saveDrawings

        this._div = document.createElement('div');
        this._div.classList.add('color-picker');

        let colorPicker = document.createElement('div')
        colorPicker.style.margin = '10px'
        colorPicker.style.display = 'flex'
        colorPicker.style.flexWrap = 'wrap'

        ColorPicker.colors.forEach((color) => colorPicker.appendChild(this.makeColorBox(color)))

        let separator = document.createElement('div')
        separator.style.backgroundColor = window.pane.borderColor
        separator.style.height = '1px'
        separator.style.width = '130px'

        let opacity = document.createElement('div')
        opacity.style.margin = '10px'

        let opacityText = document.createElement('div')
        opacityText.style.color = 'lightgray'
        opacityText.style.fontSize = '12px'
        opacityText.innerText = 'Opacity'

        this._opacityLabel = document.createElement('div')
        this._opacityLabel.style.color = 'lightgray'
        this._opacityLabel.style.fontSize = '12px'

        this._opacitySlider = document.createElement('input')
        this._opacitySlider.type = 'range'
        this._opacitySlider.value = (this.opacity*100).toString();
        this._opacityLabel.innerText = this._opacitySlider.value+'%'
        this._opacitySlider.oninput = () => {
            this._opacityLabel.innerText = this._opacitySlider.value+'%'
            this.opacity = parseInt(this._opacitySlider.value)/100
            this.updateColor()
        }

        opacity.appendChild(opacityText)
        opacity.appendChild(this._opacitySlider)
        opacity.appendChild(this._opacityLabel)

        this._div.appendChild(colorPicker)
        this._div.appendChild(separator)
        this._div.appendChild(opacity)
        window.containerDiv.appendChild(this._div)

    }

    private _updateOpacitySlider() {
        this._opacitySlider.value = (this.opacity*100).toString();
        this._opacityLabel.innerText = this._opacitySlider.value+'%';
    }

    makeColorBox(color: string) {
        const box = document.createElement('div')
        box.style.width = '18px'
        box.style.height = '18px'
        box.style.borderRadius = '3px'
        box.style.margin = '3px'
        box.style.boxSizing = 'border-box'
        box.style.backgroundColor = color

        box.addEventListener('mouseover', () => box.style.border = '2px solid lightgray')
        box.addEventListener('mouseout', () => box.style.border = 'none')

        const rgba = ColorPicker.extractRGBA(color)
        box.addEventListener('click', () => {
            this.rgba = rgba;
            this.updateColor();
        })
        return box
    }

    private static extractRGBA(anyColor: string) {
        const dummyElem = document.createElement('div');
        dummyElem.style.color = anyColor;
        document.body.appendChild(dummyElem);
        const computedColor = getComputedStyle(dummyElem).color;
        document.body.removeChild(dummyElem);
        const rgb = computedColor.match(/\d+/g)?.map(Number);
        if (!rgb) return [];
        let isRgba = computedColor.includes('rgba');
        let opacity = isRgba ? parseFloat(computedColor.split(',')[3]) : 1
        return [rgb[0], rgb[1], rgb[2], opacity]
    }

    updateColor() {
        if (!Drawing.lastHoveredObject || !this.rgba) return;
        const oColor = `rgba(${this.rgba[0]}, ${this.rgba[1]}, ${this.rgba[2]}, ${this.opacity})`
        Drawing.lastHoveredObject.applyOptions({[this.colorOption]: oColor})
        this.saveDrawings()
    }
    openMenu(rect: DOMRect) {
        if (!Drawing.lastHoveredObject) return;
        this.rgba = ColorPicker.extractRGBA(
            Drawing.lastHoveredObject._options[this.colorOption] as string
        )
        this.opacity = this.rgba[3];
        this._updateOpacitySlider();
        this._div.style.top = (rect.top-30)+'px'
        this._div.style.left = rect.right+'px'
        this._div.style.display = 'flex'

        setTimeout(() => document.addEventListener('mousedown', (event: MouseEvent) => {
            if (!this._div.contains(event.target as Node)) {
                this.closeMenu()
            }
        }), 10)
    }
    closeMenu() {
        document.body.removeEventListener('click', this.closeMenu)
        this._div.style.display = 'none'
    }
}