# Scene Autocomplete Implementation

## Overview

This feature adds intelligent typeahead/autocomplete support for command arguments that reference scene nodes (objects, cameras, lights, characters). When the DAZ Script Server is enabled, the system periodically queries the DAZ Studio scene hierarchy and caches node information, which is then used to provide autocomplete suggestions in Pro Mode and Interactive Mode.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│ DAZ Studio Scene                                          │
│  - Characters/Figures                                     │
│  - Props/Objects                                          │
│  - Cameras                                                │
│  - Lights                                                 │
└────────────┬─────────────────────────────────────────────┘
             │ Query via inline script
             ▼
┌──────────────────────────────────────────────────────────┐
│ DAZ Script Server (Plugin)                                │
│  - HTTP REST API on port 18811                            │
│  - Executes inline DSA scripts                            │
└────────────┬─────────────────────────────────────────────┘
             │ JSON response
             ▼
┌──────────────────────────────────────────────────────────┐
│ SceneCacheManager (vangard/scene_cache.py)                │
│  - Background polling thread (every 30s)                  │
│  - Parses scene hierarchy                                 │
│  - Caches nodes by type                                   │
│  - Provides query methods                                 │
└────────────┬─────────────────────────────────────────────┘
             │ In-memory cache
             ▼
┌──────────────────────────────────────────────────────────┐
│ API Endpoints (vangard/pro.py)                            │
│  - GET /api/scene/nodes                                   │
│  - GET /api/scene/labels                                  │
│  - POST /api/scene/refresh                                │
│  - GET /api/scene/stats                                   │
└────────────┬─────────────────────────────────────────────┘
             │ JSON API
             ▼
┌──────────────────────────────────────────────────────────┐
│ Frontend (app.js / interactive.py)                        │
│  - Fetches node labels                                    │
│  - Populates HTML5 datalist (Pro)                         │
│  - Populates prompt-toolkit completer (Interactive)       │
└──────────────────────────────────────────────────────────┘
```

## Components

### 1. Scene Cache Manager (`vangard/scene_cache.py`)

**SceneCacheManager Class:**
- Polls DAZ Script Server periodically (default: every 30 seconds)
- Executes inline DSA script to query scene hierarchy
- Caches nodes categorized by type: `all_nodes`, `cameras`, `lights`, `characters`, `props`, `groups`
- Provides filtering and query methods
- Thread-safe with locking
- Automatic cache staleness detection (TTL: 60 seconds)

**Key Methods:**
- `start_polling()` - Start background polling thread
- `stop_polling()` - Stop background polling
- `refresh_cache(force=False)` - Refresh cache immediately
- `get_nodes(node_type, name_filter)` - Get cached nodes with filters
- `get_node_labels(node_type)` - Get label list for autocomplete
- `get_cache_stats()` - Get statistics about cache state

**Inline DSA Script:**
The cache manager sends an inline script (not a file) to DAZ that:
1. Traverses all nodes in the scene
2. Identifies node types (camera, light, figure, prop, bone, group)
3. Extracts metadata (label, name, path, visibility, selection state, depth)
4. Returns JSON with scene hierarchy

### 2. API Endpoints (`vangard/pro.py`)

**Scene Endpoints:**
- `GET /api/scene/nodes` - Get all nodes with optional filtering
  - Query params: `node_type` (camera/light/figure/prop/group), `name_filter`
- `GET /api/scene/labels` - Get simple list of node labels for autocomplete
  - Query params: `node_type`
- `POST /api/scene/refresh` - Force immediate cache refresh
- `GET /api/scene/stats` - Get cache statistics and status

**Lifecycle Integration:**
- `@app.on_event("startup")` - Starts polling when server starts
- `@app.on_event("shutdown")` - Stops polling when server shuts down

### 3. Configuration (`config.yaml`)

**Autocomplete Metadata:**
Add `autocomplete` section to arguments that should have scene node suggestions:

```yaml
arguments:
  - names: ["object_name"]
    dest: "object_name"
    type: "str"
    required: true
    help: "Label of the object"
    ui:
      widget: "text"
      placeholder: "Object name"
    autocomplete:
      source: "scene-nodes"
      types: ["figure", "prop"]  # Optional: filter by types
```

**Autocomplete Options:**
- `source`: `"scene-nodes"` - Indicates this field should autocomplete from scene cache
- `types`: Array of node types to include - `["camera", "light", "figure", "prop", "group"]`
  - If omitted, all node types are included

### 4. Backend Integration (`vangard/server.py`)

**Metadata Passing:**
- Extracts `autocomplete` metadata from config.yaml
- Passes through OpenAPI schema via `json_schema_extra`
- Frontend receives autocomplete config for each parameter

```python
autocomplete_metadata = arg.get("autocomplete", {})
json_schema_extra = {}
if autocomplete_metadata:
    json_schema_extra["autocomplete"] = autocomplete_metadata
```

### 5. Frontend Pro Mode (`vangard/static/js/app.js`)

**Autocomplete Integration:**
1. `extractParameters()` - Reads autocomplete metadata from schema
2. `generateTextInput()` - Adds `list` attribute linking to datalist
3. `renderCommandForm()` - Calls `populateAutocomplete()` after rendering
4. `populateAutocomplete()` - Fetches scene labels and populates datalists
5. `fetchAndFilterNodesByType()` - Filters nodes by type if specified

**HTML5 Datalist:**
Uses native browser autocomplete via `<datalist>` element:
```html
<input type="text" list="field_object_name_datalist">
<datalist id="field_object_name_datalist">
  <option value="Genesis9">
  <option value="Camera 1">
  <option value="Point Light">
</datalist>
```

**Benefits:**
- Native browser support
- No external libraries needed
- Works on mobile devices
- Accessible

## Commands with Autocomplete

The following commands have been enhanced with scene node autocomplete:

1. **drop-object**
   - `source_node` - Props/Figures
   - `target_node` - Props/Figures

2. **rotate-render**
   - `object_name` - Figures/Props/Cameras

3. **transform-copy**
   - `source_node` - All nodes
   - `target_node` - All nodes

4. **copy-camera**
   - `source_camera` - Cameras only
   - `target_camera` - Cameras only

5. **apply-pose**
   - `target_node` - Figures only

6. **face-render-lora**
   - `node_label` - Figures only

## Environment Configuration

**Enable DAZ Script Server:**
```bash
# .env file
DAZ_SCRIPT_SERVER_ENABLED=true
DAZ_SCRIPT_SERVER_HOST=127.0.0.1
DAZ_SCRIPT_SERVER_PORT=18811
```

**Without DAZ Script Server:**
- Feature gracefully degrades
- Autocomplete fields work as regular text inputs
- No errors or warnings displayed to users

## Usage Example

### Pro Mode

1. Start Pro Mode with Script Server enabled:
   ```bash
   vangard-pro
   ```

2. Open http://127.0.0.1:8000/ui

3. Select command "rotate-render"

4. Click in the "object_name" field

5. Start typing - autocomplete suggestions appear

6. Select a node from the dropdown or continue typing

### Interactive Mode (Future Enhancement)

```python
# In interactive.py
from prompt_toolkit.completion import WordCompleter
from vangard.scene_cache import get_scene_cache_manager

scene_cache = get_scene_cache_manager()
scene_cache.start_polling()

# Create completer with scene node labels
node_labels = scene_cache.get_node_labels()
completer = WordCompleter(node_labels, ignore_case=True)

# Use with prompt_toolkit session
session.prompt('object_name: ', completer=completer)
```

## Performance Considerations

### Polling Interval
- Default: 30 seconds
- Adjustable via `SceneCacheManager(poll_interval=X)`
- Balance between freshness and DAZ performance

### Cache TTL
- Default: 60 seconds (stale threshold)
- Cache is considered stale if older than TTL
- Forced refresh available via API

### Query Timeout
- 10 second timeout for scene queries
- Prevents hanging if DAZ is unresponsive
- Errors logged but don't crash the server

### Memory Usage
- Scene data cached in memory
- Typical scene: 50-500 nodes
- Memory footprint: < 1 MB for most scenes

## Error Handling

### DAZ Script Server Unavailable
- Polling silently fails
- Cache remains empty
- Autocomplete fields work as plain text inputs
- No error messages shown to user

### Invalid Scene Data
- JSON parsing errors logged
- Cache not updated
- Previous cache data retained
- Fallback to empty suggestions

### Network Timeouts
- 10 second timeout on queries
- Logged to console
- Retry on next poll cycle

## Testing

### Unit Tests
```bash
python -m pytest tests/unit/test_scene_cache.py
```

### Integration Tests
```bash
# Requires DAZ Script Server running
python -m pytest tests/integration/test_scene_cache_integration.py
```

### Manual Testing

1. **Verify Polling Starts:**
   ```bash
   vangard-pro
   # Should see: "Scene cache polling started (interval: 30s)"
   ```

2. **Check Cache Stats:**
   ```bash
   curl http://127.0.0.1:8000/api/scene/stats
   ```

3. **Get Node Labels:**
   ```bash
   curl http://127.0.0.1:8000/api/scene/labels
   ```

4. **Force Refresh:**
   ```bash
   curl -X POST http://127.0.0.1:8000/api/scene/refresh
   ```

5. **Filter by Type:**
   ```bash
   curl "http://127.0.0.1:8000/api/scene/nodes?node_type=camera"
   ```

## Future Enhancements

### 1. Scene Change Detection
Monitor scene for changes (node added/removed/renamed) and auto-refresh cache

### 2. Interactive Mode Integration
Full integration with prompt-toolkit for CLI autocomplete

### 3. Hierarchy Awareness
Show node paths in autocomplete (e.g., "Scene/Genesis 9/Hair")

### 4. Recent Nodes Priority
Prioritize recently used/selected nodes in suggestions

### 5. Smart Filtering
Context-aware filtering based on command (e.g., only show applicable node types)

### 6. Icon Indicators
Show icons next to node labels indicating type (📷 camera, 💡 light, 🧍 figure)

### 7. Caching Strategy
Implement redis or file-based caching for multi-instance deployments

### 8. WebSocket Updates
Push scene updates to frontend in real-time instead of polling

## Troubleshooting

### Issue: Autocomplete not appearing

**Check:**
1. Is DAZ Script Server enabled? (`DAZ_SCRIPT_SERVER_ENABLED=true`)
2. Is DAZ Script Server running? (Check DAZ Studio plugin)
3. Is polling active? (Check `/api/scene/stats`)
4. Are there nodes in the scene? (Empty scene = no suggestions)

**Debug:**
```bash
# Check cache stats
curl http://127.0.0.1:8000/api/scene/stats

# Check if labels exist
curl http://127.0.0.1:8000/api/scene/labels

# Force refresh
curl -X POST http://127.0.0.1:8000/api/scene/refresh
```

### Issue: Polling not starting

**Check:**
1. Environment variable set correctly
2. DAZ Script Server accessible at configured host:port
3. Network firewall not blocking localhost:18811

**Solution:**
Set environment variable explicitly before starting:
```bash
export DAZ_SCRIPT_SERVER_ENABLED=true
vangard-pro
```

### Issue: Stale data

**Cause:** Cache TTL expired, polling failed

**Solution:**
```bash
# Manual refresh
curl -X POST http://127.0.0.1:8000/api/scene/refresh
```

## Security Considerations

### Localhost Only
- Default: Server binds to 127.0.0.1
- Not exposed to network
- Safe for single-user workstation use

### No Authentication
- Current implementation has no auth
- Suitable for local development only
- **Do not expose to internet without authentication**

### Inline Script Execution
- Script is hardcoded, not user-provided
- No script injection vulnerabilities
- Safe to execute in DAZ

## Files Modified/Created

### New Files:
- `vangard/scene_cache.py` - Scene cache manager
- `SCENE_AUTOCOMPLETE_IMPLEMENTATION.md` - This documentation

### Modified Files:
- `vangard/pro.py` - Added scene endpoints and lifecycle hooks
- `vangard/server.py` - Pass autocomplete metadata through schema
- `vangard/static/js/app.js` - Frontend autocomplete integration
- `config.yaml` - Added autocomplete hints to 6 commands

### Test Files (to be created):
- `tests/unit/test_scene_cache.py`
- `tests/integration/test_scene_cache_integration.py`

## Summary

The scene autocomplete feature provides intelligent suggestions for command arguments that reference scene nodes. By leveraging the DAZ Script Server plugin, the system maintains an up-to-date cache of scene hierarchy, enabling smooth typeahead experiences in Pro Mode. The implementation is designed to gracefully degrade when the Script Server is unavailable, ensuring the system remains functional in all scenarios.
