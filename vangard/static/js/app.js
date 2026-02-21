/**
 * Vangard Pro - JavaScript Application
 * Handles dynamic UI generation and API interactions
 */

// ============================================
// State Management
// ============================================

const state = {
    commands: [],
    selectedCommand: null,
    theme: localStorage.getItem('theme') || 'dark',
    openApiSchema: null  // Store full schema for $ref resolution
};

// Command icon mapping (emoji-based)
const COMMAND_ICONS = {
    'help': '❓',
    'load': '📂',
    'save': '💾',
    'render': '🎬',
    'batch': '📦',
    'create': '✨',
    'camera': '📷',
    'cam': '📷',
    'scene': '🎭',
    'rotate': '🔄',
    'transform': '🔀',
    'copy': '📋',
    'paste': '📌',
    'group': '🗂️',
    'node': '🔗',
    'apply': '✅',
    'pose': '🧍',
    'product': '🛍️',
    'list': '📋',
    'export': '📤',
    'import': '📥',
    'action': '⚡',
    'default': '📦'
};

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    // Initialize theme
    applyTheme();

    // Load commands from API
    await loadCommands();

    // Setup event listeners
    setupEventListeners();
});

// ============================================
// Theme Management
// ============================================

function applyTheme() {
    if (state.theme === 'light') {
        document.body.classList.add('light-theme');
    } else {
        document.body.classList.remove('light-theme');
    }

    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = state.theme === 'light' ? '☀️' : '🌙';
    }
}

function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', state.theme);
    applyTheme();
}

// ============================================
// API Communication
// ============================================

async function loadCommands() {
    try {
        const response = await fetch('/openapi.json');
        const schema = await response.json();

        // Store full schema for $ref resolution
        state.openApiSchema = schema;

        // Extract commands from OpenAPI schema
        state.commands = Object.entries(schema.paths)
            .filter(([path, _]) => path.startsWith('/api/'))
            .map(([path, operations]) => {
                const commandName = path.replace('/api/', '');
                const postOp = operations.post;

                return {
                    name: commandName,
                    description: postOp.summary || 'No description available',
                    parameters: extractParameters(postOp, schema),
                    icon: getCommandIcon(commandName)
                };
            })
            .sort((a, b) => a.name.localeCompare(b.name));

        renderCommandList();
    } catch (error) {
        console.error('Failed to load commands:', error);
        showToast('Failed to load commands', 'error');
    }
}

function extractParameters(operation, fullSchema) {
    if (!operation.requestBody?.content?.['application/json']?.schema) {
        return [];
    }

    let schema = operation.requestBody.content['application/json'].schema;

    // Resolve $ref if present
    if (schema.$ref) {
        const refPath = schema.$ref.split('/').slice(1); // Remove leading #
        schema = refPath.reduce((obj, key) => obj[key], fullSchema);
    }

    const properties = schema.properties || {};
    const required = schema.required || [];

    return Object.entries(properties).map(([name, prop]) => {
        // Handle anyOf pattern (used for optional nullable fields)
        let actualType = prop.type;
        let actualDefault = prop.default;

        if (prop.anyOf && Array.isArray(prop.anyOf)) {
            // Find the non-null type
            const nonNullType = prop.anyOf.find(t => t.type && t.type !== 'null');
            if (nonNullType) {
                actualType = nonNullType.type;
            }
        }

        return {
            name,
            type: actualType || 'string',
            required: required.includes(name),
            description: prop.description || prop.title || '',
            default: actualDefault !== undefined ? actualDefault : prop.default,
            items: prop.items, // For array types
            uiclass: prop['x-uiclass'] || null // Custom UI widget hint
        };
    });
}

function getCommandIcon(commandName) {
    // Try to match command name with icon keywords
    for (const [keyword, icon] of Object.entries(COMMAND_ICONS)) {
        if (commandName.toLowerCase().includes(keyword)) {
            return icon;
        }
    }
    return COMMAND_ICONS.default;
}

async function executeCommand(commandName, formData) {
    try {
        showLoadingOverlay(true);

        const response = await fetch(`/api/${commandName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        showLoadingOverlay(false);

        if (response.ok) {
            displayOutput(result, 'success');
            showToast('Command executed successfully', 'success');
        } else {
            displayOutput(result, 'error');
            showToast(result.detail || 'Command execution failed', 'error');
        }
    } catch (error) {
        showLoadingOverlay(false);
        console.error('Command execution error:', error);
        displayOutput({ error: error.message }, 'error');
        showToast('An error occurred', 'error');
    }
}

// ============================================
// UI Rendering
// ============================================

function renderCommandList() {
    const commandList = document.getElementById('commandList');
    const commandCount = document.getElementById('commandCount');

    commandCount.textContent = state.commands.length;

    if (state.commands.length === 0) {
        commandList.innerHTML = '<div class="loading"><p>No commands available</p></div>';
        return;
    }

    commandList.innerHTML = state.commands.map(cmd => `
        <div class="command-item" data-command="${cmd.name}">
            <div class="command-item-icon">${cmd.icon}</div>
            <div class="command-item-content">
                <div class="command-item-name">${cmd.name}</div>
                <div class="command-item-desc">${truncate(cmd.description, 50)}</div>
            </div>
        </div>
    `).join('');

    // Add click handlers
    commandList.querySelectorAll('.command-item').forEach(item => {
        item.addEventListener('click', () => {
            const commandName = item.dataset.command;
            selectCommand(commandName);
        });
    });
}

function selectCommand(commandName) {
    const command = state.commands.find(cmd => cmd.name === commandName);
    if (!command) return;

    state.selectedCommand = command;

    // Update active state in sidebar
    document.querySelectorAll('.command-item').forEach(item => {
        item.classList.toggle('active', item.dataset.command === commandName);
    });

    // Hide welcome, show form
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('commandFormContainer').style.display = 'block';

    // Render command form
    renderCommandForm(command);
}

function renderCommandForm(command) {
    // Update header
    document.getElementById('commandIcon').textContent = command.icon;
    document.getElementById('commandName').textContent = command.name;
    document.getElementById('commandDescription').textContent = command.description;

    // Generate form fields
    const formFields = document.getElementById('formFields');

    if (command.parameters.length === 0) {
        formFields.innerHTML = '<p class="no-params">This command has no parameters</p>';
    } else {
        formFields.innerHTML = command.parameters.map(param =>
            generateFormField(param)
        ).join('');
    }

    // Hide output panel initially
    document.getElementById('outputPanel').style.display = 'none';
}

function generateFormField(param) {
    const isRequired = param.required;
    const fieldId = `field_${param.name}`;

    let inputHtml = '';

    // Check for special UI classes first
    if (param.uiclass === 'pick-folder' || param.uiclass === 'pick-file') {
        const buttonText = param.uiclass === 'pick-folder' ? '📁 Browse Folder' : '📄 Browse File';
        inputHtml = `
            <div class="file-picker-wrapper">
                <input
                    type="text"
                    id="${fieldId}"
                    name="${param.name}"
                    class="form-input file-picker-input"
                    ${isRequired ? 'required' : ''}
                    ${param.default !== undefined ? `value="${param.default}"` : ''}
                    placeholder="${param.description || 'Enter or browse for path'}"
                >
                <button
                    type="button"
                    class="btn btn-secondary file-picker-button"
                    onclick="alert('File picker coming soon! For now, please type the path manually.')"
                    title="Browse for ${param.uiclass === 'pick-folder' ? 'folder' : 'file'}"
                >
                    ${buttonText}
                </button>
            </div>
            <small style="color: var(--color-text-muted); font-size: 0.75rem;">
                Tip: You can type the path directly or use the browse button
            </small>
        `;
    } else if (param.type === 'boolean') {
        inputHtml = `
            <div class="form-checkbox-wrapper">
                <input
                    type="checkbox"
                    id="${fieldId}"
                    name="${param.name}"
                    class="form-checkbox"
                    ${param.default === true ? 'checked' : ''}
                >
                <label for="${fieldId}">${param.description || param.name}</label>
            </div>
        `;
    } else if (param.type === 'integer' || param.type === 'number') {
        inputHtml = `
            <input
                type="number"
                id="${fieldId}"
                name="${param.name}"
                class="form-input"
                ${isRequired ? 'required' : ''}
                ${param.default !== undefined ? `value="${param.default}"` : ''}
                ${param.type === 'integer' ? 'step="1"' : 'step="any"'}
            >
        `;
    } else if (param.type === 'array') {
        inputHtml = `
            <input
                type="text"
                id="${fieldId}"
                name="${param.name}"
                class="form-input"
                placeholder="Comma-separated values"
                ${isRequired ? 'required' : ''}
            >
            <small style="color: var(--color-text-muted); font-size: 0.75rem;">
                Enter multiple values separated by commas
            </small>
        `;
    } else {
        // Default to text input
        inputHtml = `
            <input
                type="text"
                id="${fieldId}"
                name="${param.name}"
                class="form-input"
                ${isRequired ? 'required' : ''}
                ${param.default !== undefined ? `value="${param.default}"` : ''}
                placeholder="${param.description || param.name}"
            >
        `;
    }

    return `
        <div class="form-group">
            <label for="${fieldId}" class="form-label">
                ${formatParameterName(param.name)}
                ${isRequired ? '<span class="required-indicator">*</span>' : ''}
                ${param.description ? `<span class="help-icon" title="${param.description}">ⓘ</span>` : ''}
            </label>
            ${inputHtml}
        </div>
    `;
}

function displayOutput(result, type = 'info') {
    const outputPanel = document.getElementById('outputPanel');
    const outputContent = document.getElementById('outputContent');

    outputPanel.style.display = 'block';

    const timestamp = new Date().toLocaleTimeString();
    const outputLine = document.createElement('div');
    outputLine.className = `output-line ${type}`;

    if (typeof result === 'object') {
        outputLine.innerHTML = `<strong>[${timestamp}]</strong> ${JSON.stringify(result, null, 2)}`;
    } else {
        outputLine.innerHTML = `<strong>[${timestamp}]</strong> ${result}`;
    }

    outputContent.appendChild(outputLine);
    outputContent.scrollTop = outputContent.scrollHeight;
}

// ============================================
// Event Handlers
// ============================================

function setupEventListeners() {
    // Theme toggle
    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);

    // Search
    document.getElementById('searchInput')?.addEventListener('input', handleSearch);

    // Close command
    document.getElementById('closeCommand')?.addEventListener('click', closeCommandForm);

    // Form submission
    document.getElementById('commandForm')?.addEventListener('submit', handleFormSubmit);

    // Reset form
    document.getElementById('resetForm')?.addEventListener('click', resetForm);

    // Clear output
    document.getElementById('clearOutput')?.addEventListener('click', clearOutput);

    // Toggle output
    document.getElementById('toggleOutput')?.addEventListener('click', toggleOutput);
}

function handleSearch(event) {
    const query = event.target.value.toLowerCase();

    document.querySelectorAll('.command-item').forEach(item => {
        const name = item.querySelector('.command-item-name').textContent.toLowerCase();
        const desc = item.querySelector('.command-item-desc').textContent.toLowerCase();

        if (name.includes(query) || desc.includes(query)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function closeCommandForm() {
    document.getElementById('welcomeScreen').style.display = 'flex';
    document.getElementById('commandFormContainer').style.display = 'none';

    // Clear active states
    document.querySelectorAll('.command-item').forEach(item => {
        item.classList.remove('active');
    });

    state.selectedCommand = null;
}

async function handleFormSubmit(event) {
    event.preventDefault();

    if (!state.selectedCommand) return;

    const formData = {};
    const form = event.target;
    const formElements = form.elements;

    // Collect form data
    for (let i = 0; i < formElements.length; i++) {
        const element = formElements[i];

        if (element.name) {
            if (element.type === 'checkbox') {
                formData[element.name] = element.checked;
            } else if (element.value !== '') {
                // Check if this is an array parameter
                const param = state.selectedCommand.parameters.find(p => p.name === element.name);
                if (param && param.type === 'array') {
                    // Split comma-separated values
                    formData[element.name] = element.value.split(',').map(v => v.trim());
                } else if (param && (param.type === 'integer' || param.type === 'number')) {
                    formData[element.name] = Number(element.value);
                } else {
                    formData[element.name] = element.value;
                }
            }
        }
    }

    await executeCommand(state.selectedCommand.name, formData);
}

function resetForm() {
    document.getElementById('commandForm').reset();
    document.getElementById('outputPanel').style.display = 'none';
}

function clearOutput() {
    document.getElementById('outputContent').innerHTML = '';
    document.getElementById('outputPanel').style.display = 'none';
}

function toggleOutput() {
    const outputContent = document.getElementById('outputContent');
    const toggleButton = document.getElementById('toggleOutput');

    if (outputContent.style.display === 'none') {
        outputContent.style.display = 'block';
        toggleButton.querySelector('span').textContent = '▼';
    } else {
        outputContent.style.display = 'none';
        toggleButton.querySelector('span').textContent = '▶';
    }
}

// ============================================
// Utility Functions
// ============================================

function showLoadingOverlay(show) {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = show ? 'flex' : 'none';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');

    const icons = {
        success: '✓',
        error: '✕',
        info: 'ⓘ'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
    `;

    container.appendChild(toast);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function truncate(str, length) {
    if (str.length <= length) return str;
    return str.substring(0, length) + '...';
}

function formatParameterName(name) {
    // Convert snake_case or kebab-case to Title Case
    return name
        .replace(/[_-]/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
