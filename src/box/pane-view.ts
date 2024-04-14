import { Box, BoxOptions } from './box';
import { BoxPaneRenderer } from './pane-renderer';
import { TwoPointDrawingPaneView } from '../drawing/pane-view';

export class BoxPaneView extends TwoPointDrawingPaneView {
    constructor(source: Box) {
        super(source)
    }

    renderer() {
        return new BoxPaneRenderer(
            this._p1,
            this._p2,
            this._source._options as BoxOptions,
            this._source.hovered,
        );
    }
}