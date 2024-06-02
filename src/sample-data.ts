import type { Time, } from 'lightweight-charts';

type LineData = {
	time: Time;
	value: number;
};

export type CandleData = {
	time: Time;
	high: number;
	low: number;
	close: number;
	open: number;
};

let randomFactor = 25 + Math.random() * 25;
const samplePoint = (i: number) =>
	i *
		(0.5 +
			Math.sin(i / 10) * 0.2 +
			Math.sin(i / 20) * 0.4 +
			Math.sin(i / randomFactor) * 0.8 +
			Math.sin(i / 500) * 0.5) +
	200;

export function generateLineData(numberOfPoints: number = 500): LineData[] {
	randomFactor = 25 + Math.random() * 25;
	const res = [];
	const date = new Date(Date.UTC(2018, 0, 1, 12, 0, 0, 0));
	for (let i = 0; i < numberOfPoints; ++i) {
		const time = (date.getTime() / 1000) as Time;
		const value = samplePoint(i);
		res.push({
			time,
			value,
		});

		date.setUTCDate(date.getUTCDate() + 1);
	}

	return res;
}

export function generateCandleData(numberOfPoints: number = 250): CandleData[] {
	const lineData = generateLineData(numberOfPoints);
	return lineData.map((d, i) => {
		const randomRanges = [-1 * Math.random(), Math.random(), Math.random()].map(
			j => j * 10
		);
		const sign = Math.sin(Math.random() - 0.5);
		return {
			time: d.time,
			low: d.value + randomRanges[0],
			high: d.value + randomRanges[1],
			open: d.value + sign * randomRanges[2],
			close: samplePoint(i + 1),
		};
	});
}