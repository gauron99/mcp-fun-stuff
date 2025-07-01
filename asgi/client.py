from mcp.client.stdio import stdio_client
from mcp import ClientSession,StdioServerParameters

server_params = StdioServerParameters(
    command="python",
    args=["main.py"],
    env=None,
)

async def run():
    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read,write) as s:
            _ = await s.initialize()
            prompts = await s.list_prompts()
            prompt = await s.get_prompt(
                    "hello", arguments={"name": "Johnny"}
                    )
            
            result = await s.call_tool("welcomer",arguments={"name":"Newcomer"})

if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
