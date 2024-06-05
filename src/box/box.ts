import {
    MouseEventParams,
} from 'lightweight-charts';

import { Point } from '../drawing/data-source';
import { InteractionState } from '../drawing/drawing';
import { DrawingOptions, defaultOptions } from '../drawing/options';
import { BoxPaneView } from './pane-view';
import { TwoPointDrawing } from '../drawing/two-point-drawing';


export interface BoxOptions extends DrawingOptions {
    fillEnabled: boolean;
    fillColor: string;
}

const defaultBoxOptions = {
    fillEnabled: true,
    fillColor: 'rgba(255, 255, 255, 0.2)',
    ...defaultOptions
}


export class Box extends TwoPointDrawing {
    _type = "Box";

    constructor(
        p1: Point,
        p2: Point,
        options?: Partial<BoxOptions>
    ) {
        super(p1, p2, options);
        this._options = {
            ...defaultBoxOptions,
            ...options,
        }
        this._paneViews = [new BoxPaneView(this)];
    }

    // autoscaleInfo(startTimePoint: Logical, endTimePoint: Logical): AutoscaleInfo | null {
        // const p1Index = this._pointIndex(this._p1);
        // const p2Index = this._pointIndex(this._p2);
        // if (p1Index === null || p2Index === null) return null;
        // if (endTimePoint < p1Index || startTimePoint > p2Index) return null;
        // return {
        //  priceRange: {
        //      minValue: this._minPrice,
        //      maxValue: this._maxPrice,
        //  },
        // };
    // }

    _moveToState(state: InteractionState) {
        switch(state) {
            case InteractionState.NONE:
                document.body.style.cursor = "default";
                this._hovered = false;
                this._unsubscribe("mousedown", this._handleMouseDownInteraction);
                break;

            case InteractionState.HOVERING:
                document.body.style.cursor = "pointer";
                this._hovered = true;
                this._unsubscribe("mouseup", this._handleMouseUpInteraction);
                this._subscribe("mousedown", this._handleMouseDownInteraction)
                this.chart.applyOptions({handleScroll: true});
                break;

            case InteractionState.DRAGGINGP1:
            case InteractionState.DRAGGINGP2:
            case InteractionState.DRAGGINGP3:
            case InteractionState.DRAGGINGP4:
            case InteractionState.DRAGGING:
                document.body.style.cursor = "grabbing";
                document.body.addEventListener("mouseup", this._handleMouseUpInteraction);
                this._subscribe("mouseup", this._handleMouseUpInteraction);
                this.chart.applyOptions({handleScroll: false});
                break;
        }
        this._state = state;
    }

     _onDrag(diff: any) {
        if (this._state == InteractionState.DRAGGING || this._state == InteractionState.DRAGGINGP1) {
            this._addDiffToPoint(this.p1, diff.logical, diff.price);
        }
        if (this._state == InteractionState.DRAGGING || this._state == InteractionState.DRAGGINGP2) {
            this._addDiffToPoint(this.p2, diff.logical, diff.price);
        }
        if (this._state != InteractionState.DRAGGING) {
            if (this._state == InteractionState.DRAGGINGP3) {
                this._addDiffToPoint(this.p1, diff.logical, 0);
                this._addDiffToPoint(this.p2, 0, diff.price);
            }
            if (this._state == InteractionState.DRAGGINGP4) {
                this._addDiffToPoint(this.p1, 0, diff.price);
                this._addDiffToPoint(this.p2, diff.logical, 0);
            }
        }
    }

    protected _onMouseDown() {
        this._startDragPoint = null;
        const hoverPoint = this._latestHoverPoint;
        const p1  = this._paneViews[0]._p1;
        const p2  = this._paneViews[0]._p2;

        if (!p1.x || !p2.x || !p1.y || !p2.y) return this._moveToState(InteractionState.DRAGGING);

        const tolerance = 10;
        if (Math.abs(hoverPoint.x-p1.x) < tolerance && Math.abs(hoverPoint.y-p1.y) < tolerance) {
            this._moveToState(InteractionState.DRAGGINGP1)
        }
        else if (Math.abs(hoverPoint.x-p2.x) < tolerance && Math.abs(hoverPoint.y-p2.y) < tolerance) {
            this._moveToState(InteractionState.DRAGGINGP2)
        }
        else if (Math.abs(hoverPoint.x-p1.x) < tolerance && Math.abs(hoverPoint.y-p2.y) < tolerance) {
            this._moveToState(InteractionState.DRAGGINGP3)
        }
        else if (Math.abs(hoverPoint.x-p2.x) < tolerance && Math.abs(hoverPoint.y-p1.y) < tolerance) {
            this._moveToState(InteractionState.DRAGGINGP4)
        }
        else {
            this._moveToState(InteractionState.DRAGGING);
        }
    }

    protected _mouseIsOverDrawing(param: MouseEventParams, tolerance = 4) {
        if (!param.point) return false;

        const x1 = this._paneViews[0]._p1.x;
        const y1 = this._paneViews[0]._p1.y;
        const x2 = this._paneViews[0]._p2.x;
        const y2 = this._paneViews[0]._p2.y;
        if (!x1 || !x2 || !y1 || !y2 ) return false;

        const mouseX = param.point.x;
        const mouseY = param.point.y;

        const mainX = Math.min(x1, x2);
        const mainY = Math.min(y1, y2);

        const width = Math.abs(x1-x2);
        const height = Math.abs(y1-y2);

        const halfTolerance = tolerance/2;

        return mouseX > mainX-halfTolerance && mouseX < mainX+width+halfTolerance &&
            mouseY > mainY-halfTolerance && mouseY < mainY+height+halfTolerance;
    }
}


