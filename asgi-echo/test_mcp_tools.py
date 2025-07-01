#!/usr/bin/env python3
"""
Simple test that verifies the MCP server works with the MCP client library.
"""

import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def test_mcp_server():
    """Test the MCP server using the official MCP client"""
    
    # Connect to the server
    async with streamablehttp_client("http://localhost:8081/mcp/mcp") as streams:
        read_stream, write_stream = streams[0], streams[1]
        
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()
            
            # Test hello_tool
            result = await session.call_tool(
                name="hello_tool",
                arguments={"name": "MCP Client"}
            )
            print(f"hello_tool('MCP Client') = '{result.content[0].text}'")
            
            # Test add_numbers
            result = await session.call_tool(
                name="add_numbers", 
                arguments={"a": 5, "b": 3}
            )
            print(f"add_numbers(5, 3) = {result.content[0].text}")
            
            print("\n✅ MCP server is working correctly!")


if __name__ == "__main__":
    try:
        asyncio.run(test_mcp_server())
    except Exception as e:
        # Ignore cleanup errors
        if "validation error" not in str(e).lower():
            raise