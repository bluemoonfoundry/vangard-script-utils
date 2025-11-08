import yaml

def _generate_args_markdown(arguments):
    """
    Generates a Markdown table string for a list of arguments.
    This string is designed to be embedded within a cell of another table.
    """
    if not arguments:
        return "No arguments."

    # CORRECTED: Header for the arguments table, without leading/trailing pipes.
    args_md = "Arg Name | Description | Type | Optional<br>"
    args_md += "--- | --- | --- | ---<br>"

    # Process each argument
    for arg in arguments:
        # Sanitize content for Markdown table (escape the pipe character)
        arg_names = ", ".join(arg.get('names', []))
        arg_names = f"`{arg_names.replace('|', '\\|')}`"
        
        # Also remove newlines from description to keep the row clean
        arg_desc = arg.get('help', '').replace('|', '\\|').replace('\n', ' ')

        if arg.get('action') == 'store_true':
            arg_type = 'flag (boolean)'
        else:
            arg_type = arg.get('type', 'string')
        arg_type = arg_type.replace('|', '\\|')

        is_optional = "No" if arg.get('required', False) else "Yes"

        # CORRECTED: The row string no longer starts or ends with a pipe.
        args_md += f"{arg_names} | {arg_desc} | {arg_type} | {is_optional}<br>"

    # Return the complete string, removing the final <br>
    return args_md.rstrip('<br>')

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

    # Start building the Markdown string
    md_content = "# Command Line Utility Reference\n\n"

    # Main table header
    md_content += "| Command Name | Description | Arguments |\n"
    md_content += "|---|---|---|\n" # Corrected separator line for 3 columns

    # Process each command
    for command in data.get('commands', []):
        # Sanitize command name and description for the main table
        command_name = f"`{command.get('name', 'N/A').replace('|', '\\|')}`"
        command_desc = command.get('help', '').replace('|', '\\|').replace('\n', ' ')

        # Generate the arguments table as a single, multi-line string
        arguments_md = _generate_args_markdown(command.get('arguments'))
        
        # Add the complete row to the main table
        md_content += f"| {command_name} | {command_desc} | {arguments_md} |\n"

    # Write the final Markdown content to the output file
    with open(output_md_path, 'w') as f:
        f.write(md_content)
    print(f"Successfully generated Markdown documentation at '{output_md_path}'")

# --- Main execution block ---
if __name__ == "__main__":
    YAML_INPUT_FILE = "config.yaml"
    MD_OUTPUT_FILE = "config_reference.md"
    generate_markdown_table(YAML_INPUT_FILE, MD_OUTPUT_FILE)