import asyncio
import logging

from mcp.server.fastmcp import FastMCP

from middleware import serve

def new():
    """Factory function for creating Function instances."""
    return Function()

class MCPServer:
    """MCP server that exposes tools, resources, and prompts via the MCP protocol."""
    
    def __init__(self):
        # Create FastMCP instance with stateless HTTP for Kubernetes deployment
        self.mcp = FastMCP("MCP Echo Server", stateless_http=True)
        
        self._register_tools()
        self._register_resources()
        self._register_prompts()
        
        # Get the ASGI app from FastMCP - handles session manager lifecycle
        self._app = self.mcp.streamable_http_app()

    def _register_tools(self):
        """Register MCP tools."""
        @self.mcp.tool()
        def hello_tool(name: str) -> str:
            """Say hello to someone."""
            return f"Hey there {name}!"
        
        @self.mcp.tool()
        def add_numbers(a: int, b: int) -> int:
            """Add two numbers together."""
            return a + b
    
    def _register_resources(self):
        """Register MCP resources."""
        @self.mcp.resource("echo://{message}")
        def echo_resource(message: str) -> str:
            """Echo the message as a resource."""
            return f"Echo: {message}"
    
    def _register_prompts(self):
        """Register MCP prompts."""
        @self.mcp.prompt()
        def greeting_prompt(name: str = "World"):
            """Generate a greeting prompt."""
            return [
                {
                    "role": "user",
                    "content": f"Please write a friendly greeting for {name}"
                }
            ]

    async def handle_request(self, scope, receive, send):
        """Handle ASGI requests - both lifespan and HTTP."""
        await self._app(scope, receive, send)
    
class Function:
    """ASGI application that integrates MCP server with existing middleware."""
    
    def __init__(self):
        self.mcp_server = MCPServer()
        self._mcp_initialized = False

    async def handle(self, scope, receive, send):
        """Handle ASGI requests."""
        # Initialize MCP server on first request
        if not self._mcp_initialized:
            await self._initialize_mcp()
        
        # Route MCP requests
        if scope['path'].startswith('/mcp'):
            await self.mcp_server.handle_request(scope, receive, send)
            return
        
        # Default response for non-MCP requests
        await self._send_default_response(send)
    
    async def _initialize_mcp(self):
        """Initialize the MCP server by sending lifespan startup event."""
        lifespan_scope = {'type': 'lifespan', 'asgi': {'version': '3.0'}}
        startup_sent = False
        
        async def lifespan_receive():
            nonlocal startup_sent
            if not startup_sent:
                startup_sent = True
                return {'type': 'lifespan.startup'}
            await asyncio.Event().wait()  # Wait forever for shutdown
        
        async def lifespan_send(message):
            if message['type'] == 'lifespan.startup.complete':
                self._mcp_initialized = True
            elif message['type'] == 'lifespan.startup.failed':
                logging.error(f"MCP startup failed: {message}")
        
        # Start lifespan in background
        asyncio.create_task(self.mcp_server.handle_request(
            lifespan_scope, lifespan_receive, lifespan_send
        ))
        
        # Brief wait for startup completion
        await asyncio.sleep(0.1)
    
    async def _send_default_response(self, send):
        """Send default OK response."""
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [[b'content-type', b'text/plain']],
        })
        await send({
            'type': 'http.response.body',
            'body': b'OK',
        })

    def start(self, cfg):
        """Called when the function instance starts."""
        logging.info("Function starting")
    
    def stop(self):
        """Called when the function instance stops."""
        logging.info("Function stopping")

if __name__ == "__main__":
    serve(new)