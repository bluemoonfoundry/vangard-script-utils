import yaml
import html

def _generate_args_html_table(arguments):
    """
    Generates a complete HTML table string for a list of arguments.
    This string is designed to be embedded within a Markdown table cell.
    """
    if not arguments:
        return "No arguments."

    # Start the HTML table.
    # Using inline styles for basic formatting that works well in Markdown renderers.
    html_table = '<table>'
    html_table += '<thead><tr><th>Arg Name</th><th>Description</th><th>Type</th><th>Optional</th></tr></thead>'
    html_table += '<tbody>'

    # Process each argument and create a table row
    for arg in arguments:
        # It is CRITICAL to escape user-provided content for HTML
        arg_names = html.escape(", ".join(arg.get('names', [])))
        arg_desc = html.escape(arg.get('help', ''))

        if arg.get('action') == 'store_true':
            arg_type = 'flag (boolean)'
        else:
            arg_type = arg.get('type', 'string')
        arg_type = html.escape(arg_type)

        is_optional = "No" if arg.get('required', False) else "Yes"

        # Add the HTML row
        html_table += f'<tr><td><code>{arg_names}</code></td><td>{arg_desc}</td><td>{arg_type}</td><td>{is_optional}</td></tr>'

    html_table += '</tbody></table>'
    return html_table

def generate_markdown_table(yaml_file_path, output_md_path):
    """
    Reads a YAML file defining commands and generates a Markdown table.

    Args:
        yaml_file_path (str): The path to the input YAML file.
        output_md_path (str): The path to the output Markdown file.
    """
    try:
        with open(yaml_file_path, 'r') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: The file '{yaml_file_path}' was not found.")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return

    md_content = "# Command Line Utility Reference\n\n"

    # Main table header
    md_content += "| Command Name | Description | Arguments |\n"
    md_content += "|---|---|---|\n"

    # Process each command
    for command in data.get('commands', []):
        # Sanitize text for the main Markdown table cells
        command_name = f"`{command.get('name', 'N/A').replace('|', '\\|')}`"
        # Remove newlines from description to keep the main table row on one line
        command_desc = command.get('help', '').replace('|', '\\|').replace('\n', ' ')

        # Generate the arguments table as a single HTML string
        arguments_html = _generate_args_html_table(command.get('arguments'))
        
        # Add the complete row to the main table. The HTML string can contain newlines,
        # which is fine as long as the row itself starts and ends with a pipe.
        md_content += f"| {command_name} | {command_desc} | {arguments_html} |\n"

    # Write the final Markdown content to the output file
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Successfully generated Markdown documentation at '{output_md_path}'")

# --- Main execution block ---
if __name__ == "__main__":
    YAML_INPUT_FILE = "config.yaml"
    MD_OUTPUT_FILE = "config_reference.md"
    generate_markdown_table(YAML_INPUT_FILE, MD_OUTPUT_FILE)