import typescript from '@rollup/plugin-typescript';
import terser from '@rollup/plugin-terser';

export default [
  {
    input: 'src/general/handler.ts',
    output: {
      file: 'dist/bundle.js',
      format: 'es',
    },
    external: ['lightweight-charts'],
    plugins: [
      typescript(),
      terser(),
    ],
  },
];
