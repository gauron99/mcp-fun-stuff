from fastmcp import FastMCP

mcp = FastMCP("My supercool local server")

@mcp.tool()
def hello(name: str) -> str:
    """ Say hello to my little friend """
    return f"Howdy {name}!"

if __name__ == "__main__":
    mcp.run()

