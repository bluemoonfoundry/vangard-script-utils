"""
Scene Cache Manager - Queries DAZ Studio scene hierarchy and caches node information
for autocomplete/typeahead functionality.
"""
import os
import json
import time
import threading
import urllib.request
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class SceneCacheManager:
    """
    Manages cached scene hierarchy data from DAZ Studio.
    Polls the DAZ Script Server periodically when enabled.
    """

    def __init__(self, poll_interval: int = 30, cache_ttl: int = 60):
        """
        Initialize the scene cache manager.

        Args:
            poll_interval: Seconds between automatic polls (default 30)
            cache_ttl: Seconds before cache is considered stale (default 60)
        """
        self.poll_interval = poll_interval
        self.cache_ttl = cache_ttl
        self.cache: Dict[str, List[Dict]] = {
            "all_nodes": [],
            "cameras": [],
            "lights": [],
            "characters": [],
            "props": [],
            "groups": []
        }
        self.last_update: Optional[datetime] = None
        self.polling_enabled = False
        self.polling_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Check if DAZ Script Server is enabled
        self.server_enabled = os.getenv("DAZ_SCRIPT_SERVER_ENABLED", "false").lower() in ("true", "1", "yes")
        self.server_host = os.getenv("DAZ_SCRIPT_SERVER_HOST", "127.0.0.1")
        self.server_port = os.getenv("DAZ_SCRIPT_SERVER_PORT", "18811")
        self.server_url = f"http://{self.server_host}:{self.server_port}/execute"

    def is_cache_stale(self) -> bool:
        """Check if the cache needs refreshing."""
        if self.last_update is None:
            return True
        return datetime.now() - self.last_update > timedelta(seconds=self.cache_ttl)

    def start_polling(self):
        """Start background polling if DAZ Script Server is enabled."""
        if not self.server_enabled:
            print("Scene cache polling disabled: DAZ_SCRIPT_SERVER_ENABLED is false")
            return

        if self.polling_enabled:
            print("Scene cache polling already running")
            return

        self.polling_enabled = True
        self.polling_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.polling_thread.start()
        print(f"Scene cache polling started (interval: {self.poll_interval}s)")

    def stop_polling(self):
        """Stop background polling."""
        self.polling_enabled = False
        if self.polling_thread:
            self.polling_thread.join(timeout=5)
        print("Scene cache polling stopped")

    def _poll_loop(self):
        """Background polling loop."""
        while self.polling_enabled:
            try:
                self.refresh_cache()
            except Exception as e:
                print(f"Error refreshing scene cache: {e}")

            # Sleep in small intervals to allow quick shutdown
            for _ in range(self.poll_interval):
                if not self.polling_enabled:
                    break
                time.sleep(1)

    def refresh_cache(self, force: bool = False) -> bool:
        """
        Refresh the scene cache by querying DAZ Studio.

        Args:
            force: Force refresh even if cache is not stale

        Returns:
            True if cache was refreshed, False otherwise
        """
        if not force and not self.is_cache_stale():
            return False

        if not self.server_enabled:
            return False

        try:
            # Query scene hierarchy from DAZ Studio
            scene_data = self._query_scene_hierarchy()

            with self._lock:
                # Update cache
                self.cache["all_nodes"] = scene_data.get("nodes", [])
                self.cache["cameras"] = [n for n in self.cache["all_nodes"] if n.get("type") == "camera"]
                self.cache["lights"] = [n for n in self.cache["all_nodes"] if n.get("type") == "light"]
                self.cache["characters"] = [n for n in self.cache["all_nodes"] if n.get("type") == "figure"]
                self.cache["props"] = [n for n in self.cache["all_nodes"] if n.get("type") == "prop"]
                self.cache["groups"] = [n for n in self.cache["all_nodes"] if n.get("type") == "group"]
                self.last_update = datetime.now()

            print(f"Scene cache refreshed: {len(self.cache['all_nodes'])} nodes")
            return True

        except Exception as e:
            print(f"Failed to refresh scene cache: {e}")
            return False

    def _query_scene_hierarchy(self) -> Dict:
        """
        Query DAZ Studio for scene hierarchy via inline script.

        Returns:
            Dictionary with scene data
        """
        # Inline DSA script to query scene hierarchy
        dsa_script = """
        // Query Scene Hierarchy - Inline Script
        function querySceneHierarchy() {
            var result = {
                "nodes": [],
                "timestamp": new Date().toISOString()
            };

            var scene = Scene.getPrimarySelection();
            if (!scene) {
                scene = Scene.getScene();
            }

            function getNodeType(node) {
                if (!node) return "unknown";

                var className = node.className();
                if (className.indexOf("DzCamera") >= 0) return "camera";
                if (className.indexOf("DzLight") >= 0) return "light";
                if (className.indexOf("DzSkeleton") >= 0 || className.indexOf("DzFigure") >= 0) return "figure";
                if (className.indexOf("DzBone") >= 0) return "bone";

                // Check if it's a group node
                if (node.getNumNodeChildren() > 0 && !node.getObject()) {
                    return "group";
                }

                // Default to prop if it has geometry
                if (node.getObject()) return "prop";

                return "node";
            }

            function traverseNode(node, depth) {
                if (!node) return;

                var nodeInfo = {
                    "label": node.getLabel(),
                    "name": node.name,
                    "type": getNodeType(node),
                    "path": node.getNodePath(),
                    "visible": node.isVisible(),
                    "selected": node.isSelected(),
                    "depth": depth
                };

                result.nodes.push(nodeInfo);

                // Recursively traverse children
                for (var i = 0; i < node.getNumNodeChildren(); i++) {
                    var child = node.getNodeChild(i);
                    traverseNode(child, depth + 1);
                }
            }

            // Traverse all root nodes in the scene
            var rootNodes = Scene.getNodeList();
            for (var i = 0; i < rootNodes.length; i++) {
                traverseNode(rootNodes[i], 0);
            }

            return JSON.stringify(result);
        }

        // Execute and print result
        print(querySceneHierarchy());
        """

        # Send inline script to DAZ Script Server
        payload = {
            "script": dsa_script,  # Inline script (not scriptFile)
            "args": {}
        }

        req = urllib.request.Request(
            self.server_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        timeout = 10  # 10 second timeout for scene query
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result_text = response.read().decode("utf-8")

            # Parse JSON response from DAZ
            # The print() statement in DSA will be captured in the response
            try:
                result_data = json.loads(result_text)
                return result_data
            except json.JSONDecodeError:
                # If response is not JSON, try to extract JSON from text
                # (DAZ might wrap it in other output)
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                raise ValueError(f"Could not parse JSON from response: {result_text[:200]}")

    def get_nodes(self, node_type: Optional[str] = None, name_filter: Optional[str] = None) -> List[Dict]:
        """
        Get cached nodes, optionally filtered by type and name.

        Args:
            node_type: Filter by type (camera, light, figure, prop, group, all_nodes)
            name_filter: Case-insensitive substring filter for node labels

        Returns:
            List of node dictionaries
        """
        with self._lock:
            # Get nodes by type
            if node_type and node_type in self.cache:
                nodes = self.cache[node_type]
            else:
                nodes = self.cache["all_nodes"]

            # Apply name filter if provided
            if name_filter:
                filter_lower = name_filter.lower()
                nodes = [n for n in nodes if filter_lower in n.get("label", "").lower()]

            return nodes.copy()

    def get_node_labels(self, node_type: Optional[str] = None) -> List[str]:
        """
        Get list of node labels for autocomplete.

        Args:
            node_type: Filter by type (camera, light, figure, prop, group)

        Returns:
            List of node label strings
        """
        nodes = self.get_nodes(node_type)
        return [n["label"] for n in nodes if n.get("label")]

    def get_cache_stats(self) -> Dict:
        """Get statistics about the cache."""
        with self._lock:
            return {
                "last_update": self.last_update.isoformat() if self.last_update else None,
                "is_stale": self.is_cache_stale(),
                "total_nodes": len(self.cache["all_nodes"]),
                "cameras": len(self.cache["cameras"]),
                "lights": len(self.cache["lights"]),
                "characters": len(self.cache["characters"]),
                "props": len(self.cache["props"]),
                "groups": len(self.cache["groups"]),
                "polling_enabled": self.polling_enabled,
                "server_enabled": self.server_enabled
            }


# Global singleton instance
_scene_cache_manager: Optional[SceneCacheManager] = None


def get_scene_cache_manager() -> SceneCacheManager:
    """Get or create the global scene cache manager instance."""
    global _scene_cache_manager
    if _scene_cache_manager is None:
        _scene_cache_manager = SceneCacheManager()
    return _scene_cache_manager
