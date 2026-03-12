const mod = await import('file:///D:/nvm/v24.9.0/node_modules/openclaw/node_modules/node-llama-cpp/dist/index.js');
const llama = await mod.getLlama({ logLevel: mod.LlamaLogLevel?.warn ?? 3 });
console.log('LLAMA_OK');
const uri = 'hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf';
console.log('RESOLVE_START', uri);
const resolved = await mod.resolveModelFile(uri, {
  modelDownloader: true,
  dirPath: 'C:/Users/pc/.openclaw/memory-models'
});
console.log('RESOLVE_OK', resolved);
