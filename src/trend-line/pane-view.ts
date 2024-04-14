import { Coordinate, } from 'lightweight-charts';
import { TrendLine } from './trend-line';
import { TrendLinePaneRenderer } from './pane-renderer';
import { TwoPointDrawingPaneView } from '../drawing/pane-view';

export interface ViewPoint {
    x: Coordinate | null;
    y: Coordinate | null;
}

export class TrendLinePaneView extends TwoPointDrawingPaneView {
    constructor(source: TrendLine) {
        super(source)
    }

    renderer() {
        return new TrendLinePaneRenderer(
            this._p1,
            this._p2,
            this._source._options,
            this._source.hovered,
        );
    }
}