import {
    DeepPartial,
    MouseEventParams
} from "lightweight-charts";
import { Point } from "../drawing/data-source";
import { Drawing, InteractionState } from "../drawing/drawing";
import { DrawingOptions } from "../drawing/options";
import { HorizontalLinePaneView } from "./pane-view";

export class HorizontalLine extends Drawing {
    _type = 'HorizontalLine';
    _paneViews: HorizontalLinePaneView[];
    _point: Point;

    protected _startDragPoint: Point | null = null;

    constructor(point: Point, options: DeepPartial<DrawingOptions>) {
        super(options)
        this._point = point;
        this._point.time = null;    // time is null for horizontal lines
        this._paneViews = [new HorizontalLinePaneView(this)];

        // TODO ids should be stored in an object dictionary so u can access the lines
        // this.handler.horizontal_lines.push(this) TODO fix this in handler ?
    }

    public updatePoints(...points: (Point | null)[]) {
        for (const p of points) if (p) this._point.price = p.price;
        this.requestUpdate();
    }

    _moveToState(state: InteractionState) {
        switch(state) {
            case InteractionState.NONE:
                document.body.style.cursor = "default";
                this._unsubscribe("mousedown", this._handleMouseDownInteraction);
                break;

            case InteractionState.HOVERING:
                document.body.style.cursor = "pointer";
                this._unsubscribe("mouseup", this._handleMouseUpInteraction);
                this._subscribe("mousedown", this._handleMouseDownInteraction)
                this.chart.applyOptions({handleScroll: true});
                break;

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
        Drawing._addDiffToPoint(this._point, 0, 0, diff.price);
        this.requestUpdate();
    }

    _mouseIsOverDrawing(param: MouseEventParams, tolerance = 4) {
        if (!param.point) return false;
        const y = this.series.priceToCoordinate(this._point.price);
        if (!y) return false;
        return (Math.abs(y-param.point.y) < tolerance);
    }

    protected _onMouseDown() {
        this._startDragPoint = null;
        const hoverPoint = this._latestHoverPoint;
        if (!hoverPoint) return;
        return this._moveToState(InteractionState.DRAGGING);
    }
}