# UI Hints Testing Checklist

## Pre-flight Checks

✅ **Syntax Validation**
- [x] `server.py` - Python syntax valid
- [x] `config.yaml` - YAML syntax valid
- [x] `app.js` - JavaScript (visual inspection)
- [x] `styles.css` - CSS (visual inspection)

## Testing Steps

### 1. Start the Server
```bash
vangard-pro
```

Expected: Server starts on http://127.0.0.1:8000

### 2. Open Pro Interface
Navigate to: http://127.0.0.1:8000/ui

Expected: Pro interface loads successfully

### 3. Test Widget Types

#### A. Slider Widget (rotate-render command)
1. Select "rotate-render" from command list
2. Check "lower" and "upper" parameters

**Verify:**
- [ ] Slider displays horizontally
- [ ] Current value shows next to slider
- [ ] Value updates in real-time when dragging
- [ ] Range is 0-360
- [ ] Step is 15 degrees
- [ ] Default values are set (0 and 180)

#### B. Spinner Widget (rotate-render command)
1. Still on "rotate-render" command
2. Check "slices" parameter

**Verify:**
- [ ] Number input with up/down arrows
- [ ] Can type value directly
- [ ] Can use arrows to increment/decrement
- [ ] Min: 0, Max: 72, Step: 1

#### C. File Picker (load-scene command)
1. Select "load-scene" command
2. Check "scene_file" parameter

**Verify:**
- [ ] Text input + Browse button
- [ ] Browse button shows file icon
- [ ] Placeholder shows expected extensions
- [ ] Small text shows allowed extensions (.duf, .dsx, .dsf)

#### D. Folder Picker (rotate-render command)
1. Select "rotate-render" command
2. Check "output_file" parameter

**Verify:**
- [ ] Text input + Browse button
- [ ] Browse button shows folder icon
- [ ] Labeled as folder picker

#### E. Dropdown/Select (batch-render command)
1. Select "batch-render" command
2. Check "target" parameter

**Verify:**
- [ ] Dropdown shows with down arrow
- [ ] Options: direct-file, local-to-file, local-to-window, iray-server-bridge
- [ ] Each option has descriptive label
- [ ] Default is "direct-file"

#### F. Checkbox (load-scene command)
1. Select "load-scene" command
2. Check "merge" parameter

**Verify:**
- [ ] Checkbox displays
- [ ] Label is next to checkbox
- [ ] Default is unchecked
- [ ] Can toggle on/off

#### G. Text with Placeholder (help command)
1. Select "help" command
2. Check "command_name" parameter

**Verify:**
- [ ] Text input
- [ ] Placeholder shows: "e.g., load-scene, batch-render"

### 4. Form Submission Test

1. Select "rotate-render" command
2. Fill in values:
   - object_name: "TestObject"
   - lower: 45 (use slider)
   - upper: 315 (use slider)
   - slices: 8 (use spinner)
3. Click "Execute Command"

**Verify:**
- [ ] Loading indicator shows
- [ ] Command executes (or shows appropriate error if DAZ not running)
- [ ] Output panel displays result
- [ ] No JavaScript console errors

### 5. Edge Cases

#### A. Empty Optional Fields
1. Select "save-subset" command
2. Fill only required field "subset_file"
3. Leave "directory" and "category" empty
4. Submit

**Verify:**
- [ ] Form submits successfully
- [ ] Optional fields are not included in request

#### B. Numeric Range Validation
1. Select "face-render-lora" command
2. Try to manually enter value outside range in "width" field (e.g., 10000)
3. Submit

**Verify:**
- [ ] Browser validation prevents submission OR
- [ ] Server returns appropriate error

#### C. Default Values Persistence
1. Select "inc-scene" command
2. Check that "increment" shows default value: 1
3. Change to 5
4. Submit
5. Select same command again

**Verify:**
- [ ] Default value resets to 1 (not persisting previous value)

### 6. Cross-browser Testing

Test in multiple browsers:
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari (if on macOS)

**Verify:**
- [ ] Sliders render correctly
- [ ] All widgets functional
- [ ] No console errors

### 7. Theme Compatibility

1. Toggle theme (moon/sun icon in header)
2. Check both light and dark themes

**Verify:**
- [ ] All widgets visible in both themes
- [ ] Text is readable
- [ ] Contrast is adequate
- [ ] Slider thumb is visible

### 8. Responsive Design

1. Resize browser window to narrow width
2. Check form layout

**Verify:**
- [ ] Forms remain usable
- [ ] No horizontal scrolling in form fields
- [ ] Sliders don't break layout

## Known Issues / Limitations

1. **File Picker** - Shows alert "coming soon" when browse button clicked (placeholder until native file picker implemented)
2. **Validation** - Client-side only; server validation may differ
3. **Real-time Updates** - Some fields (like sliders) update display but don't validate until submit

## Success Criteria

✅ All widget types render correctly
✅ Default values populate properly
✅ Form submission works with all widget types
✅ No JavaScript console errors
✅ UI is intuitive and responsive
✅ Works in all major browsers

## Regression Testing

After confirming UI hints work, verify other modes still function:

```bash
# CLI mode
vangard-cli rotate-render TestObject 0 180 8

# Interactive mode
vangard-interactive

# Standard server mode
vangard-server
# Visit http://127.0.0.1:8000/docs
```

**Verify:**
- [ ] CLI executes commands normally
- [ ] Interactive mode works
- [ ] Server mode API docs accessible
- [ ] No breaking changes in non-Pro modes
