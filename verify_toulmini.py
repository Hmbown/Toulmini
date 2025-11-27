#!/usr/bin/env python3
"""
Toulmini Verification Script.

Tests that all 4 tools are registered and functioning correctly.
Run with: python verify_toulmini.py
"""

import asyncio
import sys

from toulmini.server import mcp


async def main():
    print("=" * 60)
    print("TOULMINI LOGIC HARNESS - VERIFICATION")
    print("=" * 60)

    # Test 1: List tools
    print("\n[1] Checking registered tools...")
    try:
        tools = await mcp.list_tools()
        print(f"    Found {len(tools)} tools:")
        for tool in tools:
            print(f"    ✓ {tool.name}")

        expected_tools = {
            "initiate_toulmin_sequence",
            "inject_logic_bridge",
            "stress_test_argument",
            "render_verdict"
        }
        actual_tools = {tool.name for tool in tools}

        if actual_tools == expected_tools:
            print("    ✓ All 4 tools registered correctly")
        else:
            missing = expected_tools - actual_tools
            extra = actual_tools - expected_tools
            if missing:
                print(f"    ✗ Missing tools: {missing}")
            if extra:
                print(f"    ⚠ Extra tools: {extra}")
            sys.exit(1)
    except Exception as e:
        print(f"    ✗ Failed to list tools: {e}")
        sys.exit(1)

    # Test 2: Phase 1 - initiate_toulmin_sequence
    print("\n[2] Testing Phase 1: initiate_toulmin_sequence...")
    try:
        result = await mcp.call_tool(
            "initiate_toulmin_sequence",
            arguments={"query": "Is AI sentient?"}
        )
        # Result should be a list of content items
        if result and len(result) > 0:
            content = result[0].text if hasattr(result[0], 'text') else str(result[0])
            # Check it contains expected prompt elements
            if "PHASE 1" in content and "DATA" in content and "CLAIM" in content:
                print("    ✓ Phase 1 returns valid prompt structure")
            else:
                print("    ⚠ Phase 1 returned unexpected content")
        else:
            print("    ✗ Phase 1 returned empty result")
    except Exception as e:
        print(f"    ✗ Phase 1 failed: {e}")

    # Test 3: Query too short error
    print("\n[3] Testing error handling (query too short)...")
    try:
        result = await mcp.call_tool(
            "initiate_toulmin_sequence",
            arguments={"query": "Hi"}
        )
        content = result[0].text if hasattr(result[0], 'text') else str(result[0])
        if "QUERY_TOO_SHORT" in content:
            print("    ✓ Short query error handled correctly")
        else:
            print(f"    ⚠ Unexpected response: {content[:50]}")
    except Exception as e:
        print(f"    ✗ Error handling test failed: {e}")

    # Test 4: Phase 2 missing dependencies
    print("\n[4] Testing Phase 2 dependency check...")
    try:
        result = await mcp.call_tool(
            "inject_logic_bridge",
            arguments={"query": "Test", "data_json": "", "claim_json": ""}
        )
        content = result[0].text if hasattr(result[0], 'text') else str(result[0])
        if "MISSING_PHASE_1_OUTPUT" in content:
            print("    ✓ Missing dependency error handled correctly")
        else:
            print(f"    ⚠ Unexpected response: {content[:50]}")
    except Exception as e:
        print(f"    ✗ Dependency check test failed: {e}")

    # Test 5: Check tool descriptions contain examples
    print("\n[5] Checking tool documentation quality...")
    docs_quality = True
    for tool in tools:
        desc = tool.description or ""
        if "Example" in desc or "example" in desc:
            print(f"    ✓ {tool.name}: Has examples in description")
        else:
            print(f"    ⚠ {tool.name}: Missing examples in description")
            docs_quality = False

    if docs_quality:
        print("    ✓ All tools have documented examples")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
