"""Development server entry point.

Usage:
    python serve.py          # no reload (safe for repeated runs)
    python serve.py --reload # hot reload (only one instance at a time!)

Note: --reload spawns a watcher + worker process pair. Running multiple
instances with --reload will stack up zombie processes on port 8000.
Kill all python.exe / uvicorn processes before restarting with --reload.
"""
import sys
import uvicorn

if __name__ == "__main__":
    reload = "--reload" in sys.argv
    uvicorn.run(
        "ebird_recommend.api.app:app",
        host="127.0.0.1",
        port=8000,
        reload=reload,
    )
