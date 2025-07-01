import logging
import json
import asyncio
import mcp
from mcp.server.models import InitializationOptions
from mcp.server.fastmcp import FastMCP

from middleware import serve

# new function
def new():
    return Function()

class MCPServer:
    def __init__(self):
        print("MCPServer init")
        # Create FastMCP instance with all our tools, resources, and prompts
        self.mcp = FastMCP("super cool mcp server")
        
        # Define tools using the decorator
        @self.mcp.tool()
        def hello_tool(name: str) -> str:
            """Say hello to someone"""
            return f"Hey there {name}!"
        
        @self.mcp.tool()
        def add_numbers(a: int, b: int) -> int:
            """Add two numbers together"""
            return a + b
        
        # Define a resource
        @self.mcp.resource("echo://{message}")
        def echo_resource(message: str) -> str:
            """Echo the message as a resource"""
            return f"Echo: {message}"
        
        # Define a prompt
        @self.mcp.prompt()
        def greeting_prompt(name: str = "World"):
            """Generate a greeting prompt"""
            return [
                {
                    "role": "user",
                    "content": f"Please write a friendly greeting for {name}"
                }
            ]
        
        # Get the streamable HTTP app from FastMCP
        # This creates a Starlette app with /mcp mount point
        self._starlette_app = self.mcp.streamable_http_app()

    async def handle_mcp_requests(self, scope, receive, send):
        """Forward requests to the FastMCP streamable HTTP app"""
        # The streamable_http_app() returns a Starlette app that expects
        # to handle the full ASGI interface
        await self._starlette_app(scope, receive, send)
    
# Function
class Function:
    def __init__(self):
        """
        initialize MCP server
        """
        self.mcp_server = MCPServer()

    async def handle(self, scope, receive, send): # pyright: ignore
        """ Handle all HTTP requests to this Function other than readiness
        and liveness probes."""

        logging.info(f"OK: Request Received for path: {scope['path']}")
        
        # Route MCP requests to the MCP server
        # The FastMCP streamable_http_app has its own routing,
        # so we pass all /mcp* requests to it
        if scope['path'].startswith('/mcp'):
            print(f"scope starts with /mcp, path: {scope['path']}")
            await self.mcp_server.handle_mcp_requests(scope, receive, send)
            return

        # echo the request to the calling client
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'text/plain'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': 'OK'.encode(),
        })

    def start(self, cfg):
        """ start is an optional method which is called when a new Function
        instance is started, such as when scaling up or during an update.
        Provided is a dictionary containing all environmental configuration.
        Args:
            cfg (Dict[str, str]): A dictionary containing environmental config.
                In most cases this will be a copy of os.environ, but it is
                best practice to use this cfg dict instead of os.environ.
        """
        logging.info("Function starting")

    def stop(self):
        """ stop is an optional method which is called when a function is
        stopped, such as when scaled down, updated, or manually canceled.  Stop
        can block while performing function shutdown/cleanup operations.  The
        process will eventually be killed if this method blocks beyond the
        platform's configured maximum studown timeout.
        """
        logging.info("Function stopping")

###############################################################################
###############################################################################

if __name__ == "__main__":
    print("Start")
    serve(new)