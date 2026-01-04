占位：GitHub MCP

- 预期入口：`npx github-mcp` 或 `node build/index.js`
- 安装示例：
  ```bash
  npm install
  npm run build
  # 或基于发布包：npm install github-mcp -D
  ```
- 功能：Issues/PR/代码片段检索，写作时引用仓库信息。
- 环境变量：`GITHUB_TOKEN=<REDACTED>`（建议只读 token）。

配置片段（示例）：
```
[mcp_servers.github-mcp]
command = "npx"
args = ["github-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\github-mcp"
env = { GITHUB_TOKEN = "<REDACTED>" }
```
