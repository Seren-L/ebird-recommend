"""Development server entry point. Run: python serve.py"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "ebird_recommend.api.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
