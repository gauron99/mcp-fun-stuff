# server.py -- Streamable http transport

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My supercool awesome MCP server",port="8080")

@mcp.tool()
def hello(name: str) -> str:
    """ Say hello to my little friend """
    return f"Howdy {name}!"

@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """ Echo the message as a resource"""
    return f"Resource echo: {message}"

@mcp.prompt()
def echo_bot_hello(): # pyright: ignore[reportAny]
    return hello("Billy_the_bot") # pyright: ignore[reportAny]

if __name__ == "__main__":
    mcp.run(transport="streamable-http")

