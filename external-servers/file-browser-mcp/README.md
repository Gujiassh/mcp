占位：File Browser MCP

- 预期入口：`npx file-browser-mcp` 或 `node build/index.js`
- 安装示例：
  ```bash
  npm install
  npm run build
  # 或基于发布包：npm install file-browser-mcp -D
  ```
- 功能：列目录/读文件，为写作/格式化提供上下文。

配置片段（示例）：
```
[mcp_servers.file-browser-mcp]
command = "npx"
args = ["file-browser-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\file-browser-mcp"
```
