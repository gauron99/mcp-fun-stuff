import asyncio
from fastmcp import Client

async def main():
  async with Client("local-server.py") as client:
    tools = await client.list_tools()
    print("Tools:" ,tools)
    result = await client.call_tool("hello",{"name":"Davidos"})
    print("Result: ",result)


asyncio.run(main())