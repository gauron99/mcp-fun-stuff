# mcp-fun-stuff

# Fun stuff related to Kn-Functions and MCP

Implementations of MCP and integrating MCP into Knative Functions

- using [python-sdk](https://github.com/modelcontextprotocol/python-sdk)

## dir structure explained
- mcp-only - contains mcp server/client (no func)
    - contains streamable-http and stdio style communication for MCP
- asgi - contains Function-like code without it being run like a Function
    - local - basic implementation of MCP server/client
    - standard - uses func-python middleware
    - dev - contains bunch of testing/debug code on top
- functions - contains actuall depoyable MCP server as a Function

## how to use
- install python venv
- pip install requirements.txt if available (usually just `mcp`)
- choose a function/project
- either:
    - run `python main.py` or similar in non-functions dir
    - run `func deploy` or `func run` using host builder
- port-forward your function
    - eg: `kubectl port-forward <pod name in cluster> 8080:8080`
- run `client.py` to communicate with the MCP server

> [!Note]
> If desired, getting `mcp`, `hypercorn`, `asyncio`, `logging` and 
> `knative-extensions/func-python.git` 
> (`pip install git+https://github.com/knative-extensions/func-python.git`)
> should suffice for any.
