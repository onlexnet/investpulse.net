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

## run all tests
```bash
pytest -v
```

## Concepts

Key components:
- strategy - keep current state, uses market indicators to create buy / sell commands
- market_agent: driven by strategy commands to buys / sells assets using the best price, and emits events when assets are sold / buyed. The events are consumed by strategy to update ots internal state
- 

## Random hints
[Jupyter notebook vscode shortcuts](https://github.com/microsoft/vscode-jupyter/issues/4376)
[praw](https://pypi.org/project/praw/) - use to analyze sentiment from reddit r/wallstreetbets
