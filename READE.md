自用

codex 配置
```
[mcp_servers]
[mcp_servers.local_mcp]
command = "npx"
args = ["ts-node-esm", "src/server.ts"]
cwd = "E:\\code\\mcp"
```

## Project Planner MCP

- 已经把 https://github.com/Harshithsoma/ProjectPlannerMCP 集成进 `src/server.ts`，并开放 `create_project`、`list_projects`、`get_projects`、`delete_project`、`create_todo`、`update_todo`、`delete_todo`、`get_todo`、`list_todos` 等工具，方便项目 / Todo 管理。
- Planner 数据默认持久化到 `data/project-planner.json`，如果需要换位置，请在启动前设置 `MCP_PROJECT_PLANNER_DATA_DIR`。

## 外部 MCP 服务器（external-servers）

所有第三方服务器都集中在 `external-servers/` 下，按需进入子目录执行各自的安装/构建命令即可。

| 名称 | 目录 | 技术栈 / 说明 |
| --- | --- | --- |
| Filesystem MCP | `external-servers/filesystem-mcp` | 官方 TypeScript 版本，运行 `npm install && npm run build`，之后可用 `npx mcp-server-filesystem` 启动。 |
| mcp-shell | `external-servers/mcp-shell` | TypeScript，运行 `npm install && npm run build`，命令为 `npx mcp-shell`。 |
| mcp-doc-analyzer | `external-servers/mcp-doc-analyzer` | Python（fastmcp）。推荐使用 `uv sync` 或 `pip install -r` 安装依赖，然后 `uv run python main.py`。 |
| software-planning-mcp | `external-servers/software-planning-mcp` | TypeScript，`npm install && npm run build` 后，通过 `node build/index.js` 暴露 server。 |
| mcp-http | `external-servers/mcp-http` | Python（mcp[cli]），需要 Python ≥ 3.13，执行 `uv sync`（或 `pip install mcp[cli]`），然后 `uv run python main.py`。 |
| mcp-qdrant | `external-servers/mcp-qdrant` | Python（fastmcp + qdrant-client）。执行 `uv sync`/`pip install -r requirements` 后，通过 `uv run mcp-server-qdrant` 启动。 |
| Auggie MCP | `external-servers/auggie-mcp` | Node 18+ + Python 3.10+，需先在系统安装 Auggie CLI 并准备 `AUGMENT_API_TOKEN`。本地可 `npm install` 后 `node bin/auggie-mcp.js`，或直接 `npx -y auggie-mcp --setup-only && npx -y auggie-mcp`。 |

> `mcp-markdown-processor`：公共仓库/包暂未找到，后续如果有官方地址或发行方式请补充，再追加到 `external-servers/`。

## 文档/写作类 MCP（新增待接入）

以下工具链用于自动撰写、排版与校验文档，计划统一放在 `external-servers/` 下，按需拉取官方仓库或发布包：

| 名称 | 计划目录 | 说明 |
| --- | --- | --- |
| writing-assistant-mcp | `external-servers/writing-assistant-mcp` | 写作助手，负责正文生成与润色。待拉官方仓库后在目录内执行 `npm install && npm run build`（或对应语言的安装命令），入口一般为 `npx writing-assistant-mcp`。 |
| markdown-formatter-mcp | `external-servers/markdown-formatter-mcp` | Markdown 结构化/排版工具，建议在本地安装后暴露 `format_markdown` 等动作。 |
| schema-mcp | `external-servers/schema-mcp` | 文档提纲/Schema 生成器，可用来生成 PRD/TechSpec 目录结构。 |
| diagram-mcp | `external-servers/diagram-mcp` | 基于描述生成流程图/架构图（如 Mermaid/SVG）。 |
| file-browser-mcp | `external-servers/file-browser-mcp` | 文件浏览/读取，辅助把仓库上下文喂给写作与格式化工具。 |
| github-mcp | `external-servers/github-mcp` | GitHub API 集成（issues/PR/代码片段检索），便于写作时取用上下文。 |
| websearch-mcp | `external-servers/websearch-mcp` | Web 搜索/检索，用于补充外部资料与引用。 |
| style-guide-mcp | `external-servers/style-guide-mcp` | 风格/规范检查器，约束输出符合团队写作/术语要求。 |

> 推荐路由：在生成完整文档时默认组合 `schema-mcp → writing-assistant-mcp → diagram-mcp → markdown-formatter-mcp → style-guide-mcp`，必要时穿插 `file-browser-mcp`/`github-mcp`/`websearch-mcp` 获取上下文，无需用户逐一点名工具。

### 运行/配置示例

在 `config.toml` 中追加：
```
[mcp_servers.schema-mcp]
command = "npx"
args = ["schema-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\schema-mcp"

[mcp_servers.writing-assistant-mcp]
command = "npx"
args = ["writing-assistant-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\writing-assistant-mcp"

[mcp_servers.diagram-mcp]
command = "npx"
args = ["diagram-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\diagram-mcp"

[mcp_servers.markdown-formatter-mcp]
command = "npx"
args = ["markdown-formatter-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\markdown-formatter-mcp"

[mcp_servers.style-guide-mcp]
command = "npx"
args = ["style-guide-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\style-guide-mcp"

[mcp_servers.file-browser-mcp]
command = "npx"
args = ["file-browser-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\file-browser-mcp"

[mcp_servers.github-mcp]
command = "npx"
args = ["github-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\github-mcp"
env = { GITHUB_TOKEN = "<REDACTED>" }

[mcp_servers.websearch-mcp]
command = "npx"
args = ["websearch-mcp"]
cwd = "E:\\code\\mcp\\external-servers\\websearch-mcp"
env = { SEARCH_API_KEY = "<REDACTED>" }
```

通用安装指令（在各子目录执行）：
```
npm install
npm run build   # 如包已发布，可改为 npm install <package> -D
```
