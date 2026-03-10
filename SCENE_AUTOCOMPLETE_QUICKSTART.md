# Scene Autocomplete - Quick Start Guide

## Overview

Scene autocomplete provides intelligent typeahead suggestions for command arguments that reference DAZ Studio scene nodes (objects, cameras, lights, characters). When you type in a field like "object_name" or "source_camera", the system suggests available nodes from your current DAZ scene.

## Prerequisites

1. **DAZ Script Server Plugin** must be installed and running
   - Available at: https://github.com/bluemoonfoundry/vangard-daz-script-server
   - Must be started within DAZ Studio

2. **Environment Configuration** in `.env` file:
   ```bash
   DAZ_SCRIPT_SERVER_ENABLED=true
   DAZ_SCRIPT_SERVER_HOST=127.0.0.1
   DAZ_SCRIPT_SERVER_PORT=18811
   ```

## Setup (5 minutes)

### Step 1: Enable Script Server

Edit your `.env` file (create if it doesn't exist):

```bash
# Enable DAZ Script Server
DAZ_SCRIPT_SERVER_ENABLED=true
DAZ_SCRIPT_SERVER_HOST=127.0.0.1
DAZ_SCRIPT_SERVER_PORT=18811

# DAZ Studio path (still needed for fallback)
DAZ_ROOT=/path/to/DAZStudio
```

### Step 2: Start DAZ Studio with Script Server

1. Launch DAZ Studio
2. Load the Script Server plugin (Window > Panes (Tabs) > Script Server)
3. Click "Start Server" in the Script Server pane
4. Verify it's running on port 18811

### Step 3: Start Pro Mode

```bash
vangard-pro
```

You should see:
```
Scene cache polling started (interval: 30s)
```

### Step 4: Test It

1. Open http://127.0.0.1:8000/ui
2. Load a scene in DAZ Studio with some objects
3. Wait ~30 seconds for first cache update
4. Select command "rotate-render"
5. Click in "object_name" field
6. Start typing - suggestions appear!

## Verification

### Check Cache Status

```bash
curl http://127.0.0.1:8000/api/scene/stats
```

Should return:
```json
{
  "last_update": "2025-01-15T10:30:45.123",
  "is_stale": false,
  "total_nodes": 25,
  "cameras": 3,
  "lights": 2,
  "characters": 5,
  "props": 10,
  "groups": 5,
  "polling_enabled": true,
  "server_enabled": true
}
```

### Get Available Nodes

```bash
curl http://127.0.0.1:8000/api/scene/labels
```

### Force Refresh

```bash
curl -X POST http://127.0.0.1:8000/api/scene/refresh
```

## Commands with Autocomplete

### 1. rotate-render
- **object_name** → Suggests: Figures, Props, Cameras
- Use case: "Rotate Genesis 9 and render from multiple angles"

### 2. copy-camera
- **source_camera** → Suggests: Cameras only
- **target_camera** → Suggests: Cameras only
- Use case: "Copy settings from Camera 1 to Camera 2"

### 3. drop-object
- **source_node** → Suggests: Props, Figures
- **target_node** → Suggests: Props, Figures
- Use case: "Drop coffee mug onto table"

### 4. transform-copy
- **source_node** → Suggests: All nodes
- **target_node** → Suggests: All nodes
- Use case: "Copy position from one object to another"

### 5. apply-pose
- **target_node** → Suggests: Figures only
- Use case: "Apply sitting pose to Genesis 9"

### 6. face-render-lora
- **node_label** → Suggests: Figures only
- Use case: "Render face angles for LoRA training"

## How It Works

```
DAZ Scene → Script Server → Cache Manager → API → Pro Mode UI
  (Live)    (Query/Poll)      (30s poll)    (JSON)  (Dropdown)
```

1. **Polling**: Every 30 seconds, the cache manager queries DAZ
2. **Caching**: Node data stored in memory, categorized by type
3. **API**: Frontend fetches labels via `/api/scene/labels`
4. **Autocomplete**: HTML5 datalist provides native browser suggestions

## Troubleshooting

### No suggestions appearing?

**Check 1:** Is Script Server enabled?
```bash
curl http://127.0.0.1:8000/api/scene/stats
# Look for: "server_enabled": true
```

**Check 2:** Is DAZ Script Server running?
- Check DAZ Studio Script Server pane
- Should show "Server Running" on port 18811

**Check 3:** Are there nodes in your scene?
```bash
curl http://127.0.0.1:8000/api/scene/labels
# Should return list of node labels
```

**Check 4:** Wait for first poll
- First cache update happens after 30 seconds
- Or manually refresh: `curl -X POST http://127.0.0.1:8000/api/scene/refresh`

### Suggestions are outdated?

**Solution:** Force cache refresh
```bash
curl -X POST http://127.0.0.1:8000/api/scene/refresh
```

Or just wait - cache auto-refreshes every 30 seconds.

### Script Server connection failed?

**Check:**
1. Is DAZ Studio running?
2. Is Script Server plugin active?
3. Is server started in the plugin?
4. Firewall blocking localhost:18811?

**Debug:**
```bash
# Test direct connection
curl http://127.0.0.1:18811/status
```

### Works in Pro Mode but not CLI?

Currently, autocomplete is **only implemented in Pro Mode**. CLI and Interactive mode still work as before (manual typing).

Future enhancement will add autocomplete to Interactive Mode via prompt-toolkit.

## Configuration Options

### Adjust Polling Interval

In `vangard/scene_cache.py`:
```python
scene_cache = SceneCacheManager(
    poll_interval=60,  # Poll every 60 seconds instead of 30
    cache_ttl=120      # Cache valid for 120 seconds
)
```

### Disable Polling (On-Demand Only)

```bash
# Don't start auto-polling
# Cache updates only on manual refresh
```

In `vangard/pro.py`, comment out:
```python
# scene_cache.start_polling()  # Don't auto-poll
```

Then use manual refresh when needed:
```bash
curl -X POST http://127.0.0.1:8000/api/scene/refresh
```

## Performance Tips

### Large Scenes (1000+ nodes)

- Increase poll interval to 60+ seconds
- Query may take 2-5 seconds
- Cache will still be fast once populated

### Multiple Figures

- Each figure adds ~50-100 nodes (body + bones)
- Cache handles 5000+ nodes easily
- Memory usage: ~2-5 MB for large scenes

### Network Latency

- All communication is localhost (127.0.0.1)
- Typical query time: 100-500ms
- No network delays

## Best Practices

### 1. Start Script Server First
Always start DAZ Script Server before launching vangard-pro

### 2. Keep DAZ Open
If DAZ closes, cache becomes stale but Pro Mode continues working

### 3. Refresh After Scene Changes
Add/remove nodes in DAZ? Manually refresh or wait for next poll

### 4. Use Type Filters
Commands filter by node type automatically:
- `copy-camera` only shows cameras
- `apply-pose` only shows figures
- `drop-object` shows props and figures

### 5. Check Stats Periodically
Monitor cache health:
```bash
watch -n 5 curl http://127.0.0.1:8000/api/scene/stats
```

## Adding Autocomplete to New Commands

### Step 1: Update config.yaml

```yaml
arguments:
  - names: ["node_name"]
    dest: "node_name"
    type: "str"
    required: true
    help: "Scene node to operate on"
    ui:
      widget: "text"
      placeholder: "Node name"
    autocomplete:
      source: "scene-nodes"
      types: ["figure", "prop"]  # Optional filter
```

### Step 2: Test

```bash
# Restart server
vangard-pro

# Check new command in UI
# http://127.0.0.1:8000/ui
```

That's it! Autocomplete automatically works.

## FAQ

**Q: Does this work without Script Server?**
A: Yes! Fields work as normal text inputs if Script Server is disabled.

**Q: Does it slow down DAZ Studio?**
A: No. Queries take ~100-500ms every 30 seconds. Minimal impact.

**Q: Can I use it in CLI mode?**
A: Not yet. Currently Pro Mode only. CLI enhancement planned.

**Q: What if DAZ crashes during a query?**
A: Query times out after 10 seconds. Cache retains last good data.

**Q: Can multiple instances share the cache?**
A: Not currently. Each vangard-pro instance has its own cache. Future: Redis cache.

**Q: Does it work with headless DAZ?**
A: Yes, if Script Server plugin is running in headless DAZ.

## Support

- Full documentation: `SCENE_AUTOCOMPLETE_IMPLEMENTATION.md`
- Issues: https://github.com/bluemoonfoundry/vangard-script-utils/issues
- DAZ Script Server: https://github.com/bluemoonfoundry/vangard-daz-script-server

## Summary

Scene autocomplete makes Pro Mode significantly more user-friendly by providing intelligent suggestions based on your actual DAZ scene. Setup takes just a few minutes, and once running, it "just works" - continuously keeping suggestions up-to-date as you modify your scene.

**Required:** DAZ Script Server plugin + 3 lines in `.env`
**Result:** Smart autocomplete in all supported command fields
**Performance:** Minimal overhead, smooth UX
**Compatibility:** Gracefully degrades if Script Server unavailable
