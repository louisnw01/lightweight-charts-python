if (!window.Table) {
    class Table {
        constructor(width, height, headings, widths, alignments, position, draggable = false) {
            this.container = document.createElement('div')
            this.callbackName = null

            if (draggable) {
                this.container.style.position = 'absolute'
                this.container.style.cursor = 'move'
            } else {
                this.container.style.position = 'relative'
                this.container.style.float = position
            }

            this.container.style.zIndex = '2000'
            this.container.style.width = width <= 1 ? width * 100 + '%' : width + 'px'
            this.container.style.height = height <= 1 ? height * 100 + '%' : height + 'px'
            this.container.style.display = 'flex'
            this.container.style.flexDirection = 'column'
            this.container.style.justifyContent = 'space-between'

            this.container.style.backgroundColor = '#121417'
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
                row.appendChild(th)
                th.style.border = '1px solid rgb(70, 70, 70)'
            }

            let overflowWrapper = document.createElement('div')
            overflowWrapper.style.overflow = 'auto'
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

        newRow(vals, id) {
            let row = this.table.insertRow()
            row.style.cursor = 'default'

            for (let i = 0; i < vals.length; i++) {
                row[this.headings[i]] = row.insertCell()
                row[this.headings[i]].textContent = vals[i]
                row[this.headings[i]].style.width = this.widths[i];
                row[this.headings[i]].style.textAlign = this.alignments[i];
                row[this.headings[i]].style.border = '1px solid rgb(70, 70, 70)'

            }
            row.addEventListener('mouseover', () => row.style.backgroundColor = 'rgba(60, 60, 60, 0.6)')
            row.addEventListener('mouseout', () => row.style.backgroundColor = 'transparent')
            row.addEventListener('mousedown', () => row.style.backgroundColor = 'rgba(60, 60, 60)')

            row.addEventListener('click', () => window.callbackFunction(`${this.callbackName}_~_${id}`))
            row.addEventListener('mouseup', () => row.style.backgroundColor = 'rgba(60, 60, 60, 0.6)')

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

        makeFooter(numBoxes) {
            let footer = document.createElement('div')
            footer.style.display = 'flex'
            footer.style.width = '100%'
            footer.style.padding = '3px 0px'
            footer.style.backgroundColor = 'rgb(30, 30, 30)'
            this.container.appendChild(footer)

            this.footer = []
            for (let i = 0; i < numBoxes; i++) {
                this.footer.push(document.createElement('div'))
                footer.appendChild(this.footer[i])
                this.footer[i].style.flex = '1'
                this.footer[i].style.textAlign = 'center'
            }
        }
    }
    window.Table = Table
}
