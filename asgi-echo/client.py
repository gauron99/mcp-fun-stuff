from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession


async def main():
    async with streamablehttp_client("localhost:8080/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream,write_stream) as s:
            _ = await s.initialize()

            tools = await s.list_tools()
            print(tools)

            hello_tool = await s.call_tool("hello",{"name":"Pepa"})
            print(hello_tool)

