const mod = await import('file:///D:/nvm/v24.9.0/node_modules/openclaw/node_modules/node-llama-cpp/dist/index.js');
console.log('IMPORT_OK', Object.keys(mod).slice(0, 20));
if (typeof mod.getLlama !== 'function') {
  console.error('NO_GET_LLAMA');
  process.exit(2);
}
console.log('GET_LLAMA_START');
const llama = await mod.getLlama({ logLevel: mod.LlamaLogLevel?.warn ?? 3 });
console.log('GET_LLAMA_OK', !!llama);
