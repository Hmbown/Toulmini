import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # 1. Define server parameters
    # We assume 'toulmini' is installed or accessible via python -m toulmini.server
    server_params = StdioServerParameters(
        command="python", args=["-m", "toulmini.server"], env=None
    )

    print("🔌 Connecting to Toulmini MCP Server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 2. Initialize
            await session.initialize()
            print("✅ Connected!")

            # 3. List Tools
            tools = await session.list_tools()
            print(f"\n🛠️  Available Tools: {len(tools.tools)}")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description[:50]}...")

            # 4. List Resources
            resources = await session.list_resources()
            print(f"\n📚 Available Resources: {len(resources.resources)}")
            for resource in resources.resources:
                print(f"  - {resource.uri}: {resource.name}")

            # 5. List Prompts
            prompts = await session.list_prompts()
            print(f"\n💬 Available Prompts: {len(prompts.prompts)}")
            for prompt in prompts.prompts:
                print(f"  - {prompt.name}: {prompt.description}")

            # 6. Read the Model Resource
            print("\n📖 Reading toulmin://model resource...")
            try:
                content = await session.read_resource("toulmin://model")
                print(
                    f"--- Content Preview ---\n{content.contents[0].text[:200]}...\n-----------------------"
                )
            except Exception as e:
                print(f"❌ Failed to read resource: {e}")

            # 7. Example Tool Call (Phase 1)
            query = "Is remote work more productive?"
            print(f"\n🧪 Testing Phase 1 with query: '{query}'")
            try:
                result = await session.call_tool(
                    "initiate_toulmin_sequence", arguments={"query": query}
                )
                print("--- Tool Output (Prompt) ---")
                print(result.content[0].text[:200] + "...")
                print("----------------------------")
            except Exception as e:
                print(f"❌ Tool call failed: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
