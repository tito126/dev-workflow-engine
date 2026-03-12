import fs from 'node:fs';
const mod = await import('file:///D:/nvm/v24.9.0/node_modules/openclaw/node_modules/node-llama-cpp/dist/index.js');
const target = 'C:/Users/pc/.openclaw/memory-models/embeddinggemma-300m';
console.log('EXISTS', fs.existsSync(target));
console.log('IS_DIR', fs.existsSync(target) ? fs.statSync(target).isDirectory() : false);
if (fs.existsSync(target) && fs.statSync(target).isDirectory()) {
  console.log('FILES', fs.readdirSync(target).slice(0, 20));
}
const llama = await mod.getLlama({ logLevel: mod.LlamaLogLevel?.warn ?? 3 });
console.log('LLAMA_OK');
try {
  const resolved = await mod.resolveModelFile(target, {
    modelDownloader: true,
    dirPath: 'C:/Users/pc/.openclaw/memory-models'
  });
  console.log('RESOLVED', resolved);
} catch (e) {
  console.error('RESOLVE_FAIL', e?.stack || e?.message || e);
  process.exit(1);
}
