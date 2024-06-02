import { Coordinate, ISeriesPrimitiveAxisView, PriceFormatBuiltIn } from 'lightweight-charts';
import { HorizontalLine } from './horizontal-line';

export class HorizontalLineAxisView implements ISeriesPrimitiveAxisView {
    _source: HorizontalLine;
    _y: Coordinate | null = null;
    _price: string | null = null;

    constructor(source: HorizontalLine) {
        this._source = source;
    }
    update() {
        if (!this._source.series || !this._source._point) return;
        this._y = this._source.series.priceToCoordinate(this._source._point.price);
        const priceFormat = this._source.series.options().priceFormat as PriceFormatBuiltIn;
        const precision = priceFormat.precision;
        this._price = this._source._point.price.toFixed(precision).toString();
    }
    visible() {
        return true;
    }
    tickVisible() {
        return true;
    }
    coordinate() {
        return this._y ?? 0;
    }
    text() {
        return this._source._options.text || this._price || '';
    }
    textColor() {
        return 'white';
    }
    backColor() {
        return this._source._options.lineColor;
    }
}
