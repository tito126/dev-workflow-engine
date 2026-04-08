const esbuild = require('esbuild')

esbuild.build({
  entryPoints: ['src/cli.ts'],
  bundle: true,
  platform: 'node',
  target: 'node18',
  format: 'cjs',
  outfile: 'dist/cli.js',
  banner: { js: '#!/usr/bin/env node' },
  minify: false,
  sourcemap: false
}).then(() => {
  console.log('Build complete: dist/cli.js')
})
