# gui.py
import tkinter as tk
from tkinter import scrolledtext
import shlex
import argparse
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

from core.framework import load_config, build_parser, run_command

class App(tk.Tk):
    """A Tkinter GUI wrapper with completion, hinting, and command history."""

    def __init__(self):
        super().__init__()

        # --- Load Framework ---
        try:
            self.config = load_config()
            self.parser = build_parser(self.config)
        except SystemExit:
            self.destroy()
            return

        # --- Setup for Features ---
        self.setup_completions()
        # --- NEW: Command History Setup ---
        self.command_history = []
        self.history_index = 0
        self.current_command_buffer = ""
            
        # --- Window Setup ---
        self.title(self.config.get("app", {}).get("prog", "GUI Command Shell"))
        self.geometry("800x600")

        # --- Widget Creation ---
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.output_text = scrolledtext.ScrolledText(main_frame, state=tk.DISABLED, wrap=tk.WORD, font=("monospace", 10))
        self.output_text.pack(fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        prompt_label = tk.Label(input_frame, text=">", font=("monospace", 12))
        prompt_label.pack(side=tk.LEFT)
        
        self.input_var = tk.StringVar()
        self.input_var.trace_add("write", self.update_hint)
        
        self.entry = tk.Entry(input_frame, font=("monospace", 12), textvariable=self.input_var)
        self.entry.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(5, 0))
        self.entry.focus_set()

        self.hint_label = tk.Label(main_frame, font=("monospace", 12), fg="grey", anchor="w")
        self.hint_label.pack(fill=tk.X, padx=(25, 0))

        # --- Event Binding ---
        self.entry.bind("<Return>", self.process_command)
        self.entry.bind("<Tab>", self.handle_tab_completion)
        # --- NEW: History Navigation Binding ---
        self.entry.bind("<Up>", self.scroll_history_up)
        self.entry.bind("<Down>", self.scroll_history_down)

        self.write_to_output("Welcome! Use Tab for completions and Up/Down arrows for history.\n")

    def setup_completions(self):
        """Loads all commands and options from config into a list for completion."""
        command_names = [cmd['name'] for cmd in self.config.get('commands', [])]
        option_names = set()
        for cmd in self.config.get('commands', []):
            for arg in cmd.get('arguments', []):
                option_names.update(arg['names'])
        self.completer_words = sorted(command_names + list(option_names))

    def update_hint(self, *args):
        """Updates the hint label as the user types."""
        current_text = self.input_var.get()
        if not current_text or current_text[-1] == " ":
            self.hint_label.config(text="")
            return
        last_word = current_text.split()[-1]
        suggestion = next((word for word in self.completer_words if word.startswith(last_word)), "")
        if suggestion and suggestion != last_word:
            self.hint_label.config(text=suggestion[len(last_word):])
        else:
            self.hint_label.config(text="")

    def handle_tab_completion(self, event=None):
        """Handles Tab key presses for autocompletion."""
        current_text = self.input_var.get()
        if not current_text: return "break"
        last_word = current_text.split()[-1]
        matches = [word for word in self.completer_words if word.startswith(last_word)]
        if len(matches) == 1:
            completion = matches[0]
            new_text = current_text[:current_text.rfind(last_word)] + completion + " "
            self.input_var.set(new_text)
            self.entry.icursor(tk.END)
        elif len(matches) > 1:
            self.write_to_output(f"\n> {current_text}\n{'  '.join(matches)}\n")
        return "break"

    # --- NEW: Method to scroll up in history ---
    def scroll_history_up(self, event=None):
        """Navigates to the previous command in the history."""
        if not self.command_history:
            return "break"
        
        # If we're at the bottom (new command line), save what's currently typed
        if self.history_index == len(self.command_history):
            self.current_command_buffer = self.input_var.get()

        if self.history_index > 0:
            self.history_index -= 1
            self.input_var.set(self.command_history[self.history_index])
            self.entry.icursor(tk.END)
        
        return "break"

    # --- NEW: Method to scroll down in history ---
    def scroll_history_down(self, event=None):
        """Navigates to the next command in the history."""
        if not self.command_history:
            return "break"
        
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.input_var.set(self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            # We are at the last history item, moving down should go to the new command line
            self.history_index += 1
            self.input_var.set(self.current_command_buffer) # Restore what was typed
        
        self.entry.icursor(tk.END)
        return "break"

    def write_to_output(self, msg):
        """Appends a message to the output text widget."""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, msg)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)

    def process_command(self, event=None):
        """Processes the command entered by the user."""
        command_str = self.entry.get().strip()
        if not command_str:
            return
        
        self.hint_label.config(text="")
        self.write_to_output(f"> {command_str}\n")
        self.entry.delete(0, tk.END)

        # --- MODIFIED: Add to history and reset index ---
        if command_str and (not self.command_history or self.command_history[-1] != command_str):
            self.command_history.append(command_str)
        self.history_index = len(self.command_history)
        self.current_command_buffer = ""
        # -----------------------------------------------

        try:
            input_args = shlex.split(command_str)
            stdout_capture, stderr_capture, result = io.StringIO(), io.StringIO(), None
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                try:
                    args = self.parser.parse_args(input_args)
                    result = run_command(self.parser, self.config, args)
                except (argparse.ArgumentError, SystemExit): pass
            
            err_output, std_output = stderr_capture.getvalue(), stdout_capture.getvalue()
            if err_output: self.write_to_output(err_output)
            if std_output: self.write_to_output(std_output)
            if result is not None: self.write_to_output(f"{result}\n")
        except Exception as e:
            self.write_to_output(f"An unexpected error occurred: {e}\n")
        
        self.write_to_output("\n")

def main():
    """The main entry point to launch the GUI application."""
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()