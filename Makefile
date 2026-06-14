.PHONY: dev dev-host dev-mcp stop clean

# ── 开发启动 ─────────────────────────────────

dev: dev-mcp
	@echo "Starting MCP Host..."
	cd mcp-hosts/stock-host && python app.py

# 启动所有 MCP Server（后台）
dev-mcp:
	@echo "Starting 5 MCP Servers..."
	cd mcp-servers/market-analyzer && python server.py &
	cd mcp-servers/psychology-mirror && python server.py &
	cd mcp-servers/meme-comfort && python server.py &
	cd mcp-servers/social-tactician && python server.py &
	cd mcp-servers/life-service && python server.py &
	@echo "All MCP Servers started."

# 停止所有进程
stop:
	@echo "Stopping all services..."
	pkill -f "mcp-servers" || true
	pkill -f "stock-host" || true

# 清理
clean:
	rm -rf data/stock_agent.db
	rm -rf __pycache__ */__pycache__ */*/__pycache__

# 安装依赖
install:
	pip install -r mcp-hosts/stock-host/requirements.txt
	pip install mcp anthropic
