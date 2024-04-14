import { Box } from "../box/box";
import { HorizontalLine } from "../horizontal-line/horizontal-line";
import { RayLine } from "../horizontal-line/ray-line";
import { TrendLine } from "../trend-line/trend-line";
import { VerticalLine } from "../vertical-line/vertical-line";
import { Table } from "./table";

export interface GlobalParams extends Window {
    pane: paneStyle;    // TODO shouldnt need this cause of css variables
    handlerInFocus: string;
    callbackFunction: Function;
    containerDiv: HTMLElement;
    setCursor: Function;
    cursor: string;
    Handler: any;
    Table: typeof Table;

    HorizontalLine: typeof HorizontalLine;
    TrendLine: typeof TrendLine;
    Box: typeof Box;
    RayLine: typeof RayLine;
    VerticalLine: typeof VerticalLine;

}

interface paneStyle {
    backgroundColor: string;
    hoverBackgroundColor: string;
    clickBackgroundColor: string;
    activeBackgroundColor: string;
    mutedBackgroundColor: string;
    borderColor: string;
    color: string;
    activeColor: string;
}

export const paneStyleDefault: paneStyle = {
    backgroundColor: '#0c0d0f',
    hoverBackgroundColor: '#3c434c',
    clickBackgroundColor: '#50565E',
    activeBackgroundColor: 'rgba(0, 122, 255, 0.7)',
    mutedBackgroundColor: 'rgba(0, 122, 255, 0.3)',
    borderColor: '#3C434C',
    color: '#d8d9db',
    activeColor: '#ececed',
}

declare const window: GlobalParams;

export function globalParamInit() {
    window.pane = {
        ...paneStyleDefault,
    }
    window.containerDiv = document.getElementById("container") || document.createElement('div');
    window.setCursor = (type: string | undefined) => {
        if (type) window.cursor = type;
        document.body.style.cursor = window.cursor;
    }
    window.cursor = 'default';
    window.Table = Table;

    window.HorizontalLine = HorizontalLine;
    window.TrendLine = TrendLine;
    window.Box = Box;
    window.RayLine = RayLine;
    window.VerticalLine = VerticalLine;
}


// export interface SeriesHandler {
//     type: string;
//     series: ISeriesApi<SeriesType>;
//     markers: SeriesMarker<"">[],
//     horizontal_lines: HorizontalLine[],
//     name?: string,
//     precision: number,
// }

