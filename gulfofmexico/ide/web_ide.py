#!/usr/bin/env python3
"""Web-based Gulf of Mexico IDE - works without Qt dependencies."""

import http.server
import socketserver
import json
import sys
import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import threading
import webbrowser

from gulfofmexico.processor.lexer import tokenize
from gulfofmexico.processor.syntax_tree import generate_syntax_tree
from gulfofmexico.interpreter import interpret_code_statements_main_wrapper
from gulfofmexico.builtin import KEYWORDS

# Local debug flag for the web IDE. When set, verbose internal messages
# are written to stderr. Otherwise these internal messages are suppressed
# to avoid noisy logs during normal usage.
WEB_IDE_DEBUG = bool(os.environ.get("GULFOFMEXICO_DEBUG"))


def _webide_debug(msg: str) -> None:
    if WEB_IDE_DEBUG:
        sys.stderr.write(msg)
        sys.stderr.flush()


class GOMWebIDEHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for the web-based IDE."""

    # Class variable to store the workspace directory
    workspace_dir = Path.cwd()

    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/" or self.path == "/ide":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path == "/list_files":
            self.handle_list_files()
        elif self.path.startswith("/load?"):
            self.handle_load_file()
        elif self.path.startswith("/image/"):
            # Serve generated images
            self.handle_serve_image()
        else:
            super().do_GET()

    def handle_serve_image(self):
        """Serve a generated image file."""
        try:
            # Extract filename from path
            filename = self.path.split("/image/", 1)[1]
            # Remove query string if present
            filename = filename.split("?")[0]
            filepath = self.workspace_dir / filename

            _webide_debug(f"[IMAGE] Serving image: {filename} from {filepath}\n")

            # Security: ensure file is within workspace
            filepath = filepath.resolve()
            if not str(filepath).startswith(str(self.workspace_dir.resolve())):
                raise ValueError("Access denied")

            if not filepath.exists() or not filepath.suffix.lower() in [
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
            ]:
                raise ValueError("Image not found")

            # Determine content type
            content_type = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
            }.get(filepath.suffix.lower(), "application/octet-stream")

            # Read and serve image
            with open(filepath, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

    def do_POST(self):
        """Handle POST requests for code execution and file operations."""
        import sys

        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())

        if self.path == "/execute":
            code = data.get("code", "")
            _webide_debug(f"[HTTP] Execute request for code: {repr(code[:50])}\n")
            result = self.execute_code(code)
            _webide_debug(f"[HTTP] Sending response: {result}\n")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        elif self.path == "/save":
            result = self.handle_save_file(data)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

    def handle_list_files(self):
        """List all .gom files in the workspace."""
        try:
            gom_files = sorted(
                [
                    str(f.relative_to(self.workspace_dir))
                    for f in self.workspace_dir.rglob("*.gom")
                    if not any(part.startswith(".") for part in f.parts)
                ]
            )

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "files": gom_files}).encode())
        except Exception as e:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_load_file(self):
        """Load a file from disk."""
        try:
            query = urlparse(self.path).query
            params = parse_qs(query)
            filename = params.get("file", [""])[0]

            if not filename:
                raise ValueError("No filename provided")

            filepath = self.workspace_dir / filename

            # Security: ensure file is within workspace
            filepath = filepath.resolve()
            if not str(filepath).startswith(str(self.workspace_dir.resolve())):
                raise ValueError("Access denied: file outside workspace")

            if not filepath.exists():
                raise ValueError(f"File not found: {filename}")

            content = filepath.read_text(encoding="utf-8")

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps(
                    {"success": True, "filename": filename, "content": content}
                ).encode()
            )
        except Exception as e:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_save_file(self, data):
        """Save code to a file."""
        try:
            filename = data.get("filename", "")
            content = data.get("content", "")

            if not filename:
                raise ValueError("No filename provided")

            # Ensure .gom extension
            if not filename.endswith(".gom"):
                filename += ".gom"

            filepath = self.workspace_dir / filename

            # Security: ensure file is within workspace
            filepath = filepath.resolve()
            if not str(filepath).startswith(str(self.workspace_dir.resolve())):
                raise ValueError("Access denied: cannot save outside workspace")

            # Create parent directories if needed
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Save file
            filepath.write_text(content, encoding="utf-8")

            return {
                "success": True,
                "message": f"Saved to {filename}",
                "filename": filename,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_code(self, code):
        """Execute Gulf of Mexico code and capture output."""
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr

    _webide_debug(f"[WEB IDE] Received code: {repr(code[:50])}\n")

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        # Track existing PNG files before execution with their modification times
        import time

        execution_start = time.time()
        existing_pngs = set(self.workspace_dir.glob("*.png"))

        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Set up interpreter
                import gulfofmexico.interpreter as interpreter

                interpreter.filename = "web_ide"
                interpreter.code = code

                # Tokenize and parse
                _webide_debug("[WEB IDE] Tokenizing...\n")
                tokens = tokenize("web_ide", code)
                _webide_debug(f"[WEB IDE] Got {len(tokens)} tokens\n")

                statements = generate_syntax_tree("web_ide", tokens, code)
                _webide_debug(f"[WEB IDE] Got {len(statements)} statements\n")

                # Execute
                namespaces = [KEYWORDS.copy()]
                _webide_debug("[WEB IDE] Executing...\n")
                result = interpret_code_statements_main_wrapper(
                    statements, namespaces, [], [{}], {}, []
                )
                _webide_debug("[WEB IDE] Execution complete\n")

                # Force flush
                sys.stdout.flush()

            output_val = stdout_capture.getvalue()
            error_val = stderr_capture.getvalue()

            # Detect newly created or modified PNG files
            all_pngs = set(self.workspace_dir.glob("*.png"))
            new_pngs = all_pngs - existing_pngs
            # Also check for modified existing files
            modified_pngs = {
                p
                for p in existing_pngs
                if p.exists() and p.stat().st_mtime > execution_start
            }
            changed_pngs = new_pngs | modified_pngs
            images = sorted([str(p.name) for p in changed_pngs]) if changed_pngs else []

            response = {
                "success": True,
                "output": output_val,
                "error": error_val,
                "result": str(result) if result else "",
                "images": images,  # List of newly created image files
            }

            # Log to real stderr (not captured)
            _webide_debug(
                f"[WEB IDE] Output length: {len(output_val)}, content: {repr(output_val[:100])}\n"
            )
            if images:
                _webide_debug(f"[WEB IDE] Created images: {images}\n")

            return response
        except Exception as e:
            import traceback

            error_val = stderr_capture.getvalue()
            tb = traceback.format_exc()

            response = {
                "success": False,
                "output": stdout_capture.getvalue(),
                "error": f"{error_val}\n{type(e).__name__}: {str(e)}\n{tb}",
                "result": "",
                "images": [],
            }

            sys.stderr.write(f"[WEB IDE] Error: {e}\n{tb}\n")
            sys.stderr.flush()

            return response

    def get_html(self):
        """Generate the HTML for the IDE."""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gulf of Mexico Web IDE</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Consolas', 'Liberation Mono', 'Menlo', 'Courier', monospace;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        .header {
            background: #2d2d30;
            padding: 10px 20px;
            border-bottom: 1px solid #3e3e42;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 18px;
            color: #cccccc;
        }
        .buttons {
            display: flex;
            gap: 10px;
        }
        button {
            background: #0e639c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background: #1177bb;
        }
        button:active {
            background: #0d5a8f;
        }
        .clear-btn {
            background: #c72e2e;
        }
        .clear-btn:hover {
            background: #e04343;
        }
        .save-btn {
            background: #0e8c39;
        }
        .save-btn:hover {
            background: #14a94b;
        }
        .load-btn {
            background: #6c5ce7;
        }
        .load-btn:hover {
            background: #7d6ef7;
        }
        .container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        .editor-pane {
            flex: 1;
            display: flex;
            flex-direction: column;
            border-right: 1px solid #3e3e42;
        }
        .right-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .tabs {
            display: flex;
            background: #252526;
            border-bottom: 1px solid #3e3e42;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            color: #858585;
            font-size: 13px;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        .tab:hover {
            color: #cccccc;
            background: #2d2d30;
        }
        .tab.active {
            color: #ffffff;
            border-bottom-color: #0e639c;
            background: #1e1e1e;
        }
        .tab-content {
            display: none;
            flex: 1;
            overflow: auto;
        }
        .tab-content.active {
            display: flex;
            flex-direction: column;
        }
        .output-pane {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .graphics-pane {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #1e1e1e;
            overflow: hidden;
        }
        .pane-header {
            background: #252526;
            padding: 8px 16px;
            border-bottom: 1px solid #3e3e42;
            font-size: 12px;
            color: #cccccc;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        #editor {
            flex: 1;
            padding: 16px;
            background: #1e1e1e;
            color: #d4d4d4;
            font-size: 14px;
            line-height: 1.6;
            resize: none;
            border: none;
            outline: none;
            font-family: 'Consolas', 'Liberation Mono', 'Menlo', 'Courier', monospace;
            tab-size: 3;
        }
        #output {
            flex: 1;
            padding: 16px;
            background: #1e1e1e;
            color: #d4d4d4;
            font-size: 14px;
            line-height: 1.6;
            overflow-y: auto;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Consolas', 'Liberation Mono', 'Menlo', 'Courier', monospace;
        }
        #graphics {
            flex: 1;
            padding: 16px;
            background: #1e1e1e;
            overflow: auto;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        #graphics img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border: 1px solid #3e3e42;
        }
        .no-graphics {
            color: #858585;
            font-style: italic;
        }
        .output-success {
            color: #4ec9b0;
        }
        .output-error {
            color: #f48771;
        }
        .status-bar {
            background: #007acc;
            color: white;
            padding: 4px 16px;
            font-size: 12px;
        }
        .examples {
            padding: 10px;
            background: #252526;
        }
        .examples select {
            background: #3c3c3c;
            color: #cccccc;
            border: 1px solid #3e3e42;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.6);
        }
        .modal-content {
            background-color: #2d2d30;
            margin: 10% auto;
            padding: 20px;
            border: 1px solid #3e3e42;
            border-radius: 8px;
            width: 80%;
            max-width: 500px;
            color: #d4d4d4;
        }
        .modal-content h2 {
            margin-bottom: 20px;
            color: #cccccc;
        }
        .modal-content input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            background: #3c3c3c;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            color: #d4d4d4;
            font-size: 14px;
            font-family: 'Consolas', 'Liberation Mono', 'Menlo', 'Courier', monospace;
        }
        .modal-content select {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            background: #3c3c3c;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            color: #d4d4d4;
            font-size: 14px;
            max-height: 200px;
        }
        .modal-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            justify-content: flex-end;
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: #fff;
        }
        .file-list {
            max-height: 300px;
            overflow-y: auto;
            margin: 10px 0;
        }
        .file-item {
            padding: 8px;
            margin: 4px 0;
            background: #3c3c3c;
            border: 1px solid #3e3e42;
            border-radius: 4px;
            cursor: pointer;
        }
        .file-item:hover {
            background: #4c4c4c;
        }
        .file-item.selected {
            background: #0e639c;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Gulf of Mexico Web IDE</h1>
        <div class="buttons">
            <button class="save-btn" onclick="showSaveModal()">Save</button>
            <button class="load-btn" onclick="showLoadModal()">Load</button>
            <button onclick="runCode()">Run (Ctrl+Enter)</button>
            <button class="clear-btn" onclick="clearOutput()">Clear Output</button>
        </div>
    </div>

    <div class="examples">
        <label>Examples: </label>
        <select onchange="loadExample(this.value)">
            <option value="">-- Select Example --</option>
            <option value="grand_deluxe">🌊 Grand Deluxe Demo (All Features)</option>
            <option value="hello">Hello World</option>
            <option value="variables">Variables</option>
            <option value="arrays">Arrays (-1 indexing)</option>
            <option value="functions">Functions</option>
            <option value="graphics">Graphics & Canvas</option>
            <option value="temporal">Temporal Keywords</option>
        </select>
    </div>

    <div class="container">
        <div class="editor-pane">
            <div class="pane-header">Editor</div>
            <textarea id="editor" placeholder="// Write your Gulf of Mexico code here...
// End statements with !
// Use ? for debug mode

print(&quot;Hello Gulf of Mexico&quot;)!"></textarea>
        </div>
        <div class="right-panel">
            <div class="tabs">
                <div class="tab active" onclick="switchTab('output')">Output</div>
                <div class="tab" onclick="switchTab('graphics')">Graphics</div>
            </div>
            <div id="outputTab" class="tab-content active">
                <div class="output-pane">
                    <div id="output"></div>
                </div>
            </div>
            <div id="graphicsTab" class="tab-content">
                <div class="graphics-pane">
                    <div id="graphics"><div class="no-graphics">No graphics generated yet</div></div>
                </div>
            </div>
        </div>
    </div>

    <div class="status-bar">Ready • Gulf of Mexico Interpreter v0.1.1</div>

    <!-- Save Modal -->
    <div id="saveModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeSaveModal()">&times;</span>
            <h2>Save File</h2>
            <input type="text" id="saveFilename" placeholder="filename.gom" />
            <div class="modal-buttons">
                <button onclick="closeSaveModal()">Cancel</button>
                <button class="save-btn" onclick="saveFile()">Save</button>
            </div>
        </div>
    </div>

    <!-- Load Modal -->
    <div id="loadModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeLoadModal()">&times;</span>
            <h2>Load File</h2>
            <div class="file-list" id="fileList">
                <div style="color: #858585;">Loading files...</div>
            </div>
            <div class="modal-buttons">
                <button onclick="closeLoadModal()">Cancel</button>
                <button class="load-btn" onclick="loadSelectedFile()">Load</button>
            </div>
        </div>
    </div>

    <script>
        let selectedFile = null;
        let currentFilename = null;
        const examples = {
            grand_deluxe: `// Grand Deluxe Demo — Gulf of Mexico (run this in the Web IDE)
// Showcases: variables, arrays, maps, functions, async/await, reactivity,
// math/stats/finance/science built‑ins, regex, negative indexing, string ops,
// satirical keywords, and more. Have fun!

print("🌊 Welcome to the Gulf of Mexico — Grand Deluxe Demo!")!

// 1) Variables, constants, strings and interpolation
const name = "Traveler"!
print("Hello, " + name + "!")!

// Probabilistic variables (higher ! wins)
var mood = "meh"!
var mood = "great"!!
var mood = "ecstatic"!!!
print("Mood selected by confidence:")!
print(mood)!

// Three‑valued logic
const unknown = maybe!
print("Three‑valued Boolean (maybe):")!
print(unknown)!

// 2) Arrays: start at -1 and support negative indexing
const nums = [10, 20, 30, 40, 50]!
print("Array:")!
print(nums)!
print("First element nums[-1]:")!
print(nums[-1])!
print("Fifth element via traditional index 3:")!
print(nums[3])!

// Fractional indexing inserts between elements
const between = [1, 3]!
between[0.5] = 2!
print("Fractional indexing [1,3] => insert 2 at 0.5:")!
print(between)!

// 3) Number and string indexing / methods
const n = 12345!
print("Digit at n[-1] (first digit):")!
print(n[-1])!

var s = "GOM"!
print("String before push/pop:")!
print(s)!
s.push("! ")!
s.push("Rocks")!
print("String after pushes:")!
print(s)!
print("Popped char:")!
print(s.pop(-1))!
print("String now:")!
print(s)!

// 4) Maps (dictionaries)
const person = Map()!
person["name"] = "Ada"!
person["age"] = 36!
person["skills"] = ["math", "logic", "computing"]!
print("Map person:")!
print(person)!
print("Name from map:")!
print(person["name"])!

// 5) Functions and calls
function shout(msg) => {
   print("SHOUT:")!
   print(String(msg))!
}!

function add(a, b) => a + b!

const sum = add 7, 35!
print("add(7, 35) =")!
print(sum)!
shout("hello functions")!

// 6) Reactive programming
var count = 0!
when count > 2 {
   print("when triggered! count =", count)!
}!
count = 1!
count = 3!   // triggers

// 7) Async / Await
async function greet_async() => {
   sleep(0.1)!
   return "Async greeting complete!"!
}!
print("Starting async demo...")!
const async_result = await greet_async()!
print(async_result)!

// 8) Math / Stats / Finance / Business / Scientific built‑ins
print("=== Built‑ins Showcase ===")!
const data = [10, 20, 30, 40, 50]!
const data_mean = mean data!
const data_stdev = stdev data!
print("mean:")!
print(data_mean)!
print("stdev:")!
print(data_stdev)!

const payment = pmt 0.05, 12, 1000!
print("pmt(0.05, 12, 1000) =>")!
print(payment)!

const return_on_investment = roi 1500, 1000!
print("roi(1500, 1000) => %")!
print(return_on_investment)!

const xs = [0, 1, 2, 3, 4]!
const ys = [1, 3, 5, 7, 9]!
const model = linear_regression xs, ys!
print("linear_regression([0..4],[1,3,5,7,9]) [slope, intercept]:")!
print(model)!

const roots = quadratic_solve 1, -7, 12!
print("quadratic_solve(1, -7, 12) roots:")!
print(roots)!

// 9) Regex utilities
const match_result = regex_match "world$,hello world"!
const findall_result = regex_findall "o,hello world"!
print("Regex match /world$/ on 'hello world':")!
print(match_result)!
print("Regex findall 'o' in 'hello world':")!
print(findall_result)!

// 10) Satirical keywords — code with vibes
happy {
   print("Everything is amazing and nothing hurts!")!
}!

blockchain {
   print("Recording this demo on the immutable ledger.")!
}!

ai_powered {
   print("Predicting 99% chance you'll enjoy this demo.")!
}!

sprint {
   print("Daily stand‑up done in 1 line. Velocity +∞.")!
}!

synergize {
   print("Leveraging cross‑functional paradigms for maximal throughput.")!
}!

// 11) Tiny object pattern via Map
function make_point(x, y) => {
   const p = Map()!
   p["x"] = x!
   p["y"] = y!
   return p!
}!

const p0 = make_point 3, 4!
print("Point map object:")!
print(p0)!

print("\\n🎉 Demo complete — explore and tweak freely in the Web IDE!")!`,

            hello: `// Hello World
print("Hello, Gulf of Mexico!")!
print("Statements end with !")!`,

            variables: `// Variable declarations
const const name = "Gulf"!
const var count = 0!
var const limit = 10!
var var value = 5!

print("Name:", name)!
print("Count:", count)!
count = count + 1!
print("Count now:", count)!`,

            arrays: `// Arrays start at -1!
const const scores = [3, 2, 5]!
print("First element (index -1):", scores[-1])!
print("Second element (index 0):", scores[0])!
print("Third element (index 1):", scores[1])!

// Float indexing
var var numbers = [1, 2, 3]!
numbers[0.5] = 99!
print("After adding at 0.5:", numbers)!`,

            functions: `// Function definitions
function add(a, b) => {
   return a + b!
}!

fn multiply(x, y) => x * y!

const sum = add 3, 5!
const product = multiply 4, 6!

print "3 + 5 =", sum!
print "4 * 6 =", product!`,

            graphics: `// Graphics and Canvas
print "Creating canvas..."!

// Create a 400x300 canvas
const canvas = Canvas(400, 300, "white")!

print "Canvas created"!

// Create colors
const red = Color(255, 0, 0)!
const blue = Color(0, 0, 255)!
const green = Color(0, 255, 0)!
const yellow = Color(255, 255, 0)!

print "Drawing shapes..."!

// Draw a big red circle
canvas.circle 100, 100, 40, red!

// Draw a blue rectangle  
canvas.rect 180, 50, 100, 80, blue!

// Draw a green line
canvas.line 50, 200, 350, 250, green, 5!

// Draw some visible pixels in a pattern
var var x = -1!
while x < 50 {
   canvas.pixel x * 3, 280, yellow!
   x = x + 1!
}!

print "Saving image..."!

// Save to file
canvas.save "web_graphics_demo.png"!

print "Graphics created!"!
print "Check the Graphics pane!"!`,

            temporal: `// Temporal keywords
var const x = 10!
print "Initial:", x!
x = 20!
print "Current:", current x!
print "Previous:", previous x!
x = 30!
print "Current:", current x!
print "Previous:", previous x!`
        };

        function switchTab(tabName) {
            // Update tab buttons
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => {
                tab.classList.remove('active');
                if (tab.textContent.toLowerCase() === tabName.toLowerCase()) {
                    tab.classList.add('active');
                }
            });
            
            // Update tab content
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            document.getElementById(tabName + 'Tab').classList.add('active');
        }

        function loadExample(key) {
            if (key && examples[key]) {
                document.getElementById('editor').value = examples[key];
            }
        }

        function clearOutput() {
            document.getElementById('output').innerHTML = '';
        }

        async function runCode() {
            const code = document.getElementById('editor').value;
            const output = document.getElementById('output');

            output.innerHTML = '<div style="color: #858585;">Running...</div>';

            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code: code })
                });

                const result = await response.json();

                // Debug logging
                console.log('Execution result:', result);
                console.log('Output:', result.output);
                console.log('Error:', result.error);
                console.log('Success:', result.success);
                console.log('Images:', result.images);

                let html = '';
                if (result.output) {
                    html += '<div class="output-success">' + escapeHtml(result.output) + '</div>';
                }
                if (result.error) {
                    html += '<div class="output-error">' + escapeHtml(result.error) + '</div>';
                }
                if (!result.success) {
                    html += '<div class="output-error">[X] Execution failed</div>';
                } else if (!result.output && !result.error) {
                    html += '<div style="color: #858585;">[OK] Executed successfully (no output)</div>';
                }

                output.innerHTML = html;
                
                // Display graphics if any images were created
                const graphics = document.getElementById('graphics');
                console.log('Images in result:', result.images);
                if (result.images && result.images.length > 0) {
                    const imageUrl = '/image/' + result.images[0] + '?t=' + Date.now();
                    console.log('Setting image URL:', imageUrl);
                    graphics.innerHTML = '<img src="' + imageUrl + '" alt="Generated graphics" />';
                    // Auto-switch to Graphics tab when graphics are generated
                    switchTab('graphics');
                } else {
                    console.log('No images found, showing placeholder');
                    graphics.innerHTML = '<div class="no-graphics">No graphics generated</div>';
                }
            } catch (error) {
                output.innerHTML = '<div class="output-error">Error: ' + escapeHtml(error.message) + '</div>';
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // File operations
        function showSaveModal() {
            document.getElementById('saveModal').style.display = 'block';
            document.getElementById('saveFilename').value = currentFilename || 'untitled.gom';
            document.getElementById('saveFilename').select();
        }

        function closeSaveModal() {
            document.getElementById('saveModal').style.display = 'none';
        }

        async function saveFile() {
            const filename = document.getElementById('saveFilename').value;
            const content = document.getElementById('editor').value;

            if (!filename) {
                alert('Please enter a filename');
                return;
            }

            try {
                const response = await fetch('/save', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ filename: filename, content: content })
                });

                const result = await response.json();

                if (result.success) {
                    currentFilename = result.filename;
                    updateStatusBar(`Saved: ${result.filename}`);
                    closeSaveModal();
                } else {
                    alert('Error saving file: ' + result.error);
                }
            } catch (error) {
                alert('Error saving file: ' + error.message);
            }
        }

        async function showLoadModal() {
            document.getElementById('loadModal').style.display = 'block';
            selectedFile = null;

            try {
                const response = await fetch('/list_files');
                const result = await response.json();

                const fileList = document.getElementById('fileList');

                if (result.success && result.files.length > 0) {
                    fileList.innerHTML = result.files.map(file =>
                        `<div class="file-item" onclick="selectFile('${file}')">${file}</div>`
                    ).join('');
                } else {
                    fileList.innerHTML = '<div style="color: #858585;">No .gom files found</div>';
                }
            } catch (error) {
                document.getElementById('fileList').innerHTML =
                    '<div class="output-error">Error loading files: ' + error.message + '</div>';
            }
        }

        function closeLoadModal() {
            document.getElementById('loadModal').style.display = 'none';
        }

        function selectFile(filename) {
            selectedFile = filename;

            // Update UI to show selection
            const items = document.querySelectorAll('.file-item');
            items.forEach(item => {
                if (item.textContent === filename) {
                    item.classList.add('selected');
                } else {
                    item.classList.remove('selected');
                }
            });
        }

        async function loadSelectedFile() {
            if (!selectedFile) {
                alert('Please select a file');
                return;
            }

            try {
                const response = await fetch(`/load?file=${encodeURIComponent(selectedFile)}`);
                const result = await response.json();

                if (result.success) {
                    document.getElementById('editor').value = result.content;
                    currentFilename = result.filename;
                    updateStatusBar(`Loaded: ${result.filename}`);
                    closeLoadModal();
                } else {
                    alert('Error loading file: ' + result.error);
                }
            } catch (error) {
                alert('Error loading file: ' + error.message);
            }
        }

        function updateStatusBar(message) {
            const statusBar = document.querySelector('.status-bar');
            statusBar.textContent = message + ' • Gulf of Mexico Interpreter v0.1.1';
            setTimeout(() => {
                statusBar.textContent = 'Ready • Gulf of Mexico Interpreter v0.1.1';
            }, 3000);
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl+S to save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                showSaveModal();
            }
            // Ctrl+O to open
            if ((e.ctrlKey || e.metaKey) && e.key === 'o') {
                e.preventDefault();
                showLoadModal();
            }
        });

        // Keyboard shortcuts
        document.getElementById('editor').addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                runCode();
            }

            // Tab key inserts 3 spaces
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;
                const value = this.value;
                this.value = value.substring(0, start) + '   ' + value.substring(end);
                this.selectionStart = this.selectionEnd = start + 3;
            }
        });
    </script>
</body>
</html>"""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def run_web_ide(port=8080):
    """Start the web-based IDE server."""
    Handler = GOMWebIDEHandler

    with socketserver.TCPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}/ide"
        print("Gulf of Mexico Web IDE starting...")
        print(f"Server running at: {url}")
        print("Opening browser...")
        print("Press Ctrl+C to stop")

        # Open browser in a separate thread
        def open_browser():
            import time

            time.sleep(1)
            webbrowser.open(url)

        threading.Thread(target=open_browser, daemon=True).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_web_ide(port)
