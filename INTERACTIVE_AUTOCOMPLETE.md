# Interactive Mode Autocomplete - Documentation

## Overview

The Interactive Mode now features intelligent, context-aware autocomplete that suggests:
- Command names
- Argument flags (--option, -o)
- Scene node names (characters, cameras, props, lights) from your DAZ Studio scene
- Command-specific suggestions based on context

## Features

### 🎯 Context-Aware Completions

The completer understands what you're typing and provides relevant suggestions:

```bash
vangard-cli 🔍> rot[TAB]
  → rotate-render    # Command suggestion

vangard-cli 🔍> rotate-render Gen[TAB]
  → 🧍 Genesis 9     # Scene character suggestion
  → 🧍 Genesis 8 Female

vangard-cli 🔍> copy-camera --source-[TAB]
  → --source-camera  # Flag suggestion

vangard-cli 🔍> copy-camera --source-camera Cam[TAB]
  → 📷 Camera 1      # Only cameras suggested
  → 📷 Camera 2
```

### 🔍 Scene Node Integration

When Script Server is enabled, the completer automatically suggests nodes from your current DAZ scene:

- **Type Filtering**: Only suggests relevant node types
  - `copy-camera` → Only cameras
  - `apply-pose` → Only figures/characters
  - `drop-object` → Props and figures

- **Visual Indicators**: Emoji icons show node types
  - 📷 Camera
  - 💡 Light
  - 🧍 Figure/Character
  - 📦 Prop/Object
  - 🗂️ Group
  - 🦴 Bone

- **Metadata Display**: Shows node type and path in completion menu

### ⚡ Special Commands

Interactive mode includes special commands for cache management:

| Command | Shortcut | Description |
|---------|----------|-------------|
| `.refresh` | `.r` | Force immediate cache refresh |
| `.stats` | `.s` | Show cache statistics |
| `.help` | `.h`, `.?` | Show special commands help |
| `exit` | `quit` | Exit interactive shell |

## Setup

### Prerequisites

1. **DAZ Script Server** (optional, for scene autocomplete)
   - Install plugin from: https://github.com/bluemoonfoundry/vangard-daz-script-server
   - Start server in DAZ Studio

2. **Environment Configuration**
   ```bash
   # .env file
   DAZ_SCRIPT_SERVER_ENABLED=true
   DAZ_SCRIPT_SERVER_HOST=127.0.0.1
   DAZ_SCRIPT_SERVER_PORT=18811
   ```

### Launch Interactive Mode

```bash
vangard-interactive
# or
vangard interactive
# or
python -m vangard.interactive
```

## Usage Examples

### Basic Command Completion

```bash
# Type partial command and press TAB
vangard-cli 🔍> bat[TAB]
  → batch-render

# Complete with metadata shown
vangard-cli 🔍> scene-[TAB]
  scene-render    # Direct render the current scene, or a new...
```

### Flag Completion

```bash
# Type dash and press TAB for flags
vangard-cli 🔍> batch-render -[TAB]
  -s, --scene-files
  -o, --output-path
  -t, --target
  -r, --resolution
  [... more flags ...]

# Complete flag value
vangard-cli 🔍> batch-render --target [TAB]
  direct-file
  local-to-file
  local-to-window
  iray-server-bridge
```

### Scene Node Completion

```bash
# Suggest scene characters
vangard-cli 🔍> rotate-render [TAB]
  🧍 Genesis 9            # figure | Scene/Genesis 9
  🧍 Genesis 8 Female     # figure | Scene/Genesis 8 Female
  📦 Coffee Mug           # prop | Scene/Props/Coffee Mug
  📷 Camera 1             # camera | Scene/Cameras/Camera 1

# Type-filtered suggestions
vangard-cli 🔍> copy-camera --source-camera [TAB]
  📷 Camera 1             # Only cameras suggested
  📷 Camera 2
  📷 Camera 3

vangard-cli 🔍> apply-pose pose.duf --target-node [TAB]
  🧍 Genesis 9            # Only figures suggested
  🧍 Genesis 8 Female
```

### Special Commands

```bash
# Refresh scene cache immediately
vangard-cli 🔍> .refresh
🔄 Refreshing scene cache...
✅ Cache refreshed successfully!
   Total nodes: 42
   Cameras: 3, Lights: 2, Characters: 5

# Show cache statistics
vangard-cli 🔍> .stats
📊 Scene Cache Statistics:
==================================================
Last Update:      2025-01-15T14:32:15.123
Cache Status:     🟢 Fresh
Polling:          🟢 Active
Server:           🟢 Enabled
--------------------------------------------------
Total Nodes:      42
  📷 Cameras:     3
  💡 Lights:      2
  🧍 Characters:  5
  📦 Props:       25
  🗂️  Groups:      7
==================================================

# Show help
vangard-cli 🔍> .help
💡 Special Commands:
==================================================
  .refresh (.r)   - Refresh scene cache immediately
  .stats (.s)     - Show scene cache statistics
  .help (.h, .?)  - Show this help
  exit, quit      - Exit interactive shell
==================================================
```

## How It Works

### Architecture

```
User Input
    ↓
SmartCompleter
    ↓ (analyzes context)
    ├─ Command completion      → Config.yaml
    ├─ Flag completion         → Config.yaml
    └─ Value completion
           ↓
       Scene Cache
           ↓ (filters by type)
       Autocomplete Suggestions
```

### Context Analysis

The completer parses your input to determine:

1. **Position**: Are you typing a command, flag, or value?
2. **Command**: Which command are you using?
3. **Argument**: Which argument are you completing?
4. **Type Filter**: What node types are relevant?

Example:
```bash
rotate-render Gen[cursor]
              ^
              |
Context: Completing positional argument "object_name"
Config: autocomplete.source = "scene-nodes"
        autocomplete.types = ["figure", "prop", "camera"]
Action: Query scene cache for figures, props, cameras
        Filter by "Gen" prefix
Result: Show matching nodes with visual indicators
```

### Intelligent Parsing

The completer handles complex cases:

```bash
# Boolean flags don't consume next token
rotate-render Genesis --skip-render [TAB]
                                     ^
                                     Still completing flags

# Flag values are recognized
rotate-render Genesis --output-file /path[TAB]
                                     ^
                                     Completing flag value

# Positional args counted correctly
transform-copy Source Target [TAB]
                              ^
                              Done with positionals, suggest flags
```

## Configuration

### Add Autocomplete to New Commands

Edit `config.yaml`:

```yaml
arguments:
  - names: ["node_name"]
    dest: "node_name"
    type: "str"
    required: true
    help: "Scene node to operate on"
    ui:
      widget: "text"
    autocomplete:
      source: "scene-nodes"
      types: ["figure", "prop"]  # Optional type filter
```

Supported types:
- `camera` - Cameras only
- `light` - Lights only
- `figure` - Characters/figures
- `prop` - Props/objects
- `group` - Node groups
- Omit `types` for all nodes

### Customize Polling

In `vangard/scene_cache.py`:

```python
scene_cache = SceneCacheManager(
    poll_interval=60,  # Poll every 60 seconds (default: 30)
    cache_ttl=120      # Cache valid for 120 seconds (default: 60)
)
```

Or disable auto-polling:

```python
# In interactive.py, comment out:
# scene_cache.start_polling()

# Use manual refresh only:
# .refresh command in shell
```

## Troubleshooting

### No autocomplete suggestions?

**Check 1: Is TAB working?**
```bash
# Press TAB key to trigger completions
# Completions don't appear while typing
```

**Check 2: Scene cache enabled?**
```bash
vangard-cli 🔍> .stats
# Should show "Server: 🟢 Enabled"
```

**Check 3: DAZ Script Server running?**
- Check DAZ Studio Script Server pane
- Should show "Server Running"

**Check 4: Scene has nodes?**
```bash
vangard-cli 🔍> .stats
# Should show Total Nodes > 0
```

### Outdated suggestions?

```bash
# Manually refresh cache
vangard-cli 🔍> .refresh

# Or wait for auto-refresh (30 seconds)
```

### Wrong suggestions?

**Issue**: Seeing props when expecting cameras

**Cause**: Command not configured with type filter

**Solution**: Check `config.yaml` for `autocomplete.types`

### Completions too slow?

**Cause**: Large scene with many nodes

**Solution**:
1. Increase poll interval
2. Reduce cache query frequency
3. Use type filters to reduce suggestion count

## Performance

### Benchmarks

- **Cache Query**: ~10-50ms for 100-500 nodes
- **Completion Generation**: ~1-5ms
- **Total Latency**: <100ms (feels instant)

### Memory Usage

- **Scene Cache**: ~1-5 MB for typical scenes
- **Completer**: <1 MB
- **Total Overhead**: Minimal

### Scaling

- **Small Scene (10-50 nodes)**: No impact
- **Medium Scene (50-500 nodes)**: Minimal impact
- **Large Scene (500-5000 nodes)**: Slight delay, still usable
- **Very Large Scene (>5000 nodes)**: Consider type filtering

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `TAB` | Show completions |
| `↑` / `↓` | Navigate completion menu |
| `Enter` | Select completion |
| `Esc` | Close completion menu |
| `Ctrl+C` | Cancel current input |
| `Ctrl+D` | Exit shell (EOF) |

## Advanced Features

### History Integration

Commands are saved to `.cli_history` file:

```bash
# Navigate history
↑ arrow    # Previous command
↓ arrow    # Next command

# Search history
Ctrl+R     # Reverse search
```

### Multi-Line Editing

```bash
# Quote for multi-line
vangard-cli 🔍> batch-render \
             --scene-files "*.duf" \
             --output-path /renders/

# Automatic quote handling
vangard-cli 🔍> load-scene "My Scene File.duf"[TAB]
                          ^
                          Quotes preserved
```

### Fuzzy Matching

Completions match prefixes:

```bash
Gen[TAB]     → Genesis 9
             → Genesis 8 Female

Cam[TAB]     → Camera 1
             → Camera 2

Light[TAB]   → Point Light 1
             → Distant Light 1
```

## Comparison with Pro Mode

| Feature | Interactive Mode | Pro Mode |
|---------|------------------|----------|
| Command Completion | ✅ | ✅ |
| Flag Completion | ✅ | ❌ |
| Scene Nodes | ✅ | ✅ |
| Visual Indicators | ✅ (emoji) | ❌ |
| Type Filtering | ✅ | ✅ |
| Real-time Updates | ✅ (30s poll) | ✅ (30s poll) |
| Manual Refresh | ✅ (.refresh) | ✅ (API) |
| Context Awareness | ✅ | ❌ |
| Keyboard Driven | ✅ | ❌ |
| Mouse Support | ❌ | ✅ |

## Best Practices

### 1. Use TAB Liberally

Press TAB frequently to:
- Discover available commands
- See available flags
- Browse scene nodes
- Verify spellings

### 2. Refresh After Scene Changes

After adding/removing nodes in DAZ:
```bash
vangard-cli 🔍> .refresh
```

### 3. Check Cache Status

Periodically verify cache is working:
```bash
vangard-cli 🔍> .stats
```

### 4. Use Type Filters

Commands with type-filtered autocomplete:
- More relevant suggestions
- Faster completions
- Less clutter

### 5. Leverage History

Use `↑` arrow for command history:
- Repeat commands quickly
- Edit previous commands
- Build on past work

## Examples Gallery

### Example 1: Character Rotation

```bash
vangard-cli 🔍> rotate-render [TAB]
  🧍 Genesis 9

vangard-cli 🔍> rotate-render "Genesis 9" [TAB]
  [entering lower angle...]

vangard-cli 🔍> rotate-render "Genesis 9" 0 360 8 --output-file [TAB]
  [entering output path...]

vangard-cli 🔍> rotate-render "Genesis 9" 0 360 8 --output-file /renders/
[Executing command...]
```

### Example 2: Camera Copy

```bash
vangard-cli 🔍> copy-camera --source-camera [TAB]
  📷 Camera 1
  📷 Camera 2
  📷 Overhead Cam

vangard-cli 🔍> copy-camera --source-camera "Camera 1" --target-camera [TAB]
  📷 Camera 2
  📷 Overhead Cam

vangard-cli 🔍> copy-camera --source-camera "Camera 1" --target-camera "Camera 2"
[Executing command...]
```

### Example 3: Cache Management

```bash
# Start shell
vangard-cli 🔍> .stats
📊 Scene Cache Statistics:
Total Nodes: 0  # Empty - first poll hasn't happened

# Wait 30 seconds or force refresh
vangard-cli 🔍> .refresh
✅ Cache refreshed successfully!
   Total nodes: 25

# Now autocomplete works
vangard-cli 🔍> rotate-render [TAB]
  🧍 Genesis 9
  📦 Coffee Mug
  📷 Camera 1
```

## FAQ

**Q: Does autocomplete work without Script Server?**
A: Yes! Command and flag completion work. Only scene node suggestions require Script Server.

**Q: Can I use this with remote DAZ?**
A: Yes, if Script Server is network-accessible. Set `DAZ_SCRIPT_SERVER_HOST` to remote IP.

**Q: Does it slow down typing?**
A: No, completions only appear when you press TAB.

**Q: Can I customize the emoji icons?**
A: Yes, edit `_get_type_emoji()` in `interactive_completer.py`.

**Q: Does it work with quoted paths?**
A: Yes, quotes are handled automatically by shlex parser.

**Q: Can I add custom completions?**
A: Yes, extend `SmartCompleter` class with custom logic.

## Support

- Full implementation: `SCENE_AUTOCOMPLETE_IMPLEMENTATION.md`
- Quick start: `SCENE_AUTOCOMPLETE_QUICKSTART.md`
- Issues: https://github.com/bluemoonfoundry/vangard-script-utils/issues

## Summary

Interactive Mode autocomplete transforms the CLI experience from manual typing to intelligent, context-aware suggestions. With scene node integration, you can quickly select characters, cameras, and props directly from your DAZ scene, making complex commands faster and less error-prone.

**Key Benefits:**
- ✅ Faster command entry
- ✅ Fewer typos
- ✅ Discover available options
- ✅ Context-aware suggestions
- ✅ Visual node type indicators
- ✅ Real-time scene integration

Launch with `vangard-interactive` and press TAB to explore!
