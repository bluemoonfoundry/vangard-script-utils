"""
Interactive Mode Smart Completer
Provides context-aware autocomplete for the interactive shell,
including scene node suggestions from the cache.
"""
import shlex
from typing import Dict, List, Iterable, Optional
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

from vangard.scene_cache import get_scene_cache_manager


class SmartCompleter(Completer):
    """
    Context-aware completer for interactive mode.

    Provides completions based on:
    - Command names
    - Argument flags (--option, -o)
    - Scene nodes (when applicable)
    - File paths (future enhancement)
    """

    def __init__(self, config: Dict):
        """
        Initialize the smart completer.

        Args:
            config: Loaded config.yaml dictionary
        """
        self.config = config
        self.scene_cache = get_scene_cache_manager()

        # Pre-compute command lookup
        self.commands = {}
        for cmd in config.get('commands', []):
            self.commands[cmd['name']] = cmd

        # Command names for root-level completion
        self.command_names = list(self.commands.keys())

        # All option flags across all commands
        self.all_option_flags = set()
        for cmd in config.get('commands', []):
            for arg in cmd.get('arguments', []):
                self.all_option_flags.update(arg.get('names', []))

    def get_completions(self, document: Document, complete_event) -> Iterable[Completion]:
        """
        Generate completions based on current document state.

        Args:
            document: Current document (command line)
            complete_event: Completion event

        Yields:
            Completion objects
        """
        text = document.text_before_cursor

        # Parse the current line to understand context
        try:
            tokens = shlex.split(text) if text.strip() else []
        except ValueError:
            # Incomplete quotes, etc - still try to parse
            tokens = text.split()

        # Determine what we're completing
        if len(tokens) == 0 or (len(tokens) == 1 and not text.endswith(' ')):
            # Completing command name
            yield from self._complete_command(document.get_word_before_cursor())

        elif len(tokens) >= 1:
            # We have a command, complete arguments
            command_name = tokens[0]

            if command_name in self.commands:
                yield from self._complete_argument(
                    command_name,
                    tokens[1:],
                    document.get_word_before_cursor(),
                    text
                )
            else:
                # Unknown command, offer command names
                yield from self._complete_command(document.get_word_before_cursor())

    def _complete_command(self, word_before_cursor: str) -> Iterable[Completion]:
        """
        Complete command names.

        Args:
            word_before_cursor: Partial command name

        Yields:
            Completion objects for matching commands
        """
        word_lower = word_before_cursor.lower()

        for cmd_name in self.command_names:
            if cmd_name.lower().startswith(word_lower):
                yield Completion(
                    cmd_name,
                    start_position=-len(word_before_cursor),
                    display=cmd_name,
                    display_meta=self.commands[cmd_name].get('help', '')[:50]
                )

    def _complete_argument(
        self,
        command_name: str,
        arg_tokens: List[str],
        word_before_cursor: str,
        full_text: str
    ) -> Iterable[Completion]:
        """
        Complete command arguments based on context.

        Args:
            command_name: Name of the command
            arg_tokens: Arguments typed so far (excluding command)
            word_before_cursor: Current partial word
            full_text: Full text before cursor

        Yields:
            Completion objects
        """
        cmd_config = self.commands[command_name]

        # Check if completing a flag or a value
        if word_before_cursor.startswith('-'):
            # Completing a flag
            yield from self._complete_flag(cmd_config, word_before_cursor)
        else:
            # Completing a value (positional or flag value)
            yield from self._complete_value(cmd_config, arg_tokens, word_before_cursor, full_text)

    def _complete_flag(self, cmd_config: Dict, word_before_cursor: str) -> Iterable[Completion]:
        """
        Complete flag names (--option or -o).

        Args:
            cmd_config: Command configuration
            word_before_cursor: Partial flag

        Yields:
            Completion objects for matching flags
        """
        word_lower = word_before_cursor.lower()

        for arg in cmd_config.get('arguments', []):
            for flag_name in arg.get('names', []):
                if flag_name.lower().startswith(word_lower):
                    yield Completion(
                        flag_name,
                        start_position=-len(word_before_cursor),
                        display=flag_name,
                        display_meta=arg.get('help', '')[:50]
                    )

    def _complete_value(
        self,
        cmd_config: Dict,
        arg_tokens: List[str],
        word_before_cursor: str,
        full_text: str
    ) -> Iterable[Completion]:
        """
        Complete argument values based on context.

        Args:
            cmd_config: Command configuration
            arg_tokens: Arguments typed so far
            word_before_cursor: Current partial word
            full_text: Full text before cursor

        Yields:
            Completion objects
        """
        # Determine which argument we're completing
        arg_def = self._identify_current_argument(cmd_config, arg_tokens, full_text)

        if not arg_def:
            # Can't determine argument, offer flags
            yield from self._complete_flag(cmd_config, word_before_cursor)
            return

        # Check for autocomplete metadata
        autocomplete = arg_def.get('autocomplete', {})

        if autocomplete.get('source') == 'scene-nodes':
            # Complete with scene node labels
            yield from self._complete_scene_nodes(
                autocomplete,
                word_before_cursor
            )

        # Also offer flags as alternative completions
        if word_before_cursor.startswith('-'):
            yield from self._complete_flag(cmd_config, word_before_cursor)

    def _identify_current_argument(
        self,
        cmd_config: Dict,
        arg_tokens: List[str],
        full_text: str
    ) -> Optional[Dict]:
        """
        Identify which argument definition we're currently completing.

        Args:
            cmd_config: Command configuration
            arg_tokens: Argument tokens (excluding command name)
            full_text: Full text before cursor

        Returns:
            Argument definition dict, or None if can't determine
        """
        # Look for flag-value pairs
        # Check if previous token was a flag
        if len(arg_tokens) >= 1:
            prev_token = arg_tokens[-1]

            # If previous token is a flag, we're completing its value
            if prev_token.startswith('-'):
                for arg_def in cmd_config.get('arguments', []):
                    if prev_token in arg_def.get('names', []):
                        return arg_def

        # Count positional arguments
        # (Simplified - assumes positional args come first)
        positional_count = 0
        i = 0
        while i < len(arg_tokens):
            token = arg_tokens[i]
            if token.startswith('-'):
                # This is a flag, skip it and its value
                # Check if it's a boolean flag or has a value
                flag_def = None
                for arg_def in cmd_config.get('arguments', []):
                    if token in arg_def.get('names', []):
                        flag_def = arg_def
                        break

                if flag_def and flag_def.get('action') != 'store_true':
                    # Has a value, skip next token
                    i += 2
                else:
                    # Boolean flag, no value
                    i += 1
            else:
                # Positional argument
                positional_count += 1
                i += 1

        # Find the Nth positional argument definition
        positional_args = [
            arg for arg in cmd_config.get('arguments', [])
            if not any(name.startswith('-') for name in arg.get('names', []))
        ]

        if positional_count < len(positional_args):
            return positional_args[positional_count]

        return None

    def _complete_scene_nodes(
        self,
        autocomplete: Dict,
        word_before_cursor: str
    ) -> Iterable[Completion]:
        """
        Complete with scene node labels from cache.

        Args:
            autocomplete: Autocomplete configuration
            word_before_cursor: Partial node name

        Yields:
            Completion objects for matching nodes
        """
        node_types = autocomplete.get('types', [])
        word_lower = word_before_cursor.lower()

        # Get nodes from cache
        try:
            if node_types:
                # Fetch filtered by types
                all_nodes = []
                for node_type in node_types:
                    nodes = self.scene_cache.get_nodes(node_type=node_type)
                    all_nodes.extend(nodes)
            else:
                # All nodes
                all_nodes = self.scene_cache.get_nodes()

            # Remove duplicates and sort
            seen = set()
            unique_nodes = []
            for node in all_nodes:
                label = node.get('label', '')
                if label and label not in seen:
                    seen.add(label)
                    unique_nodes.append(node)

            # Filter by partial match and yield completions
            for node in unique_nodes:
                label = node.get('label', '')
                if label.lower().startswith(word_lower):
                    node_type = node.get('type', 'node')
                    type_emoji = self._get_type_emoji(node_type)

                    yield Completion(
                        label,
                        start_position=-len(word_before_cursor),
                        display=f"{type_emoji} {label}",
                        display_meta=f"{node_type} | {node.get('path', '')[:40]}"
                    )

        except Exception as e:
            # Cache not available or error - silently continue
            pass

    def _get_type_emoji(self, node_type: str) -> str:
        """Get emoji icon for node type."""
        emoji_map = {
            'camera': '📷',
            'light': '💡',
            'figure': '🧍',
            'prop': '📦',
            'group': '🗂️',
            'bone': '🦴',
            'node': '📌'
        }
        return emoji_map.get(node_type, '📌')


def create_smart_completer(config: Dict) -> SmartCompleter:
    """
    Factory function to create a smart completer.

    Args:
        config: Loaded config.yaml dictionary

    Returns:
        SmartCompleter instance
    """
    return SmartCompleter(config)
