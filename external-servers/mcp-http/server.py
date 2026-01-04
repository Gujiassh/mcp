from mcp.server.fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def greet(name: str) -> str:
    """Greet a person with their name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")