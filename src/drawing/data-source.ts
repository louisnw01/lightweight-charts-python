import {
    Logical,
    Time,
} from 'lightweight-charts';

export interface Point {
    time: Time | null;
    logical: Logical;
    price: number;
}

export interface DiffPoint {
    logical: number;
    price: number;
}
