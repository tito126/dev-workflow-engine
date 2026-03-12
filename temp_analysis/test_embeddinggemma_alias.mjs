const mod = await import('file:///D:/nvm/v24.9.0/node_modules/openclaw/node_modules/node-llama-cpp/dist/index.js');
const llama = await mod.getLlama({ logLevel: mod.LlamaLogLevel?.warn ?? 3 });
console.log('LLAMA_OK');
for (const uri of ['embeddinggemma-300m', 'hf:ggml-org/embeddinggemma-300m-GGUF/embeddinggemma-300m.gguf']) {
  try {
    console.log('TRY', uri);
    const resolved = await mod.resolveModelFile(uri, {
      modelDownloader: true,
      dirPath: 'C:/Users/pc/.openclaw/memory-models'
    });
    console.log('RESOLVED', uri, resolved);
  } catch (e) {
    console.error('FAIL', uri, e?.message || e);
  }
}
