import sys
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

# run the mcp client
async def main(name :str):
  async with streamablehttp_client("http://localhost:8080/mcp") as (
          read_stream,
          write_stream,
          _,):
      async with ClientSession(read_stream,write_stream) as session:
            init = await session.initialize()
            print("Saying hello to someone...",end=" ")
            res = await session.call_tool("hello",{"name":name})
            print(res.content[0].text) # pyright: ignore 
            print("Prompting to say hello to Billy...",end=" ")
            prompt = await session.get_prompt("echo_bot_hello")
            print(prompt.messages[0].content.text) # pyright: ignore 
if __name__ == "__main__":
    import asyncio
    name = ""
    if len(sys.argv) != 2:
        name = "Anonymous"
    else:
        name = sys.argv[1]
    asyncio.run(main(name))
