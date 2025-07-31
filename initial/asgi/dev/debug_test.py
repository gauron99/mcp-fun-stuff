#!/usr/bin/env python3
"""Debug script to understand the MCP routing"""

import httpx
import asyncio

async def debug_endpoints():
    """Test various endpoints to understand the routing"""
    
    base_url = "http://localhost:8081"
    
    async with httpx.AsyncClient() as client:
        # Test different endpoints
        endpoints = [
            "/mcp",
            "/mcp/",
            "/mcp/mcp",
            "/mcp/mcp/",
            "/mcp/sessions",
            "/mcp/mcp/sessions"
        ]
        
        print("Testing endpoints:")
        for endpoint in endpoints:
            try:
                # Try GET first
                response = await client.get(f"{base_url}{endpoint}", follow_redirects=False)
                print(f"\nGET {endpoint}: {response.status_code}")
                if response.status_code == 307:
                    print(f"  Redirects to: {response.headers.get('location')}")
                
                # Try POST with JSON-RPC
                response = await client.post(
                    f"{base_url}{endpoint}",
                    json={"jsonrpc": "2.0", "method": "initialize", "id": 1},
                    follow_redirects=False
                )
                print(f"POST {endpoint}: {response.status_code}")
                if response.status_code == 307:
                    print(f"  Redirects to: {response.headers.get('location')}")
                elif response.status_code == 200:
                    print(f"  Response: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"{endpoint}: Error - {e}")

if __name__ == "__main__":
    asyncio.run(debug_endpoints())