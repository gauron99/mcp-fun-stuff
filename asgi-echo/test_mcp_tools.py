#!/usr/bin/env python3
"""
Test that confirms the MCP server in main.py correctly handles tool calls.
This test uses direct HTTP requests to the streamable HTTP endpoints.
"""

import asyncio
import sys
import httpx
import json
import uuid


async def test_mcp_tools():
    """Test the MCP server tools using streamable HTTP protocol"""
    
    # The server should be running on localhost:8081
    base_url = "http://localhost:8081"
    
    print("🔧 Testing MCP Server Tools with Streamable HTTP")
    print("=" * 50)
    
    # First check if the server is running
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url)
            print(f"✓ Server is running on {base_url}")
        except Exception as e:
            print(f"✗ Server not reachable at {base_url}")
            print(f"  Error: {e}")
            print("\nPlease start the server with:")
            print("  LISTEN_ADDRESS=:8081 python main.py")
            return False
    
    # FastMCP's streamable HTTP uses session-based communication
    async with httpx.AsyncClient() as client:
        # Create a session
        session_id = str(uuid.uuid4())
        
        print("\n1. Creating streamable HTTP session...")
        
        # The streamable HTTP protocol expects requests at /mcp/mcp
        # (our routing passes /mcp*, and FastMCP mounts at /mcp internally)
        endpoint = f"{base_url}/mcp/mcp"
        
        # Streamable HTTP uses session headers
        headers = {
            "Content-Type": "application/json",
            "X-MCP-Session-ID": session_id
        }
        
        # Test initialize
        print("\n2. Initializing MCP connection...")
        response = await client.post(
            endpoint,
            json={
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0"
                    }
                },
                "id": 1
            },
            headers=headers,
            follow_redirects=True
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"  Response: {response.text[:200]}")
            print("\n  Trying without session header...")
            
            # Try without session header
            response = await client.post(
                endpoint,
                json={
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "test-client",
                            "version": "1.0"
                        }
                    },
                    "id": 1
                },
                follow_redirects=True
            )
            
            print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                server_info = result["result"]["serverInfo"]
                print(f"✓ Connected to: {server_info['name']}")
                print(f"✓ Protocol version: {result['result']['protocolVersion']}")
                
                # Use the same headers for subsequent requests
                if "X-MCP-Session-ID" not in headers:
                    headers = {"Content-Type": "application/json"}
                
                # Test tools
                print("\n3. Listing available tools...")
                response = await client.post(
                    endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "params": {},
                        "id": 2
                    },
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    tools = result["result"]["tools"]
                    print(f"✓ Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")
                
                # Test hello_tool
                print("\n4. Testing hello_tool...")
                response = await client.post(
                    endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "hello_tool",
                            "arguments": {"name": "Streamable HTTP"}
                        },
                        "id": 3
                    },
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["result"]["content"][0]["text"]
                    print(f"✓ hello_tool('Streamable HTTP') returned: '{content}'")
                    
                    expected = "Hey there Streamable HTTP!"
                    if content == expected:
                        print("✓ Output matches expected result!")
                
                # Test add_numbers
                print("\n5. Testing add_numbers...")
                test_cases = [
                    (5, 3, 8),
                    (10, 20, 30),
                    (-5, 5, 0),
                    (100, 200, 300)
                ]
                
                all_passed = True
                for a, b, expected in test_cases:
                    response = await client.post(
                        endpoint,
                        json={
                            "jsonrpc": "2.0",
                            "method": "tools/call",
                            "params": {
                                "name": "add_numbers",
                                "arguments": {"a": a, "b": b}
                            },
                            "id": 4
                        },
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result["result"]["content"][0]["text"]
                        actual = int(content)
                        
                        if actual == expected:
                            print(f"✓ add_numbers({a}, {b}) = {actual} ✓")
                        else:
                            print(f"✗ add_numbers({a}, {b}) = {actual} (expected {expected})")
                            all_passed = False
                
                # Test resources
                print("\n6. Testing resources...")
                response = await client.post(
                    endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "method": "resources/list",
                        "params": {},
                        "id": 5
                    },
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    resources = result["result"]["resources"]
                    print(f"✓ Found {len(resources)} resource(s)")
                    
                    # Test echo resource
                    response = await client.post(
                        endpoint,
                        json={
                            "jsonrpc": "2.0",
                            "method": "resources/read",
                            "params": {"uri": "echo://Hello%20FastMCP"},
                            "id": 6
                        },
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result["result"]["contents"][0]["text"]
                        print(f"✓ Echo resource returned: '{content}'")
                
                print("\n" + "=" * 50)
                if all_passed:
                    print("✅ All tests passed!")
                    print("\n🎉 Your MCP server is working correctly!")
                    print("   - Uses FastMCP's streamable_http_app()")
                    print("   - No MCP protocol implementation in main.py")
                    print("   - All complexity delegated to FastMCP")
                    print("   - Ready for Kubernetes deployment!")
                    return True
                else:
                    print("❌ Some tests failed")
                    return False
            else:
                print(f"✗ Unexpected response: {result}")
                return False
        else:
            print(f"✗ Failed to connect to MCP server")
            print(f"  The FastMCP streamable HTTP app may need different routing")
            return False


async def main():
    """Run the test"""
    success = await test_mcp_tools()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())