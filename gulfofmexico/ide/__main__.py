"""
Gulf of Mexico IDE Launcher

Launches the IDE with automatic fallback between Qt GUI and Web-based interface.

Execution Strategy:
    1. If --web flag: Launch web IDE directly
    2. Otherwise: Try Qt GUI first
    3. On ANY Qt error (import, SSE4.x CPU requirement, etc.): Fall back to web IDE

Qt GUI Requirements:
    - PySide6 or PyQt5 installed
    - CPU with SSSE3, SSE4.1, SSE4.2, POPCNT support
    - Note: QEMU Virtual CPU lacks these instructions, so web IDE is used instead

Web IDE:
    - No special requirements (built-in http.server)
    - Runs on http://localhost:8080/ide
    - Full-featured: save, load, execute, examples
    - Compatible with any system

Command-Line Options:
    -o, --open FILE: Open file(s) on startup (multiple allowed)
    --run: Execute code immediately after opening files
    --web: Force web IDE instead of trying Qt GUI
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
        "--web",
        action="store_true",
        help="Force web-based IDE instead of Qt GUI.",
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

    # Use web IDE if forced
    if args.web:
        print("Launching Web-based IDE...")
        from .web_ide import run_web_ide

        run_web_ide()
    else:
        # Try Qt GUI first, fall back to web IDE on ANY error
        try:
            from .app import run

            run(args.open or None, run_on_open=args.run)
        except Exception as exc:
            # Fallback to web IDE for any Qt failure
            print(f"Qt GUI unavailable: {type(exc).__name__}")
            print("Launching Web-based IDE...")
            from .web_ide import run_web_ide

            run_web_ide()
