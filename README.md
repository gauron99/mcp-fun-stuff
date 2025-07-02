# mcp-fun-stuff

# Fun stuff related to Kn-Functions and MCP

Implementations of MCP and integrating MCP into Knative Functions

- using (python-sdk)[https://github.com/modelcontextprotocol/python-sdk]

## dir explanations
- local - basic implementation of MCP server/client (stdio comms)
- http - basic impl of MCP server/client (streamable-http comms)
- asgi - local integration of MCP into Function
    - python middleware is simply copy&pasted into `middleware.py`

