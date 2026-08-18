"""Backend server CLI entrypoint.

Run this script to start the Uvicorn ASGI server hosting the FastAPI application.

Usage:
    python run.py
    python run.py --host 0.0.0.0 --port 8000 --reload
"""

import argparse
import sys
import uvicorn

from app.config import settings


def main() -> None:
    """Parse CLI arguments and launch Uvicorn."""
    parser = argparse.ArgumentParser(description="Privacy-Preserving FL Platform Backend Server")
    parser.add_argument(
        "--host",
        type=str,
        default=settings.HOST,
        help=f"Host address to bind (default: {settings.HOST})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.PORT,
        help=f"Port to listen on (default: {settings.PORT})",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=True,
        help="Enable auto-reload on code changes (default: True for development)",
    )
    args = parser.parse_args()

    print(f"🚀 Starting {settings.PROJECT_NAME} Backend on http://{args.host}:{args.port}")
    print(f"📖 Interactive Swagger Docs available at http://{args.host}:{args.port}/docs")
    print(f"⚡ Live WebSocket Stream at ws://{args.host}:{args.port}/ws/metrics")

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
