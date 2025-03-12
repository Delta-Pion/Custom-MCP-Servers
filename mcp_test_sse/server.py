from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
import asyncio

# 1. Define the Server
app = Server("greeting-server")

# 2. Implement the Greeting Tool
@app.call_tool()
async def greet(name: str) -> list[TextContent]:
    """Greets the user by name."""
    greeting_message = f"Hello, {name}!"
    return [TextContent(type="text", text=greeting_message)]

# 3. Configure the SSE Transport
sse = SseServerTransport("/messages")

async def handle_sse(scope, receive, send):
    async with sse.connect_sse(scope, receive, send) as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())

async def handle_messages(scope, receive, send):
    await sse.handle_post_message(scope, receive, send)

starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ]
)
