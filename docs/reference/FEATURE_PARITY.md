# Gulf of Mexico Feature Parity Analysis

This document tracks feature parity between the Python interpreter and C++ compiler.

## Current Status (Pre-Consolidation)

### Core Language Features

| Feature | Python Interpreter | C++ Compiler | Notes |
|---------|-------------------|--------------|-------|
| **Variables** |
| const | ✅ | ✅ | Both support |
| var | ✅ | ✅ | Both support |
| const var | ✅ | ❌ | Interpreter only |
| **Functions** |
| function keyword | ✅ | ✅ | Both support |
| fn shorthand | ✅ | ✅ | Both support |
| Arrow syntax => | ✅ | ✅ | Both support |
| async functions | ✅ | ⚠️ | Compiler parses only |
| **Classes** |
| class declaration | ✅ | ⚠️ | Compiler parses only |
| new operator | ✅ | ✅ | Both support |
| init constructor | ✅ | ❌ | Interpreter only |
| **Control Flow** |
| if statements | ✅ | ✅ | Both support |
| when (reactive) | ✅ | ❌ | Interpreter only |
| after (delayed) | ✅ | ❌ | Interpreter only |
| **Operators** |
| Arithmetic (+,-,*,/,%) | ✅ | ✅ | Both support |
| Comparison (<,>,<=,>=) | ✅ | ✅ | Both support |
| Equality (==, !=) | ✅ | ✅ | Both support |
| Approximate = | ✅ | ❌ | Interpreter only |
| Triple === | ✅ | ❌ | Interpreter only |
| Quad ==== | ✅ | ❌ | Interpreter only |
| Logical (&, \|, ;) | ✅ | ✅ | Both support |
| **Data Types** |
| Numbers | ✅ | ✅ | Both support |
| Strings | ✅ | ✅ | Both support |
| Booleans | ✅ | ✅ | Both support |
| Arrays | ✅ | ✅ | Both support |
| Maps/Dicts | ✅ | ❌ | Interpreter only |
| Undefined | ✅ | ✅ | Both support |
| **Array Features** |
| -1 indexing | ✅ | ✅ | Both support |
| Fractional indexing | ✅ | ❌ | Interpreter only |
| **Special Features** |
| Three-valued logic | ✅ | ❌ | Interpreter only |
| Probabilistic vars | ✅ | ❌ | Interpreter only |
| Lifetimes | ✅ | ❌ | Interpreter only |
| String interpolation | ✅ | ⚠️ | Basic in compiler |
| Confidence levels | ✅ | ❌ | Interpreter only |
| **Statements** |
| return | ✅ | ✅ | Both support |
| delete | ✅ | ❌ | Interpreter only |
| reverse | ✅ | ❌ | Interpreter only |
| import | ✅ | ❌ | Interpreter only |
| export | ✅ | ❌ | Interpreter only |
| **Built-in Functions** |
| print() | ✅ | ✅ | Both support |
| Number() | ✅ | ❌ | Interpreter only |
| String() | ✅ | ❌ | Interpreter only |
| Boolean() | ✅ | ❌ | Interpreter only |
| Map() | ✅ | ❌ | Interpreter only |
| sleep() | ✅ | ❌ | Interpreter only |
| exit() | ✅ | ❌ | Interpreter only |
| read()/write() | ✅ | ❌ | Interpreter only |
| Math functions | ✅ | ❌ | Interpreter only |
| Regex functions | ✅ | ❌ | Interpreter only |
| Word numbers | ✅ | ❌ | Interpreter only |

### Satirical Features (Interpreter Only)

| Feature Category | Keywords | Status in Compiler |
|-----------------|----------|-------------------|
| **Try/Whatever** | try, whatever | ❌ Not implemented |
| **Procrastination** | later, eventually, whenever | ❌ Not implemented |
| **Corporate Speak** | synergize, leverage, paradigm_shift, circle_back, touch_base | ❌ Not implemented |
| **Emotional** | happy, sad, angry, excited, tired | ❌ Not implemented |
| **Superstitious** | lucky, unlucky, cross_fingers, knock_on_wood | ❌ Not implemented |
| **Quantum** | quantum | ❌ Not implemented |
| **Time Travel** | time_travel | ❌ Not implemented |
| **Gaslighting** | definitely_not | ❌ Not implemented |
| **Blockchain** | blockchain, smart_contract, mine, immutable_ledger, token, nft, web3, dao, defi, hodl | ❌ Not implemented |
| **AI Buzzwords** | ai_powered, deep_learning, neural_network, machine_learning | ❌ Not implemented |
| **Agile** | sprint, standup, retro, burndown | ❌ Not implemented |
| **Security Theater** | penetration_test, vulnerability_scan, security_audit, compliance_check | ❌ Not implemented |
| **DevOps** | containerize, orchestrate, microservice, kubernetes | ❌ Not implemented |
| **Startup** | pivot, disrupt, unicorn, hockey_stick | ❌ Not implemented |

### Analysis Functions (Interpreter Only - Recently Added)

| Category | Functions | Status in Compiler |
|----------|-----------|-------------------|
| **Statistical** | mean, median, mode, variance, stdev, min_val, max_val, sum_list, percentile, correlation | ❌ Not implemented |
| **Financial** | compound_interest, simple_interest, pmt, fv, pv, npv | ❌ Not implemented |
| **Business** | roi, profit_margin, cagr, break_even | ❌ Not implemented |
| **Scientific** | linear_regression, predict, derivative, integrate, quadratic_solve | ❌ Not implemented |
| **Base/Radix** | to_base, from_base, base_add, base_sub, base_mul, base_div, to_binary, to_octal, to_hex, from_binary, from_octal, from_hex | ❌ Not implemented |

## Consolidation Plan

### Phase 1: Core Language Parity (High Priority)
1. Add to compiler:
   - `const var` support
   - delete statement
   - reverse statement
   - Approximate equality operators (=, ===, ====)
   - Full string interpolation
   
### Phase 2: Extended Operators (Medium Priority)
2. Add to compiler:
   - Map/Dictionary type
   - Type conversion functions (Number, String, Boolean)
   
### Phase 3: Built-in Functions (Medium Priority)
3. Add to compiler:
   - Basic I/O: read(), write()
   - Control: sleep(), exit()
   - Math functions (from math.h)
   
### Phase 4: Advanced Features (Lower Priority)
4. Decide on scope for:
   - Probabilistic variables (complex in compiled code)
   - Lifetimes (complex in compiled code)
   - Fractional indexing (performance implications)
   - Three-valued logic (requires runtime changes)
   - When/After reactive programming (requires event loop)
   
### Phase 5: Satirical Features (Optional)
5. Add satirical keywords to compiler:
   - All emotional/superstitious/corporate keywords
   - Blockchain/AI/Agile buzzwords
   - These can compile to no-ops or simple transformations

### Phase 6: Analysis Functions (Optional)
6. Add analysis functions to compiler:
   - Link against standard math libraries
   - Implement statistical/financial functions in C++
   - These would be faster in compiled code!

## Implementation Strategy

### For Compiler Updates:
1. Update lexer keywords map
2. Add token types to enum
3. Add parsing logic in parser.cpp
4. Add AST node types in ast.h
5. Add code generation in codegen.cpp
6. Update runtime library if needed

### For Interpreter Updates:
All recent features are already in interpreter. Focus on:
1. Ensure documentation is complete
2. Add tests for new features
3. Verify all features work correctly

## Target Completion

- **Phase 1**: Essential for basic parity - 2-3 hours
- **Phase 2**: Nice to have - 1-2 hours
- **Phase 3**: Good for completeness - 2-3 hours
- **Phase 4**: Requires design decisions - TBD
- **Phase 5**: Fun additions - 1-2 hours
- **Phase 6**: Performance boost - 3-4 hours

## Testing Strategy

For each feature added to compiler:
1. Create .gom test file
2. Compile with gomcc
3. Compare output with Python interpreter
4. Verify identical behavior

## Documentation Updates Needed

1. Update compiler/README.md with new features
2. Update COMPILER_COMPLETE.md
3. Keep this FEATURE_PARITY.md updated
4. Update main README.md to reflect both implementations

## Success Criteria

✅ Compiler can handle all example programs in programs/examples/
✅ Core language features work identically in both
✅ Documentation is clear about which features are available where
✅ Test suite covers both implementations
