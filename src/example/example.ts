import { generateCandleData } from '../sample-data';
import { Handler } from '../general/handler';

const handler = new Handler("sadasdas", 0.556, 0.5182, "left", true);

handler.createToolBox();

const data = generateCandleData();
if (handler.series)
handler.series.setData(data);





