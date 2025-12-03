# Gulf of Mexico — C++ Compiler (gomcc)

Experimental C++ compiler for Gulf of Mexico: transpiles GOM source to C++17. ⚠️ See [EXPERIMENTAL_STATUS.md](EXPERIMENTAL_STATUS.md) for important limitations.

## Features

### Implemented
- ✅ **Lexical Analysis**: Full tokenization of GOM syntax
- ✅ **Parsing**: Recursive descent parser with precedence climbing
- ✅ **Code Generation**: Transpilation to C++17
- ✅ **Runtime Library**: Embedded GOM value types and operators
- ✅ **Core Language Features**:
  - Variables (const/var)
  - Functions (including arrow syntax)
  - Arithmetic and logical operations
  - Arrays with negative indexing (-1 indexing!)
  - If statements
  - Print statements
  - String interpolation basics

### Partial Support
- ⚠️ **Classes**: Basic structure parsing (codegen incomplete)
- ⚠️ **Async/Await**: Parsing only
- ⚠️ **When/After**: Not implemented

### Not Yet Implemented
- ❌ Probabilistic variables
- ❌ Lifetimes
- ❌ Fractional indexing
- ❌ Approximate equality (~=) - parsed but needs fuzzy logic
- ❌ Reactive programming (when statements)
- ❌ Import/export
- ❌ next/previous operators

## Building

```bash
cd compiler
mkdir build
cd build
cmake ..
make
```

This creates the `gomcc` executable.

## Usage

```bash
# Compile a GOM file to C++
./gomcc input.gom -o output.cpp

# Compile the generated C++ code
g++ -std=c++17 output.cpp -o program

# Run the program
./program
```

### Example

Create `test.gom`:
```gom
const x = 10!
const y = 20!
print "x + y = ${x + y}"!

function add(a, b) => a + b!
const result = add(5, 7)!
print "Result: ${result}"!

const list = [1, 2, 3, 4, 5]!
print "Last element: ${list[-1]}"!
```

Compile and run:
```bash
./gomcc test.gom -o test.cpp
g++ -std=c++17 test.cpp -o test
./test
```

## Architecture

### Components

1. **Lexer** (`src/lexer.cpp`)
   - Tokenizes source code
   - Handles strings, numbers, identifiers, operators, keywords
   - Preserves line/column information for error messages

2. **Parser** (`src/parser.cpp`)
   - Recursive descent with precedence climbing for expressions
   - Builds abstract syntax tree (AST)
   - Validates syntax

3. **AST** (`src/ast.cpp`)
   - Node types for all language constructs
   - Expression nodes: literals, binary ops, function calls, arrays
   - Statement nodes: declarations, functions, classes, control flow

4. **Code Generator** (`src/codegen.cpp`)
   - Traverses AST and emits C++ code
   - Embeds runtime library in generated code
   - Translates GOM semantics to C++

5. **Runtime Library** (embedded in codegen)
   - `GomValue`: Variant type holding number/string/bool/array
   - Operator implementations (arithmetic, logical, comparison)
   - Built-in functions (print, array indexing)
   - Automatic type conversions

### Runtime Type System

GOM values are represented by the `GomValue` class:

```cpp
class GomValue {
    std::variant<double, std::string, bool, std::vector<GomValue>> data;

    double as_number() const;
    std::string as_string() const;
    bool as_bool() const;
};
```

This enables dynamic typing while compiling to statically-typed C++.

## Compiler Pipeline

```
Source Code (.gom)
    ↓
[ Lexer ] → Tokens
    ↓
[ Parser ] → AST
    ↓
[ CodeGen ] → C++ Code
    ↓
[ g++ ] → Executable
```

## Testing

See `examples/` directory for test programs:

```bash
# Run all examples
for f in examples/*.gom; do
    echo "=== Compiling $f ==="
    ./gomcc "$f" -o temp.cpp
    g++ -std=c++17 temp.cpp -o temp
    ./temp
    echo
done
```

## Limitations

1. **No Three-Valued Logic**: Booleans are standard true/false (no "maybe")
2. **No Confidence Levels**: Probabilistic variables not supported
3. **Static Arrays**: No fractional indexing or dynamic insertion
4. **Synchronous Only**: Async/await not implemented
5. **No REPL**: Compilation only, no interactive mode
6. **Limited Error Messages**: Basic error reporting

## Future Enhancements

### Short Term
- Better error messages with source context
- More comprehensive runtime library
- Optimization passes
- Support for classes and objects

### Medium Term
- Separate compilation and linking
- Module system (import/export)
- Debugger integration
- Performance optimization

### Long Term
- LLVM backend for native code generation
- JIT compilation
- Probabilistic variables with confidence tracking
- Full reactive programming support

## Performance

The compiler generates straightforward C++ code without optimization.
For production use, compile generated code with optimization flags:

```bash
g++ -std=c++17 -O3 output.cpp -o program
```

## Contributing

This is a prototype compiler demonstrating feasibility of compiling GOM to C++.
For the reference implementation, see the Python interpreter in the parent directory.

## License

Same license as the Gulf of Mexico language project.
