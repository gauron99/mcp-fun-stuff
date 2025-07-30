# Ollama-MCP Function

A Knative Function implementing a Model Context Protocol (MCP) server that
provides integration with Ollama for local LLM interactions. This function
exposes Ollama capabilities through standardized MCP tools, enabling the
interact with locally hosted language models.

The flow is as follows:
`MCP client -> MCP Serer (Function) -> Ollama Server`

## Architecture

This project implements an ASGI-based Knative function with the following key
components:

### Core Components
- **Function Class**: Main ASGI application entry point with lifecycle
management
- **MCPServer Class**: FastMCP-based server implementing HTTP-streamable MCP
protocol
- **MCP Tools**: Three primary tools for Ollama interaction:
  - `list_models`: Enumerate available models on the Ollama server
  - `pull_model`: Download and install new models
  - `call_model`: Send prompts to models and receive responses

### Technical Implementation Details

- **Protocol**: HTTP-based MCP communication using FastMCP's streamable HTTP
transport
- **Stateless Design**: No persistent state between requests, suitable for
Kubernetes scaling
- **Error Handling**: Comprehensive exception handling with user-friendly error
messages
- **Lifespan Management**: Proper ASGI lifespan handling for MCP server
initialization

## Setup

### Prerequisites

- Python 3.9 or higher
- Ollama server running locally or accessible via network
- (Optional) Knative/Kubernetes environment for deployment

### Local Development Setup

1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Start Ollama server:**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.com/install.sh | sh

   # Start Ollama service
   ollama serve

   # Pull a model (optional, can be done via MCP tool)
   ollama pull llama3.2:3b
   ```

3. **Run the function locally:**
   ```bash
   # Using Python directly
   python -m function.func

   # Or using func CLI (if available)
   func run
   ```

4. **Test MCP connectivity:**
   ```bash
   python client/client.py
   ```

### MCP Tools Reference

#### `list_models()`
- **Purpose**: Returns all models currently available on the Ollama server
- **Parameters**: None
- **Returns**: List of model objects with metadata
- **Usage**: Discover available models before making chat requests

#### `pull_model(model: str)`
- **Purpose**: Downloads and installs a model from Ollama's registry
- **Parameters**:
  - `model`: Model identifier (e.g., "llama3.2:3b", "codellama:7b")
- **Returns**: Success/error message
- **Usage**: Install new models on-demand

#### `call_model(prompt: str, model: str = "llama3.2:3b")`
- **Purpose**: Sends a prompt to a model and returns the response
- **Parameters**:
  - `prompt`: The text prompt to send to the model
  - `model`: Model identifier (defaults to "llama3.2:3b")
- **Returns**: Model's text response
- **Usage**: Primary interface for LLM interactions

### Client Usage Example

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://localhost:8080/mcp") as streams:
        read_stream, write_stream = streams[0], streams[1]

        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # List available models
            models = await session.call_tool(name="list_models")
            print(f"Available models: {models}")

            # Chat with a model
            response = await session.call_tool(
                name="call_model",
                arguments={
                    "prompt": "Explain async programming in Python",
                    "model": "llama3.2:3b"
                }
            )
            print(f"Response: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Deployment

#### Knative Function Deployment

```bash
# Deploy to Knative cluster
func deploy

# Or build and deploy with custom image
func deploy --image your-registry/mcp-ollama-function
```

#### Docker Deployment

```bash
# Build container
docker build -t mcp-ollama-function .

# Run container
docker run -p 8080:8080 \
  -e OLLAMA_HOST=host.docker.internal:11434 \
  mcp-ollama-function
```

### Optional ENVs

- `OLLAMA_HOST`: Ollama server host (default: localhost:11434)
- `MCP_PATH`: Path for MCP endpoint (default: /mcp)

### Troubleshooting

**Connection Issues:**
- Ensure Ollama server is running and accessible
- Check firewall settings for port 11434 (Ollama default)
- Verify model availability with `ollama list`
- Confirm function is running on expected port (default: 8080)

**Performance Considerations:**
- Model loading time varies by size (3B models ~2-5s, 7B+ models 10-30s)
- Consider pre-loading frequently used models
- Monitor memory usage for large models

## Dependencies

- **mcp**: Model Context Protocol implementation
- **ollama**: Python client for Ollama API
- **httpx**: Async HTTP client for external requests
- **pytest/pytest-asyncio**: Testing framework with async support

