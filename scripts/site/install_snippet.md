## Install the MCP server

The server is a Python stdio MCP server published on PyPI as `apify-data-scrapers`. Every tool runs an Apify Actor on **your own** Apify account, so you need a free Apify account and its API token (Apify Console -> Settings -> Integrations).

**Claude Desktop / Claude Code** - add to `claude_desktop_config.json` (or `.mcp.json`):

```json
{
  "mcpServers": {
    "apify-scrapers": {
      "command": "uvx",
      "args": ["apify-data-scrapers"],
      "env": { "APIFY_TOKEN": "YOUR_APIFY_API_TOKEN" }
    }
  }
}
```

**Cursor** - Settings -> MCP -> Add server, same command (`uvx apify-data-scrapers`) and the `APIFY_TOKEN` environment variable.

**Smithery** - one-click install from [smithery.ai/servers/jlucasmcrell/apify-scrapers](https://smithery.ai/servers/jlucasmcrell/apify-scrapers).

**Without an MCP client** - the same Actors are callable from Python (`apify-client`), Node.js, n8n, Make or the Apify Console; see the [project README](/).
