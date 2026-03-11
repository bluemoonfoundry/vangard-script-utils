"""
Vangard Pro Mode - Professional Web Interface
A modern, visual web interface for DAZ Studio automation.
"""
import uvicorn
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from vangard.server import create_fastapi_app
from vangard.scene_cache import get_scene_cache_manager

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

    # Scene Cache Endpoints
    scene_cache = get_scene_cache_manager()

    @app.get("/api/scene/nodes", summary="Get Scene Nodes", tags=["Scene"])
    async def get_scene_nodes(
        node_type: Optional[str] = Query(None, description="Filter by node type: camera, light, figure, prop, group"),
        name_filter: Optional[str] = Query(None, description="Filter nodes by name (case-insensitive)")
    ) -> Dict[str, Any]:
        """
        Get cached scene nodes from DAZ Studio.
        Returns list of nodes with their labels, types, and metadata.
        """
        nodes = scene_cache.get_nodes(node_type=node_type, name_filter=name_filter)
        return {
            "nodes": nodes,
            "count": len(nodes),
            "cache_stats": scene_cache.get_cache_stats()
        }

    @app.get("/api/scene/labels", summary="Get Node Labels", tags=["Scene"])
    async def get_node_labels(
        node_type: Optional[str] = Query(None, description="Filter by node type: camera, light, figure, prop, group")
    ) -> Dict[str, List[str]]:
        """
        Get list of node labels for autocomplete/typeahead.
        Returns simple list of label strings.
        """
        labels = scene_cache.get_node_labels(node_type=node_type)
        return {
            "labels": labels,
            "count": len(labels)
        }

    @app.post("/api/scene/refresh", summary="Refresh Scene Cache", tags=["Scene"])
    async def refresh_scene_cache() -> Dict[str, Any]:
        """
        Force refresh of the scene cache.
        Queries DAZ Studio immediately for current scene state.
        """
        success = scene_cache.refresh_cache(force=True)
        return {
            "success": success,
            "cache_stats": scene_cache.get_cache_stats()
        }

    @app.get("/api/scene/stats", summary="Get Cache Statistics", tags=["Scene"])
    async def get_cache_stats() -> Dict[str, Any]:
        """Get statistics about the scene cache."""
        return scene_cache.get_cache_stats()

    # Startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Start scene cache polling on server startup."""
        scene_cache.start_polling()

    @app.on_event("shutdown")
    async def shutdown_event():
        """Stop scene cache polling on server shutdown."""
        scene_cache.stop_polling()

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
