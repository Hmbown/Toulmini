# Configuration

Toulmini is entirely driven by environment variables that feed `toulmini.config.Config`.
The defaults match the values committed to `.env.example`, and you can inspect the
active runtime state with `toulmini-cli --config`.

## Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `TOULMINI_ENABLE_COUNCIL` | `true` | Toggle the Council of Experts helper (`consult_field_experts`). When `false`, the server returns `{"error": "COUNCIL_DISABLED"}` and skips council prompts. |
| `TOULMINI_STRICT_MODE` | `true` | Master circuit breaker switch. When `false`, warrant/backing validation is bypassed for debugging. |
| `TOULMINI_FAIL_ON_WEAK_WARRANT` | `true` | If `strict_mode` is enabled, terminate the chain when warrant strength is `weak` or `irrelevant`. |
| `TOULMINI_FAIL_ON_WEAK_BACKING` | `true` | Same as above but for backing strength. |
| `TOULMINI_DEBUG` | `false` | Forces server logging to DEBUG regardless of `TOULMINI_LOG_LEVEL`. Useful when tracing CLI/server interactions. |
| `TOULMINI_LOG_LEVEL` | `INFO` | Logging level applied at server boot (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). |

## Working with `.env`

1. Copy the example file: `cp .env.example .env`
2. Edit the values you need to override.
3. Export them into your MCP client environment (e.g., `direnv`, `dotenv`, or your shell profile).

Because `get_config()` caches values, restart your MCP client after editing `.env`,
or call `toulmini.config.reset_config()` inside tests.

## CLI Shortcuts

- `toulmini-cli --config` prints the active configuration (including which variables were set).
- `toulmini-cli --verify` ensures warrant/backing circuit breakers are aligned with your env.
- `toulmini-cli --install -` shows the MCP server snippet without writing files.

## Tuning Circuit Breakers

- Disable `TOULMINI_FAIL_ON_WEAK_WARRANT` or `TOULMINI_FAIL_ON_WEAK_BACKING` to collect
  diagnostic prompts without terminating the chain.
- Set `TOULMINI_STRICT_MODE=false` to bypass *all* warrant/backing validation (dangerous, but
  helpful when authoring prompts).
- Combine `TOULMINI_DEBUG=true` with `toulmini-cli --verify` to confirm troubleshooting mode is active.
