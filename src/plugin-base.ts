import {
	DataChangedScope,
	IChartApiBase,
	ISeriesApi,
	ISeriesPrimitive,
	SeriesAttachedParameter,
	SeriesOptionsMap,
	Time,
} from 'lightweight-charts';
import { ensureDefined } from './helpers/assertions';

//* PluginBase is a useful base to build a plugin upon which
//* already handles creating getters for the chart and series,
//* and provides a requestUpdate method.
export abstract class PluginBase implements ISeriesPrimitive<Time> {
	private _chart: IChartApiBase<Time> | undefined = undefined;
	private _series: ISeriesApi<keyof SeriesOptionsMap> | undefined = undefined;

	protected dataUpdated?(scope: DataChangedScope): void;
	protected requestUpdate(): void {
		if (this._requestUpdate) this._requestUpdate();
	}
	private _requestUpdate?: () => void;

	// Arrow function so `this` is always bound correctly when used as a callback
	private _fireDataUpdated = (scope: DataChangedScope) => {
		if (this.dataUpdated) {
			this.dataUpdated(scope);
		}
	};

	public attached({
		chart,
		series,
		requestUpdate,
	}: SeriesAttachedParameter<Time>) {
		this._chart = chart;
		this._series = series;
		this._series.subscribeDataChanged(this._fireDataUpdated);
		this._requestUpdate = requestUpdate;
		this.requestUpdate();
	}

	public detached() {
		this._series?.unsubscribeDataChanged(this._fireDataUpdated);
		this._chart = undefined;
		this._series = undefined;
		this._requestUpdate = undefined;
	}

	public get chart(): IChartApiBase<Time> {
		return ensureDefined(this._chart);
	}

	public get series(): ISeriesApi<keyof SeriesOptionsMap> {
		return ensureDefined(this._series);
	}
}
