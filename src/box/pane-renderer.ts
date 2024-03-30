import { ViewPoint } from "../drawing/pane-view";
import { CanvasRenderingTarget2D } from "fancy-canvas";
import { TwoPointDrawingPaneRenderer } from "../drawing/pane-renderer";
import { BoxOptions } from "./box";

export class BoxPaneRenderer extends TwoPointDrawingPaneRenderer {
    declare _options: BoxOptions;

	constructor(p1: ViewPoint, p2: ViewPoint, text1: string, text2: string, options: BoxOptions) {
		super(p1, p2, text1, text2, options)
	}

	draw(target: CanvasRenderingTarget2D) {
		target.useBitmapCoordinateSpace(scope => {
			
			const ctx = scope.context;

			const scaled = this._getScaledCoordinates(scope);

			if (!scaled) return;
			
			ctx.lineWidth = this._options.width;
			ctx.strokeStyle = this._options.lineColor;
            ctx.fillStyle = this._options.fillColor;

			const mainX = Math.min(scaled.x1, scaled.x2);
			const mainY = Math.min(scaled.y1, scaled.y2);
			const width = Math.abs(scaled.x1-scaled.x2);
			const height = Math.abs(scaled.y1-scaled.y2);
			
			ctx.strokeRect(mainX, mainY, width, height);
            ctx.fillRect(mainX, mainY, width, height);
			
			if (!this._options.showCircles) return;
			this._drawEndCircle(scope, mainX, mainY);
			this._drawEndCircle(scope, mainX+width, mainY);
			this._drawEndCircle(scope, mainX+width, mainY+height);
			this._drawEndCircle(scope, mainX, mainY+height);

		});
	}
}