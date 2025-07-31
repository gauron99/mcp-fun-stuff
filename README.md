# mcp-fun-stuff

# Fun stuff related to Kn-Functions and MCP

Implementations of MCP and integrating MCP into Knative Functions

- using [python-sdk](https://github.com/modelcontextprotocol/python-sdk)

## Directories explained
- `initial` contains some initial MCP efforts using python-sdk lib with a function
integrating this mcp
- `mc-lama-mash` contains mash of ollama and mcp creating mcp server as a function
which exposes ollama inference model as one of it's tools. You can communicate
with the MCP server (function) via MCP client (this can be further moved into
having MCP client as another function and you could communicate w/ that function)

## General How to use
- This might not apply exactly to all the directories
- install python venv
- pip install requirements.txt if available (usually just `mcp`,`ollama`)
- choose a function/project
- either:
    - run `python main.py` or similar in non-functions dir
    - run `func deploy` or `func run` if in a functions dir
- optionally
    - port-forward your function (pod) if in cluster.
    eg: `kubectl port-forward <pod name in cluster> 8080:8080`
- Run the client to connect
    - run `client.py` to communicate with the MCP server

