import logging
import asyncio
from mcp import server,types
import mcp
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from middleware import serve

# from function
def handler():
    return Function()


class MCPServer:
    def __init__(self):
        self.app = server.Server("my supercool server")
        self.setup_handlers()

    def setup_handlers(self):
        @self.app.command("hello")
        async def hello_handler(params: dict) -> dict:
            name = params.get("name")
            return {"message": f"Hello {name}! from hello handler "}

        @self.app.tool("welcomer")
        async def welcomer_tool(params:dict) -> dict:
            name = params.get("name")
            return {"welcome": f"Hello and welcome {name}!. Enjoy your stay."}

    async def run_stdio(self):
        """Run MCP server with stdio transport"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="asgi-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.app.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

# Function
class Function:
    def __init__(self):
        """
        initialize MCP server
        """
        self.mcp_server = MCPServer()
        self.mcp_task = None

    async def handle(self, scope, receive, send): # pyright: ignore
        """ Handle all HTTP requests to this Function other than readiness
        and liveness probes."""

        logging.info("OK: Request Received")

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
        self.mcp_task = asyncio.create_task(self.mcp_server.run_stdio())

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
