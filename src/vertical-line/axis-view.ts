import { Coordinate, ISeriesPrimitiveAxisView } from "lightweight-charts";
import { VerticalLine } from "./vertical-line";

export class VerticalLineTimeAxisView implements ISeriesPrimitiveAxisView {
    _source: VerticalLine;
    _x: Coordinate | null = null;

    constructor(source: VerticalLine) {
        this._source = source;
    }
    update() {
        if (!this._source.chart|| !this._source._point) return;
        const point = this._source._point;
        const timeScale = this._source.chart.timeScale();
        this._x = point.time ? timeScale.timeToCoordinate(point.time) : timeScale.logicalToCoordinate(point.logical);
    }
    visible() {
        return !!this._source._options.text;
    }
    tickVisible() {
        return true;
    }
    coordinate() {
        return this._x ?? 0;
    }
    text() {
        return this._source._options.text || '';
    }
    textColor() {
        return "white";
    }
    backColor() {
        return this._source._options.lineColor;
    }
}