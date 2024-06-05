import { HorizontalLinePaneRenderer } from './pane-renderer';
import { HorizontalLine } from './horizontal-line';
import { DrawingPaneView, ViewPoint } from '../drawing/pane-view';


export class HorizontalLinePaneView extends DrawingPaneView {
    _source: HorizontalLine;
    _point: ViewPoint = {x: null, y: null};

    constructor(source: HorizontalLine) {
        super(source);
        this._source = source;
    }

    update() {
        const point = this._source._point;
        const timeScale = this._source.chart.timeScale()
        const series = this._source.series;
        if (this._source._type == "RayLine") {
            this._point.x = point.time ? timeScale.timeToCoordinate(point.time) : timeScale.logicalToCoordinate(point.logical);
        }
        this._point.y = series.priceToCoordinate(point.price);
    }

    renderer() {
        return new HorizontalLinePaneRenderer(
            this._point,
            this._source._options
        );
    }
}