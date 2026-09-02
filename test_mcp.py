#!/usr/bin/env python3
import anyio
from mcp.client.streamable_http import streamable_http_client
from mcp import ClientSession
URL="https://agent.binance.com/mcp/agentic"
async def main():
    try:
        async with streamable_http_client(URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                r = await session.list_tools()
                print("TOTAL:", len(r.tools))
                for t in r.tools[:80]:
                    print(f"  - {t.name}: {(t.description or '')[:65]}")
    except BaseException as e:
        def dump(e, d=0):
            print("  "*d + f"{type(e).__name__}: {str(e)[:300]}")
            if hasattr(e,'exceptions'):
                for sub in e.exceptions: dump(sub, d+1)
        dump(e)
anyio.run(main)
