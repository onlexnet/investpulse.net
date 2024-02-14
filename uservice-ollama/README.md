# How to use ollama

To test some smaller models, use [ollama](https://ollama.ai/library)

e.g. 
```
ollama run orca2
```

##
Quick test if ollama is working / reachable
```
export OLLAMA_HOST=172.29.228.228
curl http://$OLLAMA_HOST:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Why is the sky blue?"
}'
```

## Random hints
[Jupyter notebook vscode shortcuts](https://github.com/microsoft/vscode-jupyter/issues/4376)
