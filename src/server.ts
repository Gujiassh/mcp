import { promises as fs } from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import * as z from "zod";

const require = createRequire(import.meta.url);
type PdfParseFn = (data: Buffer, options?: { max?: number }) => Promise<{ text: string }>;
type MammothModule = {
  extractRawText: (options: { path: string }) => Promise<{
    value?: string;
    messages?: Array<{ type: string; message: string }>;
  }>;
};
type WordExtractorInstance = {
  extract: (filePath: string) => Promise<{ getBody(): string | undefined }>;
};
const mammoth = require("mammoth") as MammothModule;
const WordExtractorCtor = require("word-extractor") as new () => WordExtractorInstance;
const wordExtractor = new WordExtractorCtor();
type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | "HEAD";
const PROJECTS_ROOT = path.resolve(
  process.env.MCP_PROJECTS_ROOT ?? path.join(process.cwd(), "..", "agent", "projects")
);
const CHROME_CANDIDATES = [
  process.env.MCP_CHROME_PATH,
  "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
  "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium-browser"
].filter((entry): entry is string => Boolean(entry));
const TEXT_FILE_EXTENSIONS = new Set([".md", ".mdx", ".txt"]);

function ensurePathWithin(baseDir: string, candidate: string) {
  const normalizedBase = path.resolve(baseDir);
  const normalizedCandidate = path.resolve(candidate);
  const baseWithSep = normalizedBase.endsWith(path.sep) ? normalizedBase : `${normalizedBase}${path.sep}`;
  if (normalizedCandidate === normalizedBase || normalizedCandidate.startsWith(baseWithSep)) {
    return normalizedCandidate;
  }
  throw new Error("路径越界，拒绝访问。");
}

function resolveProjectDir(project: string) {
  const trimmed = project.trim();
  if (!trimmed) {
    throw new Error("请提供项目名称。");
  }
  return ensurePathWithin(PROJECTS_ROOT, path.resolve(PROJECTS_ROOT, trimmed));
}

function resolveProjectPath(project: string, relativePath: string) {
  const projectDir = resolveProjectDir(project);
  const target = path.resolve(projectDir, relativePath);
  return ensurePathWithin(projectDir, target);
}

async function extractWordText(filePath: string) {
  const resolvedPath = path.resolve(filePath);
  const ext = path.extname(resolvedPath).toLowerCase();
  if (ext === ".docx") {
    const result = await mammoth.extractRawText({ path: resolvedPath });
    return {
      text: (result.value ?? "").trim(),
      warnings: result.messages ?? []
    };
  }
  if (ext === ".doc") {
    const doc = await wordExtractor.extract(resolvedPath);
    return {
      text: (doc.getBody() ?? "").trim(),
      warnings: []
    };
  }
  throw new Error("仅支持 .doc 与 .docx 文件。");
}

async function collectFilesRecursively(baseDir: string, dir: string) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    let fullPath: string;
    try {
      fullPath = ensurePathWithin(baseDir, path.join(dir, entry.name));
    } catch {
      continue;
    }
    if (entry.isDirectory()) {
      files.push(...(await collectFilesRecursively(baseDir, fullPath)));
    } else {
      files.push(fullPath);
    }
  }
  return files;
}

function buildSnippet(content: string, matchIndex: number, queryLength: number) {
  const radius = 200;
  const start = Math.max(0, matchIndex - radius);
  const end = Math.min(content.length, matchIndex + queryLength + radius);
  let snippet = content.slice(start, end).replace(/\s+/g, " ").trim();
  if (start > 0) {
    snippet = `...${snippet}`;
  }
  if (end < content.length) {
    snippet = `${snippet}...`;
  }
  return snippet;
}

async function findChromeExecutable() {
  for (const candidate of CHROME_CANDIDATES) {
    try {
      await fs.access(candidate);
      return candidate;
    } catch {
      // continue
    }
  }
  throw new Error(
    "找不到 Chrome 可执行文件，请设置环境变量 MCP_CHROME_PATH 指向 chrome.exe 或 chromium。"
  );
}

async function launchChrome(options: {
  url: string;
  remoteDebuggingPort: number;
  autoOpenDevtools: boolean;
  userDataDir?: string | undefined;
}) {
  const chromeBinary = await findChromeExecutable();
  const args = [`--remote-debugging-port=${options.remoteDebuggingPort}`];
  if (options.autoOpenDevtools) {
    args.push("--auto-open-devtools-for-tabs");
  }
  if (options.userDataDir) {
    const resolvedProfile = path.resolve(options.userDataDir);
    args.push(`--user-data-dir=${resolvedProfile}`);
  }
  args.push(options.url);

  const child = spawn(chromeBinary, args, {
    detached: true,
    stdio: "ignore",
    shell: false
  });
  child.unref();
  return chromeBinary;
}

const mcpServer = new McpServer({
  name: "my-mcp-server",
  version: "1.0.0"
});

mcpServer.registerTool(
  "hello",
  {
    description: "返回问候语",
    inputSchema: {
      name: z.string().describe("要问候的名字")
    }
  },
  async ({ name }: { name: string }) => ({
    content: [
      {
        type: "text",
        text: `你好，${name}！来自 MCP Server 的回应`
      }
    ]
  })
);

mcpServer.registerTool(
  "pdfmcp",
  {
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
  },
  async ({ filePath, maxChars }: { filePath: string; maxChars?: number | undefined }) => {
    const resolvedPath = path.resolve(filePath);
    await fs.access(resolvedPath);
    const pdfParse = require("pdf-parse") as unknown as PdfParseFn;
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
  }
);

mcpServer.registerTool(
  "docmcp",
  {
    description: "读取本地 Word 文档（.doc/.docx），返回文本内容（可截断）",
    inputSchema: {
      filePath: z.string().min(1).describe("Word 文件路径"),
      maxChars: z
        .number()
        .int()
        .positive()
        .max(20000)
        .optional()
        .describe("返回的最大字符数，默认 4000，最大 20000")
    }
  },
  async ({ filePath, maxChars }: { filePath: string; maxChars?: number | undefined }) => {
    const resolvedPath = path.resolve(filePath);
    await fs.access(resolvedPath);
    const { text, warnings } = await extractWordText(resolvedPath);
    if (!text) {
      return {
        content: [{ type: "text", text: "未在 Word 文档中提取到文本。" }]
      };
    }
    const limit = Math.min(Math.max(maxChars ?? 4000, 200), 20000);
    const truncated = text.length > limit ? `${text.slice(0, limit)}\n...[截断]` : text;
    const warningText =
      warnings && warnings.length > 0
        ? `\n\n⚠️ 解析警告：\n${warnings.map(item => `- ${item.message ?? item}`).join("\n")}`
        : "";

    return {
      content: [
        {
          type: "text",
          text: `${truncated}${warningText}`
        }
      ]
    };
  }
);

mcpServer.registerTool(
  "launch_chrome_dev",
  {
    description: "启动 Chrome/Chromium Dev 实例，默认打开本地前端地址并开启远程调试端口",
    inputSchema: {
      url: z.string().url().default("http://localhost:5173").describe("要打开的页面 URL"),
      remoteDebuggingPort: z
        .number()
        .int()
        .min(1024)
        .max(65535)
        .default(9222)
        .describe("Chrome 远程调试端口"),
      autoOpenDevtools: z.boolean().default(true).describe("是否自动打开 DevTools"),
      userDataDir: z
        .string()
        .optional()
        .describe("自定义用户数据目录（可保持独立调试配置）")
    }
  },
  async ({
    url,
    remoteDebuggingPort,
    autoOpenDevtools,
    userDataDir
  }: {
    url: string;
    remoteDebuggingPort: number;
    autoOpenDevtools: boolean;
    userDataDir?: string | undefined;
  }) => {
    try {
      new URL(url);
    } catch {
      throw new Error("URL 无效，请输入合法的 http(s) 地址。");
    }
    const chromeOptions: {
      url: string;
      remoteDebuggingPort: number;
      autoOpenDevtools: boolean;
      userDataDir?: string | undefined;
    } = {
      url,
      remoteDebuggingPort,
      autoOpenDevtools
    };
    if (userDataDir) {
      chromeOptions.userDataDir = userDataDir;
    }
    const binary = await launchChrome(chromeOptions);

    return {
      content: [
        {
          type: "text",
          text: `已启动 Chrome（${binary}），URL: ${url}，远程调试端口 ${remoteDebuggingPort}`
        }
      ]
    };
  }
);

mcpServer.registerTool(
  "fetch_url",
  {
    description: "发送 HTTP(S) 请求，快速获取网页或 API 文本响应",
    inputSchema: {
      url: z.string().url().describe("请求地址，只支持 http/https"),
      method: z
        .enum(["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"])
        .default("GET")
        .describe("HTTP 方法"),
      headers: z.record(z.string(), z.string()).optional().describe("HTTP 头，键值对"),
      body: z
        .string()
        .optional()
        .describe("请求体，仅在非 GET/HEAD 方法时使用"),
      maxChars: z
        .number()
        .int()
        .positive()
        .max(20000)
        .optional()
        .describe("最大返回字符数，默认 4000，最大 20000"),
      timeoutMs: z
        .number()
        .int()
        .min(500)
        .max(60000)
        .optional()
        .describe("超时时间，默认 15000 毫秒")
    }
  },
  async ({
    url,
    method,
    headers,
    body,
    maxChars,
    timeoutMs
  }: {
    url: string;
    method: HttpMethod;
    headers?: Record<string, string> | undefined;
    body?: string | undefined;
    maxChars?: number | undefined;
    timeoutMs?: number | undefined;
  }) => {
    const allowedProtocols = new Set(["http:", "https:"]);
    const parsedUrl = new URL(url);
    if (!allowedProtocols.has(parsedUrl.protocol)) {
      throw new Error("仅支持 http/https 协议。");
    }

    const methodUpper = method.toUpperCase() as HttpMethod;
    if (body && (methodUpper === "GET" || methodUpper === "HEAD")) {
      throw new Error("GET/HEAD 请求不支持 body。");
    }

    const limit = Math.min(Math.max(maxChars ?? 4000, 200), 20000);
    const timeoutLimit = Math.min(Math.max(timeoutMs ?? 15000, 500), 60000);

    const controller = new AbortController();
    const timeoutHandle = setTimeout(() => controller.abort(), timeoutLimit);

    try {
      const requestInit: RequestInit = {
        method: methodUpper,
        signal: controller.signal
      };
      if (headers && Object.keys(headers).length > 0) {
        requestInit.headers = headers;
      }
      if (body && methodUpper !== "GET" && methodUpper !== "HEAD") {
        requestInit.body = body;
      }

      const response = await fetch(url, requestInit);

      const text = await response.text();
      const truncated = text.length > limit ? `${text.slice(0, limit)}\n...[截断]` : text;
      const contentType = response.headers.get("content-type") ?? "未知";
      const summary = [
        `URL: ${url}`,
        `Method: ${methodUpper}`,
        `Status: ${response.status} ${response.statusText}`,
        `Content-Type: ${contentType}`
      ].join("\n");

      return {
        content: [
          {
            type: "text",
            text: `${summary}\n\n${truncated}`
          }
        ]
      };
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        throw new Error("请求超时，请增大 timeoutMs。");
      }
      throw error;
    } finally {
      clearTimeout(timeoutHandle);
    }
  }
);

mcpServer.registerTool(
  "list_project_docs",
  {
    description: "列出指定项目/目录下的文档（默认 skills）",
    inputSchema: {
      project: z.string().min(1).describe("项目名称，例如 point-cloud、solarsense-ui"),
      section: z
        .string()
        .min(1)
        .default("skills")
        .describe("项目内的子目录，例如 skills、progress")
    }
  },
  async ({ project, section }: { project: string; section: string }) => {
    const targetDir = resolveProjectPath(project, section);
    const stats = await fs.stat(targetDir);
    if (!stats.isDirectory()) {
      throw new Error(`指定路径不是目录：${section}`);
    }
    const entries = await fs.readdir(targetDir, { withFileTypes: true });
    const list = entries
      .sort((a, b) => a.name.localeCompare(b.name))
      .map(entry => (entry.isDirectory() ? `${entry.name}/` : entry.name));

    const text =
      list.length > 0
        ? `项目 ${project}/${section} 下的文档：\n${list.map(item => `- ${item}`).join("\n")}`
        : `项目 ${project}/${section} 下没有文档。`;

    return {
      content: [{ type: "text", text }]
    };
  }
);

mcpServer.registerTool(
  "read_project_doc",
  {
    description: "读取项目文档内容，可指定最大字符数避免过长输出",
    inputSchema: {
      project: z.string().min(1).describe("项目名称，例如 point-cloud、solarsense-ui"),
      relativePath: z.string().min(1).describe("相对于项目根目录的路径，例如 skills/segmentation-mode.md"),
      maxChars: z
        .number()
        .int()
        .positive()
        .max(20000)
        .optional()
        .describe("返回的最大字符数，默认 4000，最大 20000")
    }
  },
  async ({
    project,
    relativePath,
    maxChars
  }: {
    project: string;
    relativePath: string;
    maxChars?: number | undefined;
  }) => {
    const filePath = resolveProjectPath(project, relativePath);
    const stats = await fs.stat(filePath);
    if (!stats.isFile()) {
      throw new Error(`指定路径不是文件：${relativePath}`);
    }
    const raw = await fs.readFile(filePath, "utf8");
    const limit = Math.min(Math.max(maxChars ?? 4000, 200), 20000);
    const truncated = raw.length > limit ? `${raw.slice(0, limit)}\n...[截断]` : raw;
    const header = `# ${project}/${relativePath}`;

    return {
      content: [{ type: "text", text: `${header}\n\n${truncated}` }]
    };
  }
);

mcpServer.registerTool(
  "search_project_docs",
  {
    description: "按关键字搜索项目文档内容（默认检索 skills 目录），返回匹配片段",
    inputSchema: {
      project: z.string().min(1).describe("项目名称，例如 point-cloud、solarsense-ui"),
      query: z.string().min(1).describe("要搜索的关键字或短语"),
      section: z
        .string()
        .min(1)
        .default("skills")
        .describe("要搜索的子目录，默认 skills"),
      maxResults: z
        .number()
        .int()
        .min(1)
        .max(20)
        .default(5)
        .describe("最多返回多少条命中，默认 5，最大 20")
    }
  },
  async ({
    project,
    query,
    section,
    maxResults
  }: {
    project: string;
    query: string;
    section: string;
    maxResults: number;
  }) => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      throw new Error("请输入有效的搜索关键字。");
    }
    const projectDir = resolveProjectDir(project);
    const targetDir = resolveProjectPath(project, section);
    const stats = await fs.stat(targetDir);
    if (!stats.isDirectory()) {
      throw new Error(`指定路径不是目录：${section}`);
    }

    const files = await collectFilesRecursively(projectDir, targetDir);
    const normalizedQuery = trimmedQuery.toLowerCase();
    const matches: { path: string; snippet: string; line: number }[] = [];

    for (const file of files) {
      if (!TEXT_FILE_EXTENSIONS.has(path.extname(file).toLowerCase())) {
        continue;
      }
      const content = await fs.readFile(file, "utf8");
      const lower = content.toLowerCase();
      const idx = lower.indexOf(normalizedQuery);
      if (idx === -1) {
        continue;
      }
      const snippet = buildSnippet(content, idx, normalizedQuery.length);
      const prefix = content.slice(0, idx);
      const line = prefix.split(/\r?\n/).length;
      matches.push({
        path: path.relative(projectDir, file),
        snippet,
        line
      });
      if (matches.length >= maxResults) {
        break;
      }
    }

    if (matches.length === 0) {
      return {
        content: [{ type: "text", text: `在项目 ${project}/${section} 中未找到“${trimmedQuery}”相关内容。` }]
      };
    }

    const lines = matches.map(
      (match, index) => `[${index + 1}] ${match.path}:${match.line}\n${match.snippet}`
    );

    return {
      content: [
        {
          type: "text",
          text: `项目 ${project}/${section} 中“${trimmedQuery}”的匹配：\n\n${lines.join("\n\n")}`
        }
      ]
    };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await mcpServer.connect(transport);
  console.error("MCP server is running over stdio");
}

main().catch(error => {
  console.error("Server failed:", error);
  process.exit(1);
});
