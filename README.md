# mcp-fun-stuff

# Fun stuff related to Kn-Functions and MCP

Implementations of MCP and integrating MCP into Knative Functions

- using [python-sdk](https://github.com/modelcontextprotocol/python-sdk)

## dir explanations
- mcp-only - contains mcp server/client (no func)
    - contains streamable-http and stdio style communication for MCP
- asgi - contains Function-like code without it being run like a Function
    - local - basic implementation of MCP server/client
    - standard - uses func-python middleware
    - dev - contains bunch of testing/debug code on top
- functions - contains actuall depoyable MCP server as a Function
