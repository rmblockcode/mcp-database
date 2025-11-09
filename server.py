import asyncio
import logging
from src.database import init_db, close_db
from src.tools import mcp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def startup():
    logger.info("Initializing startup process...")
    await init_db()
    logger.info("Database initialized successfully")

async def shutdown():
    logger.info("Shutting down MCP Server...")
    await close_db()
    logger.info("Database connection closed successfully")

if __name__ == "__main__":
    asyncio.run(startup())
    try:
        mcp.run(transport='sse', host='0.0.0.0', port=8000)
    finally:
        asyncio.run(shutdown())