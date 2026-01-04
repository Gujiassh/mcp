占位：写作助手 MCP

- 预期入口：`npx writing-assistant-mcp` 或 `node build/index.js`
- 安装示例：
  ```bash
  npm install
  npm run build
  # 或基于发布包：npm install writing-assistant-mcp -D
  ```
- 功能：正文生成、润色、分段/摘要。

配置片段（示例）：
```
[mcp_servers.writing-assistant-mcp]
command = "npx"
args = ["writing-assistant-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\writing-assistant-mcp"
```
