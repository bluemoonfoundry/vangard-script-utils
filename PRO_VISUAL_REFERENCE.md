# Vangard Pro - Visual Reference

## Interface Overview

```
╔════════════════════════════════════════════════════════════════════════╗
║  🎬 Vangard Pro          🔍 [Search...]    🌙  📚                      ║
╠═══════════════════╦════════════════════════════════════════════════════╣
║                   ║                                                    ║
║  Commands    [38] ║           Welcome to Vangard Pro                  ║
║  ───────────────  ║                                                    ║
║                   ║              🎨  (Floating Icon)                   ║
║  🔍 [________]    ║                                                    ║
║                   ║  Professional interface for DAZ Studio automation  ║
║  ┌─────────────┐ ║                                                    ║
║  │ 📦 action   │ ║    ┌──────┐  ┌──────┐  ┌──────┐                  ║
║  │ Execute...  │ ║    │  ⚡  │  │  🎯  │  │  🔄  │                  ║
║  └─────────────┘ ║    │ Fast │  │Visual│  │Real- │                  ║
║                   ║    │  &   │  │ Cmd  │  │ time │                  ║
║  ┌─────────────┐ ║    │Intui-│  │Build-│  │Feed- │                  ║
║  │ 🎬 batch... │ ║    │ tive │  │  er  │  │ back │                  ║
║  │ Batch re... │ ║    └──────┘  └──────┘  └──────┘                  ║
║  └─────────────┘ ║                                                    ║
║                   ║    Select a command from the sidebar to get started║
║  ┌─────────────┐ ║                                                    ║
║  │ 📷 create...│ ║                                                    ║
║  │ Create a... │ ║                                                    ║
║  └─────────────┘ ║                                                    ║
║                   ║                                                    ║
║  ┌─────────────┐ ║                                                    ║
║  │ 💾 save...  │ ║                                                    ║
║  │ Save sce... │ ║                                                    ║
║  └─────────────┘ ║                                                    ║
║        ⋮          ║                                                    ║
║                   ║                                                    ║
║                   ║                                                    ║
╚═══════════════════╩════════════════════════════════════════════════════╝
```

## Command Form View

```
╔════════════════════════════════════════════════════════════════════════╗
║  🎬 Vangard Pro          🔍 [load]         🌙  📚                      ║
╠═══════════════════╦════════════════════════════════════════════════════╣
║                   ║                                                    ║
║  Commands    [38] ║  📂  Load Scene                              ✕    ║
║  ───────────────  ║      Load or merge DAZ Studio scene files         ║
║                   ║  ─────────────────────────────────────────────    ║
║  🔍 [load____]    ║                                                    ║
║                   ║  ┌───────────────────────────────────────────┐   ║
║  ┌─────────────┐ ║  │                                            │   ║
║  │ 📂 load-... │ ║  │  Scene File *  ⓘ                          │   ║
║  │ Load or ... │ ║  │  [________________________________]        │   ║
║  └─────────────┘ ║  │                                            │   ║
║    (ACTIVE)       ║  │  ☐  Merge with existing scene             │   ║
║                   ║  │                                            │   ║
║  ┌─────────────┐ ║  │                                            │   ║
║  │ 📂 saveas   │ ║  │                                            │   ║
║  │ Make a c... │ ║  │                                            │   ║
║  └─────────────┘ ║  │  [Reset]              [ ▶ Execute Command]│   ║
║                   ║  └───────────────────────────────────────────┘   ║
║                   ║                                                    ║
║                   ║  ┌───────────────────────────────────────────┐   ║
║                   ║  │ Output                    🗑️  ▼            │   ║
║                   ║  ├───────────────────────────────────────────┤   ║
║                   ║  │ [14:23:45] Executing load-scene...        │   ║
║                   ║  │ [14:23:46] ✓ Scene loaded successfully    │   ║
║                   ║  │                                            │   ║
║                   ║  └───────────────────────────────────────────┘   ║
║                   ║                                                    ║
╚═══════════════════╩════════════════════════════════════════════════════╝

                                                      ┌─────────────────┐
                                                      │ ✓ Command       │
                                                      │   executed      │
                                                      │   successfully  │
                                                      └─────────────────┘
                                                       (Toast Notification)
```

## Color Scheme Examples

### Dark Theme (Default)
```
Header:    ████ #1e293b (Slate)
Sidebar:   ████ #1e293b (Slate)
Background:████ #0f172a (Dark Slate)
Primary:   ████ #6366f1 (Indigo)
Success:   ████ #10b981 (Green)
Error:     ████ #ef4444 (Red)
Accent:    ████ #8b5cf6 (Purple)
Text:      ████ #f1f5f9 (Light)
```

### Light Theme
```
Header:    ████ #ffffff (White)
Sidebar:   ████ #ffffff (White)
Background:████ #f8fafc (Very Light Blue)
Primary:   ████ #6366f1 (Indigo)
Success:   ████ #10b981 (Green)
Error:     ████ #ef4444 (Red)
Accent:    ████ #8b5cf6 (Purple)
Text:      ████ #0f172a (Dark)
```

## Component Examples

### Command Card (Hover State)
```
┌──────────────────────────────┐
│ 📦  action                   │  ← Icon + Name
│     Execute the specified... │  ← Description (truncated)
└──────────────────────────────┘

Hover Effect:
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ← Indigo background
┃ 📦  action                   ┃  ← White text
┃     Execute the specified... ┃  ← Semi-transparent white
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ← Shadow + Slide right
```

### Form Field Types

**Text Input:**
```
Label *  ⓘ
┌────────────────────────────┐
│ Enter value here...        │
└────────────────────────────┘
```

**Number Input:**
```
Quantity *  ⓘ
┌────────────────────────────┐
│ 42                      ▲▼ │
└────────────────────────────┘
```

**Checkbox:**
```
☑  Merge with existing scene
```

**Array Input:**
```
Files *  ⓘ
┌────────────────────────────┐
│ file1.duf, file2.duf       │
└────────────────────────────┘
Enter multiple values separated by commas
```

### Button States

**Primary Button (Normal):**
```
┌──────────────────────┐
│ ▶ Execute Command    │  ← Indigo background
└──────────────────────┘
```

**Primary Button (Hover):**
```
┏━━━━━━━━━━━━━━━━━━━━━━┓
┃ ▶ Execute Command    ┃  ← Darker indigo + shadow + lift
┗━━━━━━━━━━━━━━━━━━━━━━┛
```

**Secondary Button:**
```
┌──────────────────────┐
│ Reset                │  ← Gray background
└──────────────────────┘
```

### Output Panel

**Collapsed:**
```
┌────────────────────────────────────┐
│ Output              🗑️  ▶          │
└────────────────────────────────────┘
```

**Expanded:**
```
┌────────────────────────────────────┐
│ Output              🗑️  ▼          │
├────────────────────────────────────┤
│ [14:23:45] Executing command...    │  ← Info (blue)
│ [14:23:46] ✓ Success message       │  ← Success (green)
│ [14:23:47] ✕ Error message         │  ← Error (red)
│                                    │
└────────────────────────────────────┘
```

### Toast Notifications

**Success:**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ │ ✓  Command executed    ┃  ← Green left border
┃ │    successfully         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Error:**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ │ ✕  Command failed      ┃  ← Red left border
┃ │    Try again           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Info:**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ │ ⓘ  Loading commands... ┃  ← Blue left border
┗━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Loading Overlay
```
╔════════════════════════════════════╗
║                                    ║
║           ◐  (Spinning)            ║  ← Animated spinner
║                                    ║
║      Executing command...          ║
║                                    ║
╚════════════════════════════════════╝
      (Semi-transparent backdrop)
```

## Icon Mapping

```
Command Type         Icon    Example Commands
─────────────────────────────────────────────
Help/Info            ❓      help
Load/Open            📂      load-scene, load-merge
Save                 💾      save-scene, saveas
Render               🎬      scene-render, batch-render
Batch Operations     📦      batch-render
Create/New           ✨      create-light
Camera               📷      create-cam, copy-camera
Scene                🎭      scene-render
Rotate               🔄      rotate-render
Transform            🔀      transform-copy
Copy                 📋      copy-camera
Paste                📌      paste-transform
Group                🗂️      create-group
Node                 🔗      create-node
Apply                ✅      apply-pose
Pose/Character       🧍      apply-pose
Product/List         🛍️      listproducts
Export               📤      export-scene
Import               📥      import-assets
Action/Execute       ⚡      action
Default              📦      (fallback for unmatched)
```

## Responsive Breakpoints

### Desktop (> 768px)
```
┌─────────┬────────────────────────┐
│ Sidebar │    Main Content        │
│ (320px) │    (flexible)          │
│         │                        │
└─────────┴────────────────────────┘
```

### Tablet/Mobile (< 768px)
```
┌────────────────────────────────┐
│         Sidebar                │
│        (40vh max)              │
├────────────────────────────────┤
│      Main Content              │
│      (scrollable)              │
│                                │
└────────────────────────────────┘
```

## Animation Examples

### Card Hover
- **Transform**: `translateX(4px)` (slide right)
- **Duration**: `150ms`
- **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)`
- **Background**: Color transition to primary
- **Shadow**: Increase shadow depth

### Button Hover
- **Transform**: `translateY(-2px)` (lift up)
- **Duration**: `150ms`
- **Shadow**: Add shadow underneath
- **Background**: Darken color

### Toast Slide-In
- **Initial**: `translateX(400px)` + `opacity: 0`
- **Final**: `translateX(0)` + `opacity: 1`
- **Duration**: `300ms`
- **Easing**: `ease-out`

### Loading Spinner
- **Animation**: `rotate(360deg)`
- **Duration**: `1s`
- **Timing**: `linear`
- **Iteration**: `infinite`

## Typography Scale

```
Logo/Hero:       32px / 2rem    (Bold, Gradient)
Page Title:      30px / 1.875rem (Bold)
Section Header:  24px / 1.5rem   (Semi-bold)
Card Title:      18px / 1.125rem (Semi-bold)
Body Text:       16px / 1rem     (Normal)
Small Text:      14px / 0.875rem (Normal)
Tiny Text:       12px / 0.75rem  (Normal)
Code/Output:     14px / 0.875rem (Monospace)
```

## Shadow Depth System

```
Level 1 (sm):  0 1px 2px rgba(0,0,0,0.05)     [Subtle elements]
Level 2 (md):  0 4px 6px rgba(0,0,0,0.1)      [Cards, inputs]
Level 3 (lg):  0 10px 15px rgba(0,0,0,0.1)    [Modals, panels]
Level 4 (xl):  0 20px 25px rgba(0,0,0,0.1)    [Overlays, toasts]
```

## Border Radius System

```
Small:   6px / 0.375rem  [Tags, badges]
Medium:  8px / 0.5rem    [Inputs, buttons]
Large:   12px / 0.75rem  [Cards]
XLarge:  16px / 1rem     [Panels, modals]
```

## Spacing System

```
XS:  4px  / 0.25rem  [Tight spacing]
SM:  8px  / 0.5rem   [Related items]
MD:  16px / 1rem     [Standard spacing]
LG:  24px / 1.5rem   [Section gaps]
XL:  32px / 2rem     [Major sections]
```

---

**Note**: This is a text-based representation. The actual interface has smooth animations, glassmorphism effects, and vibrant colors that create a professional, modern appearance.
