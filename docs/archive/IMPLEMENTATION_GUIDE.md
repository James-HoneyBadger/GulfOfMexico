# Gulf of Mexico - Implementation Quick Reference
> Archived document: Reflects pre-Nov 2025 repository layout. References to internal GOM test folders are historical; current user-facing programs live in `programs/examples/` and `programs/demos/`.

## Two Implementations Available

### Python Interpreter (Full-Featured)
**Location**: `gulfofmexico/` directory
**Run**: `python3 run_gom.py program.gom`
**Features**: 100+ language features, all satirical keywords, all analysis functions

### C++ Compiler (Performance-Focused)
**Location**: `compiler/` directory  
**Build**: `cd compiler/build && cmake .. && make`
**Run**: `./gomcc program.gom -o output.cpp && g++ -std=c++17 output.cpp -o program && ./program`
**Features**: Core language features, working on parity

## Feature Support Matrix

| Feature | Interpreter | Compiler | Notes |
|---------|------------|----------|-------|
| **Variables & Functions** |
| const, var | ✅ | ✅ | Identical |
| const var | ✅ | ⏳ | Coming to compiler |
| Functions | ✅ | ✅ | Identical |
| Async | ✅ | ⏳ | Parsed but not executed |
| **Control Flow** |
| if statements | ✅ | ✅ | Identical |
| when (reactive) | ✅ | ❌ | Interpreter only |
| after (delayed) | ✅ | ❌ | Interpreter only |
| **Data Types** |
| Numbers, Strings, Booleans | ✅ | ✅ | Identical |
| Arrays with -1 indexing | ✅ | ✅ | **Signature feature!** |
| Maps/Dictionaries | ✅ | ⏳ | Coming to compiler |
| **Operators** |
| Arithmetic (+,-,*,/,%) | ✅ | ✅ | Identical |
| Comparison (<,>,<=,>=) | ✅ | ✅ | Identical |
| Equality (==, !=) | ✅ | ✅ | Identical |
| Approximate (=) | ✅ | ⏳ | Lexer done, parser needed |
| Triple (===) | ✅ | ⏳ | Lexer done, parser needed |
| Quad (====) | ✅ | ⏳ | Lexer done, parser needed |
| **Built-in Functions** |
| print() | ✅ | ✅ | Identical |
| Number(), String(), Boolean() | ✅ | ⏳ | Coming to compiler |
| Math functions | ✅ | ⏳ | Coming to compiler |
| File I/O | ✅ | ⏳ | Coming to compiler |
| **Satirical Features** |
| All 13 categories | ✅ | ⏳ | Lexer done, parser needed |
| **Analysis Functions** |
| Statistical (10 funcs) | ✅ | ⏳ | Coming to compiler |
| Financial (6 funcs) | ✅ | ⏳ | Coming to compiler |
| Business (4 funcs) | ✅ | ⏳ | Coming to compiler |
| Scientific (5 funcs) | ✅ | ⏳ | Coming to compiler |
| Base conversion (12 funcs) | ✅ | ⏳ | Coming to compiler |

**Legend**: ✅ Works | ⏳ In Progress | ❌ Not Planned

## When to Use Which

### Use Python Interpreter When:
- Developing and testing code
- Using satirical features (emotional, blockchain, AI buzzwords, etc.)
- Using analysis functions (statistics, finance, science)
- Need reactive programming (when/after)
- Need probabilistic variables
- Rapid prototyping

### Use C++ Compiler When:
- Need maximum performance (100x+ faster)
- Deploying production code
- Using only core language features
- Want standalone executable
- Have simple programs without advanced features

## Current Consolidation Status

### Phase 1: Lexer ✅ COMPLETE
- All keywords recognized
- All operators tokenized
- Compiler builds successfully

### Phase 2: Parser ⏳ IN PROGRESS  
- Need to add statement parsing for satirical features
- Estimated time: 2-3 hours

### Phase 3: Code Generation ⏳ PENDING
- Need to generate C++ for new statements
- Estimated time: 2-3 hours

### Phase 4: Runtime Library ⏳ PENDING
- Need to add built-in functions
- Need to add analysis functions
- Estimated time: 4-5 hours

## Example Programs

### Works in Both
```gom
const x 10!
const y 20!
print "Sum: ${x + y}"!

function add(a, b) => a + b!
const result add(x, y)!

const arr [1, 2, 3, 4, 5]!
print "Last: ${arr[-1]}"!  // -1 indexing!
```

### Interpreter Only (For Now)
```gom
// Satirical features
happy {
   print "Everything is great!"!
}

blockchain {
   print "Decentralized!"!
}

// Analysis functions
const data [85, 90, 78, 92, 88]!
const avg mean(data)!
print "Average: ${avg}"!
```

## Development Workflow

### Recommended Approach
1. **Write code** using full interpreter
2. **Test thoroughly** with all features
3. **Compile** if using only core features
4. **Deploy** compiled version for performance

### Migration Path
As compiler gains features:
1. Check FEATURE_PARITY.md
2. Test program with both implementations
3. Switch to compiled version when supported

## Documentation

- **FEATURE_PARITY.md** - Complete feature comparison
- **CONSOLIDATION_PROGRESS.md** - Implementation status
- **CONSOLIDATION_SUMMARY.md** - High-level overview
- **README.md** - User guide for interpreter
- **compiler/README.md** - Compiler documentation

## Testing

### Test a program in both:
```bash
# Interpreter
python3 run_gom.py myprogram.gom

# Compiler (when features supported)
cd compiler/build
./gomcc ../../myprogram.gom -o test.cpp
g++ -std=c++17 test.cpp -o test
./test
```

## Contributing

### To Add Compiler Support for a Feature:
1. Update `compiler/src/lexer.cpp` (if new keyword) ✅ DONE
2. Update `compiler/include/lexer.h` (token type) ✅ DONE
3. Update `compiler/src/parser.cpp` (parsing logic) ⏳ TODO
4. Update `compiler/include/ast.h` (AST node) ⏳ TODO
5. Update `compiler/src/codegen.cpp` (C++ generation) ⏳ TODO
6. Test and document

## Quick Links

- Interpreter: `/home/james/GulfOfMexico/gulfofmexico/`
- Compiler: `/home/james/GulfOfMexico/compiler/`
- Examples: `/home/james/GulfOfMexico/programs/examples/`
- Tests: `/home/james/GulfOfMexico/tests/`

## Support

For questions about feature support:
1. Check FEATURE_PARITY.md
2. Try with interpreter first
3. Check compiler documentation
4. Refer to example programs

---

**Last Updated**: November 17, 2025
**Interpreter Version**: Full feature set
**Compiler Version**: Core features + lexer for all keywords
**Consolidation Status**: Phase 1 complete, Phase 2-4 in progress
