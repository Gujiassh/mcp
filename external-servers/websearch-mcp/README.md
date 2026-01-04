占位：Web Search MCP

- 预期入口：`npx websearch-mcp` 或 `node build/index.js`
- 安装示例：
  ```bash
  npm install
  npm run build
  # 或基于发布包：npm install websearch-mcp -D
  ```
- 功能：通用 Web 搜索/检索，为文档提供外部引用。
- 环境变量：`SEARCH_API_KEY=<REDACTED>`（按实际 API 替换）。

配置片段（示例）：
```
[mcp_servers.websearch-mcp]
command = "npx"
args = ["websearch-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\websearch-mcp"
env = { SEARCH_API_KEY = "<REDACTED>" }
```
