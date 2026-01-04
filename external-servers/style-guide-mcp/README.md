占位：Style Guide MCP

- 预期入口：`npx style-guide-mcp` 或 `node build/index.js`
- 安装示例：
  ```bash
  npm install
  npm run build
  # 或基于发布包：npm install style-guide-mcp -D
  ```
- 功能：风格/术语/规范检查。

配置片段（示例）：
```
[mcp_servers.style-guide-mcp]
command = "npx"
args = ["style-guide-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\style-guide-mcp"
```
