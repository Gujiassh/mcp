占位：Schema / 提纲 MCP

- 预期入口：`npx schema-mcp` 或 `node build/index.js`
- 安装示例：
  ```bash
  npm install
  npm run build
  # 或基于发布包：npm install schema-mcp -D
  ```
- 功能：文档提纲生成、结构校验。

配置片段（示例）：
```
[mcp_servers.schema-mcp]
command = "npx"
args = ["schema-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\schema-mcp"
```
