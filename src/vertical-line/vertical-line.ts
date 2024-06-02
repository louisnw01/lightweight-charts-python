import {
    DeepPartial,
    MouseEventParams
} from "lightweight-charts";
import { Point } from "../drawing/data-source";
import { Drawing, InteractionState } from "../drawing/drawing";
import { DrawingOptions } from "../drawing/options";
import { VerticalLinePaneView } from "./pane-view";
import { GlobalParams } from "../general/global-params";
import { VerticalLineTimeAxisView } from "./axis-view";


declare const window: GlobalParams;

export class VerticalLine extends Drawing {
    _type = 'VerticalLine';
    _paneViews: VerticalLinePaneView[];
    _timeAxisViews: VerticalLineTimeAxisView[];
    _point: Point;
    private _callbackName: string | null;

    protected _startDragPoint: Point | null = null;

    constructor(point: Point, options: DeepPartial<DrawingOptions>, callbackName=null) {
        super(options)
        this._point = point;
        this._paneViews = [new VerticalLinePaneView(this)];
        this._callbackName = callbackName;

        this._timeAxisViews = [new VerticalLineTimeAxisView(this)]
    }

    updateAllViews() {
        this._paneViews.forEach(pw => pw.update());
        this._timeAxisViews.forEach(tw => tw.update());
    }

    timeAxisViews() {
        return this._timeAxisViews;
    }

    public updatePoints(...points: (Point | null)[]) {
        for (const p of points) {
            if (!p) continue;
            if (!p.time && p.logical) {
                p.time = this.series.dataByIndex(p.logical)?.time || null
            }
            this._point = p;
        }
        this.requestUpdate();
    }

    get points() {
        return [this._point];
    }

    _moveToState(state: InteractionState) {
        switch(state) {
            case InteractionState.NONE:
                document.body.style.cursor = "default";
                this._unsubscribe("mousedown", this._handleMouseDownInteraction);
                break;

            case InteractionState.HOVERING:
                document.body.style.cursor = "pointer";
                this._unsubscribe("mouseup", this._childHandleMouseUpInteraction);
                this._subscribe("mousedown", this._handleMouseDownInteraction)
                this.chart.applyOptions({handleScroll: true});
                break;

            case InteractionState.DRAGGING:
                document.body.style.cursor = "grabbing";
                this._subscribe("mouseup", this._childHandleMouseUpInteraction);
                this.chart.applyOptions({handleScroll: false});
                break;
        }
        this._state = state;
    }

    _onDrag(diff: any) {
        this._addDiffToPoint(this._point, diff.logical, 0);
        this.requestUpdate();
    }

    _mouseIsOverDrawing(param: MouseEventParams, tolerance = 4) {
        if (!param.point) return false;
        const timeScale = this.chart.timeScale()
        let x;
        if (this._point.time) {
            x = timeScale.timeToCoordinate(this._point.time);
        }
        else {
            x = timeScale.logicalToCoordinate(this._point.logical);
        }
        if (!x) return false;
        return (Math.abs(x-param.point.x) < tolerance);
    }

    protected _onMouseDown() {
        this._startDragPoint = null;
        const hoverPoint = this._latestHoverPoint;
        if (!hoverPoint) return;
        return this._moveToState(InteractionState.DRAGGING);
    }

    protected _childHandleMouseUpInteraction = () => {
        this._handleMouseUpInteraction();
        if (!this._callbackName) return;
        window.callbackFunction(`${this._callbackName}_~_${this._point.price.toFixed(8)}`);
    }
}