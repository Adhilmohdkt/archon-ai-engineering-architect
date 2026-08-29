from  langchain_mcp_adapters.client import MultiServerMCPClient
import sys
import pathlib
import asyncio
SERVER_PATH = pathlib.Path(__file__).parent /'server.py'

mcp_client = MultiServerMCPClient(
    {
    'archon':{
        'command':sys.executable,
        'args':[str(SERVER_PATH)],
        'transport':'stdio',
    }
})

async def get_mcp_tools():
    tools = await mcp_client.get_tools()
    return tools