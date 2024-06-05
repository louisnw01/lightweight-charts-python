import { LineStyle } from "lightweight-charts";

export function setLineStyle(ctx: CanvasRenderingContext2D, style: LineStyle): void {
    const dashPatterns = {
        [LineStyle.Solid]: [],
        [LineStyle.Dotted]: [ctx.lineWidth, ctx.lineWidth],
        [LineStyle.Dashed]: [2 * ctx.lineWidth, 2 * ctx.lineWidth],
        [LineStyle.LargeDashed]: [6 * ctx.lineWidth, 6 * ctx.lineWidth],
        [LineStyle.SparseDotted]: [ctx.lineWidth, 4 * ctx.lineWidth],
    };

    const dashPattern = dashPatterns[style];
    ctx.setLineDash(dashPattern);
}