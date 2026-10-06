import sys
import uvicorn
from app.config import settings

# Force UTF-8 on Windows
sys.stdout.reconfigure(encoding="utf-8")

def start():
    print("=" * 65)
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📡 Web Application Dashboard: http://{settings.HOST}:{settings.PORT}")
    print(f"📖 Interactive API Docs:      http://{settings.HOST}:{settings.PORT}/docs")
    print(f"⚙️  MCP JSON-RPC Endpoint:     http://{settings.HOST}:{settings.PORT}/mcp")
    print("=" * 65)
    uvicorn.run(
        "app.web.api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    start()
