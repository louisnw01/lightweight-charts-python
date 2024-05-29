import typescript from '@rollup/plugin-typescript';
import terser from '@rollup/plugin-terser';

export default [
  {
    input: 'src/index.ts',
    output: {
      file: 'dist/bundle.js',
      format: 'iife',
      name: 'Lib',
      globals: {
        'lightweight-charts': 'LightweightCharts'
      },
    },
    external: ['lightweight-charts'],
    plugins: [
      typescript(),
      terser(),
    ],
  },
];
