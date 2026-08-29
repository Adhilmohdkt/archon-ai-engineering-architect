from fastmcp import FastMCP
import os
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()

mcp = FastMCP("Archon")

tavily=TavilyClient(os.getenv('TAVILY_API_KEY'))

@mcp.tool 
def websearch(query : str , max_results : int = 5 ) :
    """ search for current information """

    response = tavily.search(query=query,max_results=max_results)

    return response['results']

if __name__ == "__main__":
    mcp.run()