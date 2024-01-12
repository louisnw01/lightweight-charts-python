if (!window.Table) {
    class Table {
        constructor(width, height, headings, widths, alignments, position, draggable = false,
                    tableBackgroundColor, borderColor, borderWidth, textColors, backgroundColors) {
            this.container = document.createElement('div')
            this.callbackName = null
            this.borderColor = borderColor
            this.borderWidth = borderWidth

            if (draggable) {
                this.container.style.position = 'absolute'
                this.container.style.cursor = 'move'
            } else {
                this.container.style.position = 'relative'
                this.container.style.float = position
            }
            this.container.style.zIndex = '2000'
            this.reSize(width, height)
            this.container.style.display = 'flex'
            this.container.style.flexDirection = 'column'
            // this.container.style.justifyContent = 'space-between'

            this.container.style.borderRadius = '5px'
            this.container.style.color = 'white'
            this.container.style.fontSize = '12px'
            this.container.style.fontVariantNumeric = 'tabular-nums'

            this.table = document.createElement('table')
            this.table.style.width = '100%'
            this.table.style.borderCollapse = 'collapse'
            this.container.style.overflow = 'hidden'

            this.rows = {}

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
            this.container.appendChild(overflowWrapper)
            document.getElementById('wrapper').appendChild(this.container)

            if (!draggable) return

            let offsetX, offsetY;

            this.onMouseDown = (event) => {
                offsetX = event.clientX - this.container.offsetLeft;
                offsetY = event.clientY - this.container.offsetTop;

                document.addEventListener('mousemove', onMouseMove);
                document.addEventListener('mouseup', onMouseUp);
            }

            let onMouseMove = (event) => {
                this.container.style.left = (event.clientX - offsetX) + 'px';
                this.container.style.top = (event.clientY - offsetY) + 'px';
            }

            let onMouseUp = () => {
                // Remove the event listeners for dragging
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            }

            this.container.addEventListener('mousedown', this.onMouseDown);


        }

        divToButton(div, callbackString) {
            div.addEventListener('mouseover', () => div.style.backgroundColor = 'rgba(60, 60, 60, 0.6)')
            div.addEventListener('mouseout', () => div.style.backgroundColor = 'transparent')
            div.addEventListener('mousedown', () => div.style.backgroundColor = 'rgba(60, 60, 60)')
            div.addEventListener('click', () => window.callbackFunction(callbackString))
            div.addEventListener('mouseup', () => div.style.backgroundColor = 'rgba(60, 60, 60, 0.6)')
        }

        newRow(id, returnClickedCell=false) {
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
                row[this.headings[i]] = cell
            }
            if (!returnClickedCell) {
                this.divToButton(row, `${this.callbackName}_~_${id}`)
            }
            this.rows[id] = row
        }

        deleteRow(id) {
            this.table.deleteRow(this.rows[id].rowIndex)
            delete this.rows[id]
        }

        clearRows() {
            let numRows = Object.keys(this.rows).length
            for (let i = 0; i < numRows; i++)
                this.table.deleteRow(-1)
            this.rows = {}
        }

        updateCell(rowId, column, val) {
            this.rows[rowId][column].textContent = val
        }

        makeSection(id, type, numBoxes, func=false) {
            let section = document.createElement('div')
            section.style.display = 'flex'
            section.style.width = '100%'
            section.style.padding = '3px 0px'
            section.style.backgroundColor = 'rgb(30, 30, 30)'
            type === 'footer' ? this.container.appendChild(section) : this.container.prepend(section)

            this[type] = []
            for (let i = 0; i < numBoxes; i++) {
                let textBox = document.createElement('div')
                section.appendChild(textBox)
                textBox.style.flex = '1'
                textBox.style.textAlign = 'center'
                if (func) {
                    this.divToButton(textBox, `${id}_~_${i}`)
                    textBox.style.borderRadius = '2px'
                }
                this[type].push(textBox)
            }
        }

        reSize(width, height) {
            this.container.style.width = width <= 1 ? width * 100 + '%' : width + 'px'
            this.container.style.height = height <= 1 ? height * 100 + '%' : height + 'px'
        }
    }
    window.Table = Table
}
