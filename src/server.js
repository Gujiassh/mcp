import { promises as fs } from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { McpServer } from "../node_modules/@modelcontextprotocol/sdk/dist/esm/server/mcp.js";
import { StdioServerTransport } from "../node_modules/@modelcontextprotocol/sdk/dist/esm/server/stdio.js";
import * as z from "zod";
const require = createRequire(import.meta.url);
const mcpServer = new McpServer({
    name: "my-mcp-server",
    version: "1.0.0"
});
mcpServer.registerTool("hello", {
    description: "返回问候语",
    inputSchema: {
        name: z.string().describe("要问候的名字")
    }
}, async ({ name }) => ({
    content: [
        {
            type: "text",
            text: `你好，${name}！来自 MCP Server 的回应`
        }
    ]
}));
mcpServer.registerTool("pdfmcp", {
    description: "读取本地 PDF，并返回文本内容（可截断）",
    inputSchema: {
        filePath: z.string().min(1).describe("PDF 文件路径"),
        maxChars: z
            .number()
            .int()
            .positive()
            .max(20000)
            .optional()
            .describe("返回的最大字符数，默认 4000，最大 20000")
    }
}, async ({ filePath, maxChars }) => {
    const resolvedPath = path.resolve(filePath);
    await fs.access(resolvedPath);
    const pdfParse = require("pdf-parse");
    const data = await fs.readFile(resolvedPath);
    const parsed = await pdfParse(data);
    const limit = Math.min(Math.max(maxChars ?? 4000, 200), 20000);
    const text = (parsed.text ?? "").trim();
    const truncated = text.length > limit ? `${text.slice(0, limit)}\n...[截断]` : text;
    if (!truncated) {
        return {
            content: [{ type: "text", text: "未在 PDF 中提取到文本。" }]
        };
    }
    return {
        content: [
            {
                type: "text",
                text: truncated
            }
        ]
    };
});
async function main() {
    const transport = new StdioServerTransport();
    await mcpServer.connect(transport);
    console.log("MCP server is running over stdio");
}
main().catch(error => {
    console.error("Server failed:", error);
    process.exit(1);
});
//# sourceMappingURL=server.js.map