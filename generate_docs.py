import yaml
import html

def _generate_args_html_details(arguments, command_name):
    """
    Generates a collapsible HTML <details> block containing an arguments table.
    """
    if not arguments:
        return "No arguments."

    arg_count = len(arguments)
    summary_text = f"View {arg_count} Argument{'s' if arg_count > 1 else ''}"
    
    details_block = f'<details><summary>{summary_text}</summary>'
    details_block += '<div style="padding-left: 16px; margin-top: 8px;">'
    details_block += '<table>'
    details_block += '<thead><tr><th>Arg Name</th><th>Description</th><th>Type</th><th>Optional</th></tr></thead>'
    details_block += '<tbody>'

    for arg in arguments:
        arg_names = html.escape(", ".join(arg.get('names', [])))
        arg_desc = html.escape(arg.get('help', ''))
        if arg.get('action') == 'store_true':
            arg_type = 'flag (boolean)'
        else:
            arg_type = arg.get('type', 'string')
        arg_type = html.escape(arg_type)
        is_optional = "No" if arg.get('required', False) else "Yes"
        details_block += f'<tr><td><code>{arg_names}</code></td><td>{arg_desc}</td><td>{arg_type}</td><td>{is_optional}</td></tr>'

    details_block += '</tbody></table></div></details>'
    return details_block

def generate_markdown_table(yaml_file_path, output_md_path):
    """
    Reads a YAML file defining commands, sorts them alphabetically,
    and generates a Markdown table with collapsible sections for arguments.
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

    # --- NEW: SORT THE COMMANDS LIST ---
    # Get the list of commands from the loaded data.
    commands_list = data.get('commands', [])
    # Sort the list of dictionaries alphabetically based on the 'name' key.
    sorted_commands = sorted(commands_list, key=lambda cmd: cmd.get('name', '').lower())

    md_content = "# Command Line Utility Reference\n\n"
    md_content += "| Command Name | Description | Arguments |\n"
    md_content += "|---|---|---|\n"

    # --- UPDATED: Iterate over the newly sorted list ---
    for command in sorted_commands:
        command_name_raw = command.get('name', 'N/A')
        command_name_md = f"`{command_name_raw.replace('|', '\\|')}`"
        command_desc = command.get('help', '').replace('|', '\\|').replace('\n', ' ')

        arguments_details = _generate_args_html_details(command.get('arguments'), command_name_raw)
        
        md_content += f"| {command_name_md} | {command_desc} | {arguments_details} |\n"

    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Successfully generated Markdown documentation at '{output_md_path}'")

# --- Main execution block ---
if __name__ == "__main__":
    YAML_INPUT_FILE = "config.yaml"
    MD_OUTPUT_FILE = "config_reference.md"
    generate_markdown_table(YAML_INPUT_FILE, MD_OUTPUT_FILE)