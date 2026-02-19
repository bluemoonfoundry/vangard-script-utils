"""
Vangard Pro Mode - Professional Web Interface
A modern, visual web interface for DAZ Studio automation.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os
from pathlib import Path

from vangard.server import create_fastapi_app

def create_pro_app():
    """
    Creates a FastAPI app that serves both the API and the Pro web interface.
    """
    # Get the base API app with all command endpoints
    app = create_fastapi_app()

    # Update app metadata for Pro mode
    app.title = "Vangard Pro - Professional DAZ Studio Interface"
    app.description = "Modern visual interface for DAZ Studio automation commands"

    # Determine the static files directory
    static_dir = Path(__file__).parent / "static"

    # Mount static files (CSS, JS, assets)
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/ui", response_class=HTMLResponse, include_in_schema=False, tags=["Pro Interface"])
    async def serve_pro_interface():
        """Serve the Pro web interface."""
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            # Fallback message if static files aren't set up yet
            return HTMLResponse("""
            <html>
                <head><title>Vangard Pro</title></head>
                <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                    <h1>Vangard Pro Interface</h1>
                    <p>Static files not found. Please ensure the static/ directory exists.</p>
                    <p>API documentation available at: <a href="/docs">/docs</a></p>
                </body>
            </html>
            """)

    # Override the root to redirect to UI
    from fastapi.responses import RedirectResponse

    @app.get("/pro", response_class=HTMLResponse, include_in_schema=False)
    async def redirect_to_ui():
        """Redirect /pro to /ui for convenience."""
        return RedirectResponse(url="/ui")

    return app

# Create the app instance
app = create_pro_app()

def main():
    """
    Main entry point for Vangard Pro mode.
    Launches the FastAPI server with the Pro web interface.
    """
    print("=" * 60)
    print("🚀 Vangard Pro - Professional Interface")
    print("=" * 60)
    print()
    print("Starting server...")
    print()
    print("📱 Pro Interface:    http://127.0.0.1:8000/ui")
    print("📚 API Docs:         http://127.0.0.1:8000/docs")
    print("💡 Health Check:     http://127.0.0.1:8000/")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    uvicorn.run(
        "vangard.pro:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
