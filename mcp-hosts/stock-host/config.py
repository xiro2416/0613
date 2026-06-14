"""MCP Host 配置 — MCP Server 连接参数。

每个业务 Server 的 STDIO 启动命令。

未来升级:
  - 远程 Server → 改为 URL 配置
  - 负载均衡 → 改为多端点列表
"""

from dataclasses import dataclass


@dataclass
class MCPServerConfig:
    """单个 MCP Server 的连接配置"""
    name: str
    command: str              # 启动命令 (e.g. "python server.py")
    cwd: str                  # 工作目录


# 5 个业务 MCP Server 配置
MCP_SERVERS: dict[str, MCPServerConfig] = {
    "market-analyzer": MCPServerConfig(
        name="market-analyzer",
        command="python server.py",
        cwd="mcp-servers/market-analyzer",
    ),
    "psychology-mirror": MCPServerConfig(
        name="psychology-mirror",
        command="python server.py",
        cwd="mcp-servers/psychology-mirror",
    ),
    "meme-comfort": MCPServerConfig(
        name="meme-comfort",
        command="python server.py",
        cwd="mcp-servers/meme-comfort",
    ),
    "social-tactician": MCPServerConfig(
        name="social-tactician",
        command="python server.py",
        cwd="mcp-servers/social-tactician",
    ),
    "life-service": MCPServerConfig(
        name="life-service",
        command="python server.py",
        cwd="mcp-servers/life-service",
    ),
}
