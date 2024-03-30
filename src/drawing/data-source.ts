import {
    IChartApi,
    ISeriesApi,
    Logical,
    SeriesOptionsMap,
    Time,
} from 'lightweight-charts';

import { DrawingOptions } from './options';

export interface Point {
    time: Time | null;
    logical: Logical;
    price: number;
}

export interface DrawingDataSource {
    chart: IChartApi;
    series: ISeriesApi<keyof SeriesOptionsMap>;
    options: DrawingOptions;
    p1: Point;
    p2: Point;
}
