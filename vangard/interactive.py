# interactive.py
import shlex
import argparse
import atexit
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from core.framework import load_config, build_parser, run_command, apply_startup_flags
from vangard.interactive_completer import create_smart_completer
from vangard.scene_cache import get_scene_cache_manager


def handle_special_command(command: str, scene_cache, cache_enabled: bool):
    """
    Handle special interactive shell commands (starting with .).

    Args:
        command: Command string
        scene_cache: Scene cache manager instance
        cache_enabled: Whether scene cache is enabled
    """
    cmd = command.lower()

    if cmd in ['.refresh', '.r']:
        if not cache_enabled:
            print("❌ Scene cache is not enabled. Set DAZ_SCRIPT_SERVER_ENABLED=true")
            return

        print("🔄 Refreshing scene cache...")
        success = scene_cache.refresh_cache(force=True)

        if success:
            stats = scene_cache.get_cache_stats()
            print(f"✅ Cache refreshed successfully!")
            print(f"   Total nodes: {stats['total_nodes']}")
            print(f"   Cameras: {stats['cameras']}, Lights: {stats['lights']}, Characters: {stats['characters']}")
        else:
            print("❌ Failed to refresh cache. Is DAZ Studio running with Script Server?")

    elif cmd in ['.stats', '.s']:
        if not cache_enabled:
            print("❌ Scene cache is not enabled. Set DAZ_SCRIPT_SERVER_ENABLED=true")
            return

        stats = scene_cache.get_cache_stats()
        print("\n📊 Scene Cache Statistics:")
        print("=" * 50)
        print(f"Last Update:      {stats['last_update'] or 'Never'}")
        print(f"Cache Status:     {'🟢 Fresh' if not stats['is_stale'] else '🟡 Stale'}")
        print(f"Polling:          {'🟢 Active' if stats['polling_enabled'] else '🔴 Inactive'}")
        print(f"Server:           {'🟢 Enabled' if stats['server_enabled'] else '🔴 Disabled'}")
        print("-" * 50)
        print(f"Total Nodes:      {stats['total_nodes']}")
        print(f"  📷 Cameras:     {stats['cameras']}")
        print(f"  💡 Lights:      {stats['lights']}")
        print(f"  🧍 Characters:  {stats['characters']}")
        print(f"  📦 Props:       {stats['props']}")
        print(f"  🗂️  Groups:      {stats['groups']}")
        print("=" * 50)

    elif cmd in ['.help', '.h', '.?']:
        print("\n💡 Special Commands:")
        print("=" * 50)
        if cache_enabled:
            print("  .refresh (.r)   - Refresh scene cache immediately")
            print("  .stats (.s)     - Show scene cache statistics")
        print("  .help (.h, .?)  - Show this help")
        print("  exit, quit      - Exit interactive shell")
        print("=" * 50)

    else:
        print(f"❌ Unknown special command: {command}")
        print("   Type '.help' for available special commands")


def main():
    """The main entry point for the interactive shell."""
    apply_startup_flags(sys.argv[1:])

    print("=" * 60)
    print("🚀 Vangard Interactive Shell")
    print("=" * 60)
    print()

    config = load_config()
    parser = build_parser(config)

    # Initialize scene cache manager for autocomplete
    scene_cache = get_scene_cache_manager()
    scene_cache_enabled = scene_cache.server_enabled

    if scene_cache_enabled:
        print("🔍 Starting scene cache for smart autocomplete...")
        scene_cache.start_polling()
        print("   Cache polling started - scene nodes will be suggested as you type")
        atexit.register(lambda: scene_cache.stop_polling())
    else:
        print("💡 Tip: Enable DAZ_SCRIPT_SERVER for scene node autocomplete")

    print()
    print("Commands:")
    print("  - Type any vangard command (press TAB for suggestions)")
    print("  - 'exit' or 'quit' - Exit the shell")
    if scene_cache_enabled:
        print("  - '.refresh' - Refresh scene cache immediately")
        print("  - '.stats' - Show scene cache statistics")
    print("=" * 60)
    print()

    # Create smart completer with scene cache integration
    completer = create_smart_completer(config)

    # Create styled prompt
    prompt_style = Style.from_dict({
        'prompt': '#6366f1 bold',  # Indigo prompt
        'cache-indicator': '#10b981',  # Green for cache active
    })

    prog_name = config.get('app', {}).get('prog', 'cli')
    cache_indicator = ' 🔍' if scene_cache_enabled else ''

    session = PromptSession(
        history=FileHistory('.cli_history'),
        completer=completer,
        complete_while_typing=False,  # Only complete on TAB
        style=prompt_style
    )

    while True:
        try:
            prompt_text = HTML(f'<prompt>{prog_name}{cache_indicator}></prompt> ')
            user_input = session.prompt(prompt_text, completer=completer)
            
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue

            # Handle special interactive commands
            if user_input.strip().startswith('.'):
                handle_special_command(user_input.strip(), scene_cache, scene_cache_enabled)
                continue

            input_args = shlex.split(user_input)
            
            try:
                args = parser.parse_args(input_args)
                result = run_command(parser, config, args)
                if result is not None:
                    print(result)
            except (argparse.ArgumentError, SystemExit):
                # Argparse prints its own help/error messages, so we just continue.
                pass

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

    # Cleanup
    if scene_cache_enabled:
        print("\n🛑 Stopping scene cache polling...")
        scene_cache.stop_polling()

    print("\n👋 Goodbye!")
    print("=" * 60)

if __name__ == "__main__":
    main()