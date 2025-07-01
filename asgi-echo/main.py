import logging
import json
import asyncio
import mcp
from mcp.server.models import InitializationOptions
from mcp.server.fastmcp import FastMCP

from middleware import serve

# from function
def handler():
    return Function()

class MCPServer:
    mcpG = FastMCP("global mcp supertooler")

    @mcpG.tool()
    def hello_tool(name: str) -> str:
        return f"Hey there {name}!"

    def __init__(self):
        print("MCPServer init")
        self.mcp = FastMCP("super cool mcp server")
        self.mcp.settings.mount_path = "/mcp"
        self.mcpG.settings.mount_path = "/mcp"

    async def handle_mcp_requests(self,scope,receive,send) -> str:
        print("hello in handle_mcp_requests")
        rec = await receive()
        print(rec)
        #self.mcp.call_tool(name)
        return "hello"
    
# Function
class Function:
    def __init__(self):
        """
        initialize MCP server
        """

        self.mcp_server = MCPServer()
        #self.mcp_task = None

    async def handle(self, scope, receive, send): # pyright: ignore
        """ Handle all HTTP requests to this Function other than readiness
        and liveness probes."""

        logging.info("OK: Request Received")
        if scope['path'].startswith('/mcp'):
            print("scope starts with /mcp")
            r = await self.mcp_server.handle_mcp_requests(scope,receive,send)
            pass

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
    serve(handler)
