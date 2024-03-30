import { LineStyle } from "lightweight-charts";

export interface DrawingOptions {
	lineColor: string;
	lineStyle: LineStyle
	width: number;
	showLabels: boolean;
	showCircles: boolean,
}


export const defaultOptions: DrawingOptions = {
	lineColor: 'rgb(255, 255, 255)',
	lineStyle: LineStyle.Solid,
	width: 4,
	showLabels: true,
	showCircles: false,
};