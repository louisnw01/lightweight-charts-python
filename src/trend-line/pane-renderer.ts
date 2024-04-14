import { ViewPoint } from "./pane-view";

import { CanvasRenderingTarget2D } from "fancy-canvas";
import { TwoPointDrawingPaneRenderer } from "../drawing/pane-renderer";
import { DrawingOptions } from "../drawing/options";
import { setLineStyle } from "../helpers/canvas-rendering";

export class TrendLinePaneRenderer extends TwoPointDrawingPaneRenderer {
    constructor(p1: ViewPoint, p2: ViewPoint, options: DrawingOptions, hovered: boolean) {
        super(p1, p2, options, hovered);
    }

    draw(target: CanvasRenderingTarget2D) {
        target.useBitmapCoordinateSpace(scope => {
            if (
                this._p1.x === null ||
                this._p1.y === null ||
                this._p2.x === null ||
                this._p2.y === null
            )
                return;
            const ctx = scope.context;

            const scaled = this._getScaledCoordinates(scope);
            if (!scaled) return;

            ctx.lineWidth = this._options.width;
            ctx.strokeStyle = this._options.lineColor;
            setLineStyle(ctx, this._options.lineStyle);
            ctx.beginPath();
            ctx.moveTo(scaled.x1, scaled.y1);
            ctx.lineTo(scaled.x2, scaled.y2);
            ctx.stroke();
            // this._drawTextLabel(scope, this._text1, x1Scaled, y1Scaled, true);
            // this._drawTextLabel(scope, this._text2, x2Scaled, y2Scaled, false);

            if (!this._hovered) return;
            this._drawEndCircle(scope, scaled.x1, scaled.y1);
            this._drawEndCircle(scope, scaled.x2, scaled.y2);
        });
    }
}