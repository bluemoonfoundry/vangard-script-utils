# Interactive Autocomplete - Test Checklist

## Pre-Test Setup

### Environment
- [ ] DAZ Studio installed and running
- [ ] DAZ Script Server plugin installed
- [ ] Script Server started in DAZ Studio (port 18811)
- [ ] `.env` file configured:
  ```bash
  DAZ_SCRIPT_SERVER_ENABLED=true
  DAZ_SCRIPT_SERVER_HOST=127.0.0.1
  DAZ_SCRIPT_SERVER_PORT=18811
  ```

### Test Scene
- [ ] Load a test scene with:
  - At least 2 characters (e.g., Genesis 9, Genesis 8)
  - At least 2 cameras
  - At least 1 light
  - At least 3 props
  - At least 1 group

## Launch Tests

### Test 1: Startup with Script Server Enabled

```bash
vangard-interactive
```

**Expected Output:**
```
============================================================
🚀 Vangard Interactive Shell
============================================================

🔍 Starting scene cache for smart autocomplete...
   Cache polling started - scene nodes will be suggested as you type

Commands:
  - Type any vangard command (press TAB for suggestions)
  - 'exit' or 'quit' - Exit the shell
  - '.refresh' - Refresh scene cache immediately
  - '.stats' - Show scene cache statistics
============================================================

vangard-cli 🔍>
```

**Verify:**
- [ ] Welcome banner displays
- [ ] "Starting scene cache" message shows
- [ ] Special commands listed
- [ ] Prompt shows with 🔍 indicator
- [ ] Prompt is colored (indigo/blue)
- [ ] No error messages

### Test 2: Startup without Script Server

Disable in `.env`:
```bash
DAZ_SCRIPT_SERVER_ENABLED=false
```

```bash
vangard-interactive
```

**Expected Output:**
```
============================================================
🚀 Vangard Interactive Shell
============================================================

💡 Tip: Enable DAZ_SCRIPT_SERVER for scene node autocomplete

Commands:
  - Type any vangard command (press TAB for suggestions)
  - 'exit' or 'quit' - Exit the shell
============================================================

vangard-cli>
```

**Verify:**
- [ ] Tip message shows instead of cache startup
- [ ] No 🔍 indicator in prompt
- [ ] Special cache commands NOT listed
- [ ] No error messages
- [ ] Shell still functional

## Command Completion Tests

### Test 3: Basic Command Completion

```bash
vangard-cli 🔍> rot[TAB]
```

**Expected:**
- [ ] Shows `rotate-random` and `rotate-render` suggestions
- [ ] Pressing TAB cycles through matches
- [ ] Help text shown in menu
- [ ] Completion inserts full command name

### Test 4: Partial Match Completion

```bash
vangard-cli 🔍> bat[TAB]
```

**Expected:**
- [ ] Completes to `batch-render`
- [ ] Help text: "Given a pattern of scene files..."

### Test 5: Ambiguous Completion

```bash
vangard-cli 🔍> load[TAB]
```

**Expected:**
- [ ] Shows `load-scene` (only match)
- [ ] Auto-completes immediately

### Test 6: No Match

```bash
vangard-cli 🔍> xyz[TAB]
```

**Expected:**
- [ ] No suggestions appear
- [ ] No error
- [ ] Input remains unchanged

## Flag Completion Tests

### Test 7: Flag After Command

```bash
vangard-cli 🔍> batch-render -[TAB]
```

**Expected:**
- [ ] Shows all flags for batch-render
- [ ] Includes short flags (-s, -o, -t, etc.)
- [ ] Includes long flags (--scene-files, --output-path, etc.)
- [ ] Help text shown for each flag

### Test 8: Long Flag Completion

```bash
vangard-cli 🔍> batch-render --out[TAB]
```

**Expected:**
- [ ] Completes to `--output-path`
- [ ] Help text: "Path to directory where output..."

### Test 9: Multiple Flags

```bash
vangard-cli 🔍> batch-render --scene-files test.duf -[TAB]
```

**Expected:**
- [ ] Shows remaining flags (excluding --scene-files)
- [ ] Can continue adding flags

## Scene Node Completion Tests

*Re-enable Script Server for these tests*

### Test 10: Wait for Initial Cache

```bash
vangard-cli 🔍> .stats
```

**First check (within 10 seconds):**
- [ ] Last Update: Never or stale
- [ ] Total Nodes: 0

**Wait 30 seconds, then:**
```bash
vangard-cli 🔍> .stats
```

**Second check:**
- [ ] Last Update: Recent timestamp
- [ ] Total Nodes: > 0
- [ ] Correct counts for cameras, lights, characters, props

### Test 11: Scene Node Suggestions

```bash
vangard-cli 🔍> rotate-render [TAB]
```

**Expected:**
- [ ] Shows scene node suggestions
- [ ] Emoji icons displayed (📷 🧍 📦)
- [ ] Node types shown in metadata
- [ ] Nodes from loaded scene appear

### Test 12: Type Filtering - Cameras Only

```bash
vangard-cli 🔍> copy-camera --source-camera [TAB]
```

**Expected:**
- [ ] Shows ONLY cameras (📷 icon)
- [ ] No characters, props, or lights shown
- [ ] Matches scene cameras

### Test 13: Type Filtering - Figures Only

```bash
vangard-cli 🔍> apply-pose pose.duf --target-node [TAB]
```

**Expected:**
- [ ] Shows ONLY figures/characters (🧍 icon)
- [ ] No cameras, props, or lights shown
- [ ] Matches scene characters

### Test 14: Type Filtering - Props and Figures

```bash
vangard-cli 🔍> drop-object [TAB]
```

**Expected:**
- [ ] Shows props (📦) and figures (🧍)
- [ ] No cameras or lights shown

### Test 15: Partial Node Name Match

```bash
vangard-cli 🔍> rotate-render Gen[TAB]
```

**Expected:**
- [ ] Shows Genesis 9, Genesis 8, etc.
- [ ] Filters by "Gen" prefix
- [ ] Case-insensitive matching

### Test 16: Quoted Node Names

```bash
vangard-cli 🔍> rotate-render "Genesis 9"[TAB]
```

**Expected:**
- [ ] Quote handling works
- [ ] Completion respects quotes
- [ ] Can complete inside quotes

## Special Command Tests

### Test 17: Manual Cache Refresh

```bash
vangard-cli 🔍> .refresh
```

**Expected:**
```
🔄 Refreshing scene cache...
✅ Cache refreshed successfully!
   Total nodes: 25
   Cameras: 3, Lights: 2, Characters: 5
```

**Verify:**
- [ ] Refresh completes quickly (<3 seconds)
- [ ] Node counts displayed
- [ ] Success message shown

### Test 18: Refresh Without Server

Disable Script Server, then:

```bash
vangard-cli> .refresh
```

**Expected:**
```
❌ Scene cache is not enabled. Set DAZ_SCRIPT_SERVER_ENABLED=true
```

**Verify:**
- [ ] Clear error message
- [ ] No crash
- [ ] Shell remains functional

### Test 19: Cache Statistics

```bash
vangard-cli 🔍> .stats
```

**Expected:**
```
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
```

**Verify:**
- [ ] All statistics shown
- [ ] Status indicators displayed
- [ ] Counts match scene content
- [ ] Recent timestamp

### Test 20: Special Commands Help

```bash
vangard-cli 🔍> .help
```

**Expected:**
```
💡 Special Commands:
==================================================
  .refresh (.r)   - Refresh scene cache immediately
  .stats (.s)     - Show scene cache statistics
  .help (.h, .?)  - Show this help
  exit, quit      - Exit interactive shell
==================================================
```

**Verify:**
- [ ] All commands listed
- [ ] Shortcuts shown
- [ ] Descriptions clear

### Test 21: Invalid Special Command

```bash
vangard-cli 🔍> .invalid
```

**Expected:**
```
❌ Unknown special command: .invalid
   Type '.help' for available special commands
```

**Verify:**
- [ ] Error message shown
- [ ] Suggests .help
- [ ] No crash

## Integration Tests

### Test 22: Full Command Execution

```bash
vangard-cli 🔍> rotate-render [TAB, select Genesis 9] 0 360 8
```

**Expected:**
- [ ] Autocomplete works
- [ ] Command executes normally
- [ ] DAZ Studio responds
- [ ] Output displayed

### Test 23: History Persistence

```bash
# Enter command
vangard-cli 🔍> load-scene test.duf

# Exit shell
vangard-cli 🔍> exit

# Restart shell
vangard-interactive

# Press UP arrow
```

**Expected:**
- [ ] Previous command appears
- [ ] History saved to .cli_history file
- [ ] Can execute historical commands

### Test 24: Multi-Argument Completion

```bash
vangard-cli 🔍> transform-copy [TAB, select node1] [TAB, select node2] -[TAB]
```

**Expected:**
- [ ] First positional: node suggestions
- [ ] Second positional: node suggestions
- [ ] After args: flag suggestions
- [ ] Context correctly tracked

### Test 25: Scene Changes Reflected

1. Note a node name from autocomplete
2. In DAZ Studio, rename or delete that node
3. In shell:
   ```bash
   vangard-cli 🔍> .refresh
   ```
4. Try autocomplete again

**Expected:**
- [ ] Old node name disappears
- [ ] New node name appears
- [ ] Cache reflects current scene state

## Error Handling Tests

### Test 26: DAZ Studio Closed

1. Start shell with cache enabled
2. Close DAZ Studio
3. Try autocomplete

**Expected:**
- [ ] Autocomplete still works (uses cached data)
- [ ] No error messages
- [ ] Eventual cache becomes stale
- [ ] Commands show previous suggestions

### Test 27: Script Server Stopped

1. Start shell with cache enabled
2. Stop Script Server in DAZ
3. Try `.refresh`

**Expected:**
```
❌ Failed to refresh cache. Is DAZ Studio running with Script Server?
```

**Verify:**
- [ ] Clear error message
- [ ] Shell remains functional
- [ ] Old cache data retained

### Test 28: Large Scene Performance

Load scene with 500+ nodes, then:

```bash
vangard-cli 🔍> rotate-render [TAB]
```

**Expected:**
- [ ] Autocomplete still responsive (<500ms)
- [ ] All nodes suggested (may be paginated)
- [ ] No lag in typing
- [ ] No memory issues

## Cleanup Tests

### Test 29: Graceful Exit

```bash
vangard-cli 🔍> exit
```

**Expected:**
```
🛑 Stopping scene cache polling...

👋 Goodbye!
============================================================
```

**Verify:**
- [ ] Polling stopped message
- [ ] Goodbye banner
- [ ] No error messages
- [ ] Clean exit (code 0)

### Test 30: Ctrl+C Handling

```bash
vangard-cli 🔍> some-partial-command[Ctrl+C]
```

**Expected:**
- [ ] Input cancelled
- [ ] New prompt appears
- [ ] Shell continues running
- [ ] No crash

### Test 31: Ctrl+D Exit

```bash
vangard-cli 🔍> [Ctrl+D]
```

**Expected:**
- [ ] Same as 'exit' command
- [ ] Clean shutdown
- [ ] Polling stopped

## Edge Cases

### Test 32: Empty Scene

Load empty scene in DAZ, then:

```bash
vangard-cli 🔍> .refresh
vangard-cli 🔍> rotate-render [TAB]
```

**Expected:**
- [ ] Cache refreshes (0 nodes)
- [ ] No suggestions appear
- [ ] No error
- [ ] Shell functional

### Test 33: Special Characters in Names

If scene has node with special chars like "Object (1)", test:

```bash
vangard-cli 🔍> rotate-render Obj[TAB]
```

**Expected:**
- [ ] Node with special chars appears
- [ ] Proper quoting applied
- [ ] Can select and execute

### Test 34: Very Long Node Names

If scene has node with 50+ character name:

```bash
vangard-cli 🔍> rotate-render [TAB]
```

**Expected:**
- [ ] Long names displayed (may truncate in menu)
- [ ] Can still select
- [ ] No layout issues

## Performance Benchmarks

### Test 35: Cold Start Time

```bash
time vangard-interactive <<< "exit"
```

**Expected:**
- [ ] Starts in <2 seconds
- [ ] Cache initialization doesn't block startup
- [ ] Responsive immediately

### Test 36: First Completion Time

Start shell, immediately:

```bash
vangard-cli 🔍> rot[TAB]
```

**Expected:**
- [ ] Suggestions appear <100ms
- [ ] No noticeable delay

### Test 37: Scene Cache Query Time

```bash
vangard-cli 🔍> .stats  # Note last update time
# Wait 30 seconds for auto-poll
vangard-cli 🔍> .stats  # Check new update time
```

**Expected:**
- [ ] Poll completes within 1-2 seconds
- [ ] No impact on typing
- [ ] Cache updates successfully

## Success Criteria

**Minimum Requirements:**
- [ ] All command completions work
- [ ] All flag completions work
- [ ] Scene cache starts successfully
- [ ] Scene node suggestions appear
- [ ] Type filtering works correctly
- [ ] Special commands function
- [ ] Graceful exit
- [ ] No crashes or errors

**Performance Requirements:**
- [ ] Startup <2 seconds
- [ ] Completions <100ms
- [ ] Cache refresh <3 seconds
- [ ] No typing lag

**UX Requirements:**
- [ ] Visual indicators (emojis) displayed
- [ ] Colored prompt
- [ ] Clear error messages
- [ ] Helpful feedback

## Regression Testing

After confirming interactive mode works, verify other modes:

```bash
# CLI mode still works
vangard-cli rotate-render Genesis 0 360 8

# Pro mode still works
vangard-pro
# Open http://127.0.0.1:8000/ui

# Server mode still works
vangard-server
# Check http://127.0.0.1:8000/docs
```

**Verify:**
- [ ] CLI executes normally
- [ ] Pro mode loads
- [ ] Server mode starts
- [ ] No breaking changes

## Notes

- Test on both macOS and Windows if possible
- Test with both Python 3.8+ versions
- Document any failures or unexpected behavior
- Check memory usage during extended sessions
- Monitor CPU usage during autocomplete

## Report Template

```
Environment:
- OS:
- Python Version:
- DAZ Studio Version:
- Script Server Status:

Tests Passed: X/37
Tests Failed: Y/37

Failures:
1. Test #X: [Description]
   Expected: [...]
   Actual: [...]

Performance:
- Startup Time: Xs
- First Completion: Xms
- Cache Refresh: Xs

Issues:
- [Any bugs or concerns]

Overall Status: ✅ PASS / ❌ FAIL
```
