import {
    ISeriesApi,
    Logical,
    MouseEventParams,
    SeriesType
} from 'lightweight-charts';

import { PluginBase } from '../plugin-base';
import { DiffPoint, Point } from './data-source';
import { DrawingOptions, defaultOptions } from './options';
import { DrawingPaneView } from './pane-view';

export enum InteractionState {
    NONE,
    HOVERING,
    DRAGGING,
    DRAGGINGP1,
    DRAGGINGP2,
    DRAGGINGP3,
    DRAGGINGP4,
}

export abstract class Drawing extends PluginBase {
    _paneViews: DrawingPaneView[] = [];
    _options: DrawingOptions;

    abstract _type: string;
    protected _points: (Point|null)[] = [];

    protected _state: InteractionState = InteractionState.NONE;

    protected _startDragPoint: Point | null = null;
    protected _latestHoverPoint: any | null = null;

    protected static _mouseIsDown: boolean = false;

    public static hoveredObject: Drawing | null = null;
    public static lastHoveredObject: Drawing | null = null;

    protected _listeners: any[] = [];

    constructor(
        options?: Partial<DrawingOptions>
    ) {
        super()
        this._options = {
            ...defaultOptions,
            ...options,
        };
    }

    updateAllViews() {
        this._paneViews.forEach(pw => pw.update());
    }

    paneViews() {
        return this._paneViews;
    }

    applyOptions(options: Partial<DrawingOptions>) {
        this._options = {
            ...this._options,
            ...options,
        }
        this.requestUpdate();
    }

    public updatePoints(...points: (Point | null)[]) {
        for (let i=0; i<this.points.length; i++) {
            if (points[i] == null) continue;
            this.points[i] = points[i] as Point;
        }
        this.requestUpdate();
    }

    detach() {
        this._options.lineColor = 'transparent';
        this.requestUpdate();
        this.series.detachPrimitive(this);
        for (const s of this._listeners) {
            document.body.removeEventListener(s.name, s.listener);
        }

    }

    get points() {
        return this._points;
    }

    protected _subscribe(name: keyof DocumentEventMap, listener: any) {
        document.body.addEventListener(name, listener);
        this._listeners.push({name: name, listener: listener});
    }

    protected _unsubscribe(name: keyof DocumentEventMap, callback: any) {
        document.body.removeEventListener(name, callback);

        const toRemove = this._listeners.find((x) => x.name === name && x.listener === callback)
        this._listeners.splice(this._listeners.indexOf(toRemove), 1);
    }

    _handleHoverInteraction(param: MouseEventParams) {
        this._latestHoverPoint = param.point;
        if (Drawing._mouseIsDown) {
            this._handleDragInteraction(param);
        } else {
            if (this._mouseIsOverDrawing(param)) {
                if (this._state != InteractionState.NONE) return;
                this._moveToState(InteractionState.HOVERING);
                Drawing.hoveredObject = Drawing.lastHoveredObject = this;
            } else {
                if (this._state == InteractionState.NONE) return;
                this._moveToState(InteractionState.NONE);
                if (Drawing.hoveredObject === this) Drawing.hoveredObject = null;
            }
        }
    }

    public static _eventToPoint(param: MouseEventParams, series: ISeriesApi<SeriesType>) {
        if (!series || !param.point || !param.logical) return null;
        const barPrice = series.coordinateToPrice(param.point.y);
        if (barPrice == null) return null;
        return {
            time: param.time || null,
            logical: param.logical,
            price: barPrice.valueOf(),
        }
    }

    protected static _getDiff(p1: Point, p2: Point): DiffPoint {
        const diff: DiffPoint = {
            logical: p1.logical-p2.logical,
            price: p1.price-p2.price,
        }
        return diff;
    }

    protected _addDiffToPoint(point: Point | null, logicalDiff: number, priceDiff: number) {
        if (!point) return;
        point.logical = point.logical + logicalDiff as Logical;
        point.price = point.price+priceDiff;
        point.time = this.series.dataByIndex(point.logical)?.time || null;
    }

    protected _handleMouseDownInteraction = () => {
        // if (Drawing._mouseIsDown) return;
        Drawing._mouseIsDown = true;
        this._onMouseDown();
    }

    protected _handleMouseUpInteraction = () => {
        // if (!Drawing._mouseIsDown) return;
        Drawing._mouseIsDown = false;
        this._moveToState(InteractionState.HOVERING);
    }

    private _handleDragInteraction(param: MouseEventParams): void {
        if (this._state != InteractionState.DRAGGING &&
            this._state != InteractionState.DRAGGINGP1 &&
            this._state != InteractionState.DRAGGINGP2 &&
            this._state != InteractionState.DRAGGINGP3 &&
            this._state != InteractionState.DRAGGINGP4) {
            return;
        }
        const mousePoint = Drawing._eventToPoint(param, this.series);
        if (!mousePoint) return;
        this._startDragPoint = this._startDragPoint || mousePoint;

        const diff = Drawing._getDiff(mousePoint, this._startDragPoint);
        this._onDrag(diff);
        this.requestUpdate();

        this._startDragPoint = mousePoint;
    }

    protected abstract _onMouseDown(): void;
    protected abstract _onDrag(diff: DiffPoint): void;
    protected abstract _moveToState(state: InteractionState): void;
    protected abstract _mouseIsOverDrawing(param: MouseEventParams): boolean;
}
