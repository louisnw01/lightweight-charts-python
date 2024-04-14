import { CanvasRenderingTarget2D } from "fancy-canvas";
import { DrawingOptions } from "../drawing/options";
import { DrawingPaneRenderer } from "../drawing/pane-renderer";
import { ViewPoint } from "../drawing/pane-view";
import { setLineStyle } from "../helpers/canvas-rendering";

export class VerticalLinePaneRenderer extends DrawingPaneRenderer {
    _point: ViewPoint = {x: null, y: null};

    constructor(point: ViewPoint, options: DrawingOptions) {
        super(options);
        this._point = point;
    }

    draw(target: CanvasRenderingTarget2D) {
        target.useBitmapCoordinateSpace(scope => {
            if (this._point.x == null) return;
            const ctx = scope.context;
            const scaledX = this._point.x * scope.horizontalPixelRatio;

            ctx.lineWidth = this._options.width;
            ctx.strokeStyle = this._options.lineColor;
            setLineStyle(ctx, this._options.lineStyle);

            ctx.beginPath();
            ctx.moveTo(scaledX, 0);
            ctx.lineTo(scaledX, scope.bitmapSize.height);
            ctx.stroke();
        });
    }

}