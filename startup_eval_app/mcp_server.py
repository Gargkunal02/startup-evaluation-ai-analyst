#!/usr/bin/env python3
import asyncio
from mcp.server.fastmcp import FastMCP
from utils.orchestrator import run_multi_agent_analysis
from utils import db

mcp = FastMCP("startup-eval-mcp")

@mcp.tool()
def analyze_startup_tool(startup_id: int) -> dict:
    s = db.get_startup(startup_id)
    if not s:
        return {"error": "not found"}
    return run_multi_agent_analysis(s)

if __name__ == "__main__":
    asyncio.run(mcp.run())
