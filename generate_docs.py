import yaml
import html

def generate_html_table(yaml_file_path, output_html_path):
    """
    Reads a YAML file defining commands and generates an HTML table.

    Args:
        yaml_file_path (str): The path to the input YAML file.
        output_html_path (str): The path to the output HTML file.
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

    # Start building the HTML string with updated styling
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-g">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Command Reference</title>
        <style>
            body { font-family: sans-serif; margin: 2em; }
            h1 { color: #333; }
            /* --- UPDATED STYLES FOR THE MAIN TABLE --- */
            table {
                border-collapse: collapse;
                width: 100%;
                box-shadow: 0 2px 3px #ccc;
                table-layout: fixed; /* Important for fixed column widths */
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
                vertical-align: top;
                overflow-wrap: break-word; /* Handle long content */
            }
            /* Define widths for the main table columns */
            table > thead > tr > th:nth-child(1),
            table > tbody > tr > td:nth-child(1) { width: 20%; } /* Command Name */
            table > thead > tr > th:nth-child(2),
            table > tbody > tr > td:nth-child(2) { width: 50%; } /* Description */
            table > thead > tr > th:nth-child(3),
            table > tbody > tr > td:nth-child(3) { width: 30%; } /* Arguments */

            th { background-color: #f2f2f2; font-weight: bold; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f1f1f1; }
            code { background-color: #eee; padding: 2px 4px; border-radius: 4px; }
            .command-name { font-weight: bold; font-size: 1.1em; }

            /* Styles for the nested arguments table */
            .args-table {
                width: 100%;
                margin: 0;
                box-shadow: none;
                table-layout: fixed;
            }
            .args-table th, .args-table td {
                padding: 8px;
                border: 1px solid #e0e0e0;
                overflow-wrap: break-word;
            }
            .args-table th { background-color: #fafafa; }
            
            /* Define the width for each nested table column */
            .args-table th:nth-child(1), .args-table td:nth-child(1) { width: 25%; } /* Arg Name */
            .args-table th:nth-child(2), .args-table td:nth-child(2) { width: 45%; } /* Description */
            .args-table th:nth-child(3), .args-table td:nth-child(3) { width: 15%; } /* Type */
            .args-table th:nth-child(4), .args-table td:nth-child(4) { width: 15%; } /* Optional */
        </style>
    </head>
    <body>
        <h1>Command Line Utility Reference</h1>
        <table>
            <thead>
                <tr>
                    <th>Command Name</th>
                    <th>Description</th>
                    <th>Arguments</th>
                </tr>
            </thead>
            <tbody>
    """

    # --- NO CHANGES TO THE LOGIC BELOW THIS POINT ---
    
    # Process each command from the YAML file
    for command in data.get('commands', []):
        command_name = html.escape(command.get('name', 'N/A'))
        command_desc = html.escape(command.get('help', ''))

        html_content += f"""
                <tr>
                    <td class="command-name"><code>{command_name}</code></td>
                    <td>{command_desc}</td>
                    <td>
        """

        # Build the embedded table for arguments
        if 'arguments' in command and command['arguments']:
            html_content += """
                        <table class="args-table">
                            <thead>
                                <tr>
                                    <th>Arg Name</th>
                                    <th>Description</th>
                                    <th>Type</th>
                                    <th>Optional</th>
                                </tr>
                            </thead>
                            <tbody>
            """
            for arg in command['arguments']:
                arg_names = ", ".join(arg.get('names', []))
                arg_desc = arg.get('help', '')
                if arg.get('action') == 'store_true':
                    arg_type = 'flag (boolean)'
                else:
                    arg_type = arg.get('type', 'string')
                is_optional = "No" if arg.get('required', False) else "Yes"
                arg_names = html.escape(arg_names)
                arg_desc = html.escape(arg_desc)
                arg_type = html.escape(arg_type)
                
                html_content += f"""
                                <tr>
                                    <td><code>{arg_names}</code></td>
                                    <td>{arg_desc}</td>
                                    <td>{arg_type}</td>
                                    <td>{is_optional}</td>
                                </tr>
                """
            html_content += "</tbody></table>"
        else:
            html_content += "No arguments."

        html_content += "</td></tr>"

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    with open(output_html_path, 'w') as f:
        f.write(html_content)
    print(f"Successfully generated HTML documentation at '{output_html_path}'")

# --- Main execution block with UPDATED filenames ---
if __name__ == "__main__":
    YAML_INPUT_FILE = "config.yaml"
    HTML_OUTPUT_FILE = "config_reference.html"
    generate_html_table(YAML_INPUT_FILE, HTML_OUTPUT_FILE)