from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route ,Mount
import uvicorn
import asyncio

# 1. Define the Server
app = Server("greeting-server")

# 2. Implement the Greeting Tool
@app.call_tool()
async def call_tool(name: str , arguments : dict) -> list[TextContent]:
    """Handle tool calls from the client."""
    if name == "greet":
        return await greet(name=arguments["name"])
    else:
        return [TextContent(
            type="text",
            text=f"Error: Unknown tool: {name}"
        )]

async def greet(name: str) -> list[TextContent]:
    """Greets the user by name."""
    greeting_message = f"Hello, {name}!"
    return [TextContent(type="text", text=greeting_message)]

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="greet",
            description="greet the user",
            inputSchema={
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "name of the user",
                    }
                },
            },
        )
    ]

# 3. Configure the SSE Transport
sse = SseServerTransport("/messages")

# async def handle_sse(scope, receive, send):
#     async with sse.connect_sse(scope, receive, send) as streams:
#         await app.run(streams[0], streams[1], app.create_initialization_options())

async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())

async def handle_messages(scope, receive, send):
    await sse.handle_post_message(scope, receive, send)

starlette_app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        #Mount("/messages", endpoint=handle_messages, methods=["POST"]),
        Mount("/messages", app=sse.handle_post_message),
    ]
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=8080)
