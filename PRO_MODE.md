# Vangard Pro Mode

Professional web interface for DAZ Studio automation - designed for users who prefer visual, form-based interactions over command-line interfaces.

## Overview

Vangard Pro is a modern, colorful web interface that provides:

- **Visual Command Discovery**: Browse all available commands with icons and descriptions
- **Dynamic Form Generation**: Automatically generated forms based on command parameters
- **Real-time Validation**: Instant feedback on required fields and input types
- **Professional Design**: Dark theme with glassmorphism effects and smooth animations
- **User-Friendly**: No command-line knowledge required

## Quick Start

### 1. Install the Package

```bash
pip install -e .
```

### 2. Launch Pro Mode

```bash
# Direct launch
vangard-pro

# Or through the main launcher
vangard pro
```

The server will start at: **http://127.0.0.1:8000**

### 3. Open in Browser

Navigate to http://127.0.0.1:8000 in your web browser to access the Pro interface.

## Features

### Command Browser

- **Searchable Command List**: Quickly find commands by name or description
- **Command Icons**: Visual indicators for different command types
- **Organized Categories**: Commands are alphabetically sorted for easy navigation

### Dynamic Forms

- **Auto-generated Forms**: Forms are created automatically from command definitions
- **Input Validation**: Required fields are clearly marked
- **Type-specific Inputs**: Different input types (text, number, checkbox, etc.) based on parameter types
- **Help Tooltips**: Hover over the info icon to see parameter descriptions

### Output Display

- **Real-time Feedback**: See command execution results immediately
- **Syntax Highlighting**: Color-coded output (success, error, info)
- **Collapsible Output**: Hide/show output panel as needed
- **Timestamped Logs**: Each output line includes a timestamp

### User Experience

- **Loading Indicators**: Visual feedback during command execution
- **Toast Notifications**: Non-intrusive success/error messages
- **Theme Toggle**: Switch between dark and light themes
- **Responsive Design**: Works on desktop and tablet devices

## Architecture

```
User Browser
    ↓
vangard/static/index.html (Frontend)
    ↓
JavaScript App (app.js)
    ↓ (HTTP POST)
FastAPI Server (vangard/pro.py)
    ↓
Command Classes
    ↓
DAZ Studio
```

### Technology Stack

**Backend:**
- FastAPI (Web server)
- Python command classes
- Existing Vangard infrastructure

**Frontend:**
- Vanilla JavaScript (no framework dependencies)
- CSS3 with custom properties for theming
- HTML5 semantic markup

### Design System

**Color Palette:**
- Primary: Indigo (#6366f1)
- Success: Emerald Green (#10b981)
- Warning: Amber (#f59e0b)
- Error: Red (#ef4444)
- Accent: Purple (#8b5cf6)

**Visual Style:**
- Dark theme by default (professional for 3D work)
- Glassmorphism effects
- Smooth transitions and animations
- Icon-based visual language

## Usage Guide

### Selecting a Command

1. Browse the command list in the left sidebar
2. Use the search box to filter commands by name or description
3. Click on a command to view its details and form

### Filling Out Forms

1. **Required Fields**: Marked with a red asterisk (*)
2. **Optional Fields**: Can be left empty
3. **Help Icons**: Click the ⓘ icon to see parameter descriptions
4. **Array Inputs**: Enter comma-separated values for array parameters

### Executing Commands

1. Fill out the form with the required parameters
2. Click the "Execute Command" button
3. Watch the loading indicator while the command runs
4. View the results in the output panel below the form

### Viewing Output

- **Success Output**: Displayed in green
- **Error Output**: Displayed in red
- **Info Output**: Displayed in blue
- **Clear Output**: Click the trash icon to clear the output
- **Collapse/Expand**: Click the arrow icon to toggle the output panel

## API Documentation

While using Pro mode, you can also access the interactive API documentation:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

## Customization

### Adding Custom Icons

Edit `/vangard/static/js/app.js` and update the `COMMAND_ICONS` object:

```javascript
const COMMAND_ICONS = {
    'your-command': '🎨',  // Add your custom icon mapping
    // ...
};
```

### Changing Colors

Edit `/vangard/static/css/styles.css` and modify the CSS variables in the `:root` selector:

```css
:root {
    --color-primary: #your-color;
    /* ... */
}
```

### Custom Styling

All styles are in `/vangard/static/css/styles.css`. The CSS is organized into sections:

- Base Styles
- Header
- Sidebar
- Main Content
- Forms
- Output
- Utilities

## Comparison with Other Modes

| Feature | CLI | Interactive | GUI | Server | **Pro** |
|---------|-----|-------------|-----|--------|---------|
| Visual Interface | ❌ | ❌ | ✅ | ❌ | ✅ |
| No Command Syntax | ❌ | ❌ | ✅ | ✅ | ✅ |
| Form-based Input | ❌ | ❌ | ✅ | ✅ | ✅ |
| Modern Design | ❌ | ❌ | ❌ | N/A | ✅ |
| Real-time Feedback | ✅ | ✅ | ✅ | ✅ | ✅ |
| Command Discovery | ❌ | ⚠️ | ⚠️ | ✅ | ✅ |
| API Access | ❌ | ❌ | ❌ | ✅ | ✅ |
| Web-based | ❌ | ❌ | ❌ | ✅ | ✅ |

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, you can modify the port in `/vangard/pro.py`:

```python
uvicorn.run(
    "vangard.pro:app",
    host="127.0.0.1",
    port=8001,  # Change to your preferred port
    # ...
)
```

### Static Files Not Loading

Ensure the static files are properly included in your installation:

```bash
pip install -e . --force-reinstall
```

### Browser Compatibility

Pro mode works best with modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Future Enhancements

Potential features for future versions:

- [ ] Command history and favorites
- [ ] Batch command execution
- [ ] WebSocket support for real-time output streaming
- [ ] File upload widget for file path parameters
- [ ] Command templates and presets
- [ ] Multi-language support
- [ ] Keyboard shortcuts
- [ ] Desktop app packaging (via pywebview or Electron)

## Contributing

To contribute to Pro mode:

1. Frontend code: `/vangard/static/`
2. Backend code: `/vangard/pro.py`
3. Follow the existing code style and design patterns
4. Test in multiple browsers before submitting PRs

## License

Same as the main Vangard project - GNU Affero General Public License v3.0.

---

**Questions or Issues?**

- Check the main [README.md](README.md) for general project information
- Review [CLAUDE.md](CLAUDE.md) for development guidance
- Open an issue on the project repository
