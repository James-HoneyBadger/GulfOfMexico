"""
Gulf of Mexico IDE Launcher

Launches the Qt GUI IDE.

Command-Line Options:
    -o, --open FILE: Open file(s) on startup (multiple allowed)
    --run: Execute code immediately after opening files
    --debug: Show internal debug messages
    --verbose: Show verbose output
"""

from __future__ import annotations

if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Gulf of Mexico IDE")
    parser.add_argument(
        "-o",
        "--open",
        action="append",
        help="Open a file on startup. Can be given multiple times.",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the active editor after opening files.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show internal debug messages (same as GULFOFMEXICO_DEBUG=1).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output (same as GULFOFMEXICO_VERBOSE=1).",
    )
    args = parser.parse_args()

    # Set environment variables based on flags
    if args.debug:
        os.environ["GULFOFMEXICO_DEBUG"] = "1"
    if args.verbose:
        os.environ["GULFOFMEXICO_VERBOSE"] = "1"

    # Launch Qt GUI IDE
    from .app import run

    run(args.open or None, run_on_open=args.run)
