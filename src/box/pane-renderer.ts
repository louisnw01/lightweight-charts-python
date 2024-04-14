import { ViewPoint } from "../drawing/pane-view";
import { CanvasRenderingTarget2D } from "fancy-canvas";
import { TwoPointDrawingPaneRenderer } from "../drawing/pane-renderer";
import { BoxOptions } from "./box";
import { setLineStyle } from "../helpers/canvas-rendering";

export class BoxPaneRenderer extends TwoPointDrawingPaneRenderer {
    declare _options: BoxOptions;

    constructor(p1: ViewPoint, p2: ViewPoint, options: BoxOptions, showCircles: boolean) {
        super(p1, p2, options, showCircles)
    }

    draw(target: CanvasRenderingTarget2D) {
        target.useBitmapCoordinateSpace(scope => {

            const ctx = scope.context;

            const scaled = this._getScaledCoordinates(scope);

            if (!scaled) return;

            ctx.lineWidth = this._options.width;
            ctx.strokeStyle = this._options.lineColor;
            setLineStyle(ctx, this._options.lineStyle)
            ctx.fillStyle = this._options.fillColor;

            const mainX = Math.min(scaled.x1, scaled.x2);
            const mainY = Math.min(scaled.y1, scaled.y2);
            const width = Math.abs(scaled.x1-scaled.x2);
            const height = Math.abs(scaled.y1-scaled.y2);

            ctx.strokeRect(mainX, mainY, width, height);
            ctx.fillRect(mainX, mainY, width, height);

            if (!this._hovered) return;
            this._drawEndCircle(scope, mainX, mainY);
            this._drawEndCircle(scope, mainX+width, mainY);
            this._drawEndCircle(scope, mainX+width, mainY+height);
            this._drawEndCircle(scope, mainX, mainY+height);

        });
    }
}