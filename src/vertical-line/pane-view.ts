import { VerticalLinePaneRenderer } from './pane-renderer';
import { VerticalLine } from './vertical-line';
import { DrawingPaneView, ViewPoint } from '../drawing/pane-view';


export class VerticalLinePaneView extends DrawingPaneView {
    _source: VerticalLine;
    _point: ViewPoint = {x: null, y: null};

    constructor(source: VerticalLine) {
        super(source);
        this._source = source;
    }

    update() {
        const point = this._source._point;
        const timeScale = this._source.chart.timeScale()
        const series = this._source.series;
        this._point.x = point.time ? timeScale.timeToCoordinate(point.time) : timeScale.logicalToCoordinate(point.logical)
        this._point.y = series.priceToCoordinate(point.price);
    }

    renderer() {
        return new VerticalLinePaneRenderer(
            this._point,
            this._source._options
        );
    }
}