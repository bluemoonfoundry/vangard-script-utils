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
                // Also check for default in anyOf items
                if (actualDefault === undefined && nonNullType.default !== undefined) {
                    actualDefault = nonNullType.default;
                }
            }
        }

        // Extract UI metadata from json_schema_extra
        const uiMetadata = prop.ui || prop['x-ui'] || {};
        const autocompleteMetadata = prop.autocomplete || {};

        return {
            name,
            type: actualType || 'string',
            required: required.includes(name),
            description: prop.description || prop.title || '',
            default: actualDefault !== undefined ? actualDefault : prop.default,
            items: prop.items, // For array types
            ui: uiMetadata, // UI widget metadata from config.yaml
            autocomplete: autocompleteMetadata // Autocomplete configuration
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

    // Populate autocomplete for fields that need it
    populateAutocomplete(command.parameters);

    // Hide output panel initially
    document.getElementById('outputPanel').style.display = 'none';
}

function generateFormField(param) {
    const isRequired = param.required;
    const fieldId = `field_${param.name}`;
    const ui = param.ui || {};
    const widget = ui.widget || inferWidget(param);

    let inputHtml = '';

    // Generate input based on widget type
    switch (widget) {
        case 'file-picker':
        case 'folder-picker':
            inputHtml = generateFilePickerInput(fieldId, param, ui);
            break;
        case 'slider':
            inputHtml = generateSliderInput(fieldId, param, ui);
            break;
        case 'spinner':
            inputHtml = generateSpinnerInput(fieldId, param, ui);
            break;
        case 'select':
            inputHtml = generateSelectInput(fieldId, param, ui);
            break;
        case 'checkbox':
            inputHtml = generateCheckboxInput(fieldId, param, ui);
            break;
        case 'radio':
            inputHtml = generateRadioInput(fieldId, param, ui);
            break;
        case 'textarea':
            inputHtml = generateTextareaInput(fieldId, param, ui);
            break;
        case 'number':
            inputHtml = generateNumberInput(fieldId, param, ui);
            break;
        case 'text':
        default:
            inputHtml = generateTextInput(fieldId, param, ui);
            break;
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

// Infer widget type from parameter properties if not explicitly specified
function inferWidget(param) {
    if (param.type === 'boolean') return 'checkbox';
    if (param.type === 'integer' || param.type === 'number') return 'number';
    if (param.type === 'array') return 'text';
    return 'text';
}

// Widget generation functions
function generateTextInput(fieldId, param, ui) {
    const placeholder = ui.placeholder || param.description || '';
    const autocomplete = param.autocomplete || {};
    const hasAutocomplete = autocomplete.source === 'scene-nodes';
    const datalistId = hasAutocomplete ? `${fieldId}_datalist` : '';

    let html = `
        <input
            type="text"
            id="${fieldId}"
            name="${param.name}"
            class="form-input ${hasAutocomplete ? 'has-autocomplete' : ''}"
            ${param.required ? 'required' : ''}
            ${param.default !== undefined && param.default !== null ? `value="${param.default}"` : ''}
            ${placeholder ? `placeholder="${placeholder}"` : ''}
            ${hasAutocomplete ? `list="${datalistId}"` : ''}
            ${hasAutocomplete ? `data-autocomplete-types="${(autocomplete.types || []).join(',')}"` : ''}
        >
    `;

    if (hasAutocomplete) {
        html += `<datalist id="${datalistId}"></datalist>`;
        // Add small helper text
        html += `<small style="color: var(--color-text-muted); font-size: 0.75rem;">
            💡 Type to see scene nodes
        </small>`;
    }

    return html;
}

function generateNumberInput(fieldId, param, ui) {
    const min = ui.min !== undefined ? `min="${ui.min}"` : '';
    const max = ui.max !== undefined ? `max="${ui.max}"` : '';
    const step = ui.step !== undefined ? `step="${ui.step}"` : (param.type === 'integer' ? 'step="1"' : 'step="any"');

    return `
        <input
            type="number"
            id="${fieldId}"
            name="${param.name}"
            class="form-input"
            ${param.required ? 'required' : ''}
            ${param.default !== undefined && param.default !== null ? `value="${param.default}"` : ''}
            ${min}
            ${max}
            ${step}
        >
    `;
}

function generateSpinnerInput(fieldId, param, ui) {
    const min = ui.min !== undefined ? `min="${ui.min}"` : '';
    const max = ui.max !== undefined ? `max="${ui.max}"` : '';
    const step = ui.step || 1;

    return `
        <input
            type="number"
            id="${fieldId}"
            name="${param.name}"
            class="form-input"
            ${param.required ? 'required' : ''}
            ${param.default !== undefined && param.default !== null ? `value="${param.default}"` : ''}
            ${min}
            ${max}
            step="${step}"
        >
    `;
}

function generateSliderInput(fieldId, param, ui) {
    const min = ui.min || 0;
    const max = ui.max || 100;
    const step = ui.step || 1;
    const defaultVal = param.default !== undefined ? param.default : min;
    const showValue = ui.show_value !== false;

    return `
        <div class="slider-container">
            <input
                type="range"
                id="${fieldId}"
                name="${param.name}"
                class="form-slider"
                min="${min}"
                max="${max}"
                step="${step}"
                value="${defaultVal}"
                oninput="updateSliderValue('${fieldId}')"
            >
            ${showValue ? `<span class="slider-value" id="${fieldId}_value">${defaultVal}</span>` : ''}
        </div>
    `;
}

function generateSelectInput(fieldId, param, ui) {
    const choices = ui.choices || [];
    let optionsHtml = '';

    // Handle both simple array and object array formats
    choices.forEach(choice => {
        if (typeof choice === 'string') {
            const selected = param.default === choice ? 'selected' : '';
            optionsHtml += `<option value="${choice}" ${selected}>${choice}</option>`;
        } else if (typeof choice === 'object') {
            const value = choice.value;
            const label = choice.label || value;
            const selected = param.default === value ? 'selected' : '';
            optionsHtml += `<option value="${value}" ${selected}>${label}</option>`;
        }
    });

    return `
        <select
            id="${fieldId}"
            name="${param.name}"
            class="form-input"
            ${param.required ? 'required' : ''}
        >
            ${!param.required ? '<option value="">-- Select --</option>' : ''}
            ${optionsHtml}
        </select>
    `;
}

function generateCheckboxInput(fieldId, param, ui) {
    const checked = param.default === true ? 'checked' : '';
    return `
        <div class="form-checkbox-wrapper">
            <input
                type="checkbox"
                id="${fieldId}"
                name="${param.name}"
                class="form-checkbox"
                ${checked}
            >
            <label for="${fieldId}">${param.description || param.name}</label>
        </div>
    `;
}

function generateRadioInput(fieldId, param, ui) {
    const choices = ui.choices || [];
    let radioHtml = '<div class="radio-group">';

    choices.forEach((choice, index) => {
        const value = typeof choice === 'string' ? choice : choice.value;
        const label = typeof choice === 'string' ? choice : (choice.label || value);
        const radioId = `${fieldId}_${index}`;
        const checked = param.default === value ? 'checked' : '';

        radioHtml += `
            <div class="form-radio-wrapper">
                <input
                    type="radio"
                    id="${radioId}"
                    name="${param.name}"
                    value="${value}"
                    class="form-radio"
                    ${checked}
                    ${param.required ? 'required' : ''}
                >
                <label for="${radioId}">${label}</label>
            </div>
        `;
    });

    radioHtml += '</div>';
    return radioHtml;
}

function generateFilePickerInput(fieldId, param, ui) {
    const isFolder = ui.widget === 'folder-picker' || ui.file_type === 'folder';
    const buttonText = isFolder ? '📁 Browse Folder' : '📄 Browse File';
    const extensions = ui.extensions ? ui.extensions.join(', ') : '';
    const placeholder = ui.placeholder || (isFolder ? 'Enter folder path' : 'Enter file path');

    return `
        <div class="file-picker-wrapper">
            <input
                type="text"
                id="${fieldId}"
                name="${param.name}"
                class="form-input file-picker-input"
                ${param.required ? 'required' : ''}
                ${param.default !== undefined && param.default !== null ? `value="${param.default}"` : ''}
                placeholder="${placeholder}"
            >
            <button
                type="button"
                class="btn btn-secondary file-picker-button"
                onclick="alert('File picker coming soon! For now, please type the path manually.')"
                title="Browse for ${isFolder ? 'folder' : 'file'}"
            >
                ${buttonText}
            </button>
        </div>
        ${extensions ? `<small style="color: var(--color-text-muted); font-size: 0.75rem;">Supported: ${extensions}</small>` : ''}
    `;
}

function generateTextareaInput(fieldId, param, ui) {
    const rows = ui.rows || 4;
    const placeholder = ui.placeholder || param.description || '';

    return `
        <textarea
            id="${fieldId}"
            name="${param.name}"
            class="form-input"
            rows="${rows}"
            ${param.required ? 'required' : ''}
            ${placeholder ? `placeholder="${placeholder}"` : ''}
        >${param.default || ''}</textarea>
    `;
}

// Helper function to update slider value display
function updateSliderValue(fieldId) {
    const slider = document.getElementById(fieldId);
    const valueDisplay = document.getElementById(`${fieldId}_value`);
    if (slider && valueDisplay) {
        valueDisplay.textContent = slider.value;
    }
}

// ============================================
// Autocomplete / Scene Cache Integration
// ============================================

async function populateAutocomplete(parameters) {
    /**
     * Populate autocomplete datalists for parameters that have scene-nodes autocomplete.
     * Fetches scene data from the cache and populates HTML5 datalist elements.
     */
    // Find parameters that need autocomplete
    const autocompleteParams = parameters.filter(p =>
        p.autocomplete && p.autocomplete.source === 'scene-nodes'
    );

    if (autocompleteParams.length === 0) {
        return; // No autocomplete needed
    }

    try {
        // Fetch scene nodes from cache
        const response = await fetch('/api/scene/labels');
        const data = await response.json();

        if (!response.ok || !data.labels) {
            console.warn('Failed to fetch scene labels for autocomplete');
            return;
        }

        const allLabels = data.labels;

        // Populate each autocomplete field
        autocompleteParams.forEach(param => {
            const fieldId = `field_${param.name}`;
            const datalistId = `${fieldId}_datalist`;
            const datalist = document.getElementById(datalistId);

            if (!datalist) {
                console.warn(`Datalist not found for ${param.name}`);
                return;
            }

            // Filter labels by type if specified
            const types = param.autocomplete.types || [];
            let labels = allLabels;

            if (types.length > 0) {
                // Need to fetch full node data to filter by type
                fetchAndFilterNodesByType(datalist, types);
            } else {
                // Use all labels
                populateDatalist(datalist, labels);
            }
        });

    } catch (error) {
        console.error('Error populating autocomplete:', error);
    }
}

async function fetchAndFilterNodesByType(datalist, types) {
    /**
     * Fetch nodes with type information and filter by specified types.
     */
    try {
        // Fetch nodes for each type and combine
        const typeQueries = types.map(type =>
            fetch(`/api/scene/nodes?node_type=${type}`)
                .then(r => r.json())
                .then(d => d.nodes || [])
        );

        const results = await Promise.all(typeQueries);
        const allNodes = results.flat();
        const labels = allNodes.map(n => n.label).filter(Boolean);

        // Remove duplicates
        const uniqueLabels = [...new Set(labels)];

        populateDatalist(datalist, uniqueLabels);
    } catch (error) {
        console.error('Error filtering nodes by type:', error);
    }
}

function populateDatalist(datalist, labels) {
    /**
     * Populate a datalist element with option elements.
     */
    // Clear existing options
    datalist.innerHTML = '';

    // Add new options
    labels.forEach(label => {
        const option = document.createElement('option');
        option.value = label;
        datalist.appendChild(option);
    });
}

// Add refresh button handler if needed
async function refreshSceneCache() {
    /**
     * Manually refresh the scene cache.
     * Can be called from UI or automatically.
     */
    try {
        const response = await fetch('/api/scene/refresh', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            showToast('Scene cache refreshed', 'success');
            // Re-populate autocomplete for current form
            if (state.selectedCommand) {
                populateAutocomplete(state.selectedCommand.parameters);
            }
        } else {
            showToast('Failed to refresh scene cache', 'error');
        }
    } catch (error) {
        console.error('Error refreshing scene cache:', error);
        showToast('Error refreshing scene cache', 'error');
    }
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
