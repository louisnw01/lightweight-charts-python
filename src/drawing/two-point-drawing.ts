import { Point } from './data-source';
import { DrawingOptions, defaultOptions } from './options';
import { Drawing } from './drawing';
import { TwoPointDrawingPaneView } from './pane-view';


export abstract class TwoPointDrawing extends Drawing {
	_p1: Point;
	_p2: Point;
	_paneViews: TwoPointDrawingPaneView[] = [];

	constructor(
		p1: Point,
		p2: Point,
		options?: Partial<DrawingOptions>
	) {
		super()
		this._p1 = p1;
		this._p2 = p2;
		this._options = {
			...defaultOptions,
			...options,
		};
	}

	setFirstPoint(point: Point) {
		this.updatePoints(point);
	}

	setSecondPoint(point: Point) {
		this.updatePoints(null, point);
	}

	public updatePoints(...points: (Point|null)[]) {
		this._p1 = points[0] || this._p1;
		this._p2 = points[1] || this._p2;
		this.requestUpdate();
	}
}
