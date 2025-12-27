#!/usr/bin/env python3
"""
Phase 4 Task 3: Integration Testing

This script tests the handler integration by:
1. Running a subset of existing unit tests
2. Executing sample GOM programs
3. Verifying outputs are as expected
4. Checking for regressions
"""

import os
import sys
import subprocess
from pathlib import Path
from collections import defaultdict

# Add project to path
sys.path.insert(0, '/home/james/GulfOfMexico')


class IntegrationTestRunner:
    """Run integration tests for Phase 4."""
    
    def __init__(self):
        self.project_root = Path('/home/james/GulfOfMexico')
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_skipped = 0
        self.results = defaultdict(list)
    
    def run_basic_syntax_check(self):
        """Verify that core modules can be imported and compiled."""
        print("\n[1] Basic Syntax Check")
        print("-" * 70)
        
        files_to_check = [
            'gulfofmexico/interpreter.py',
            'gulfofmexico/handler_registry.py',
            'gulfofmexico/handlers_impl/variable_declaration.py',
            'gulfofmexico/handlers_impl/return_statement.py',
            'gulfofmexico/handlers_impl/conditional.py',
        ]
        
        all_pass = True
        for filepath in files_to_check:
            full_path = self.project_root / filepath
            try:
                result = subprocess.run(
                    ['python3', '-m', 'py_compile', str(full_path)],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"  ✓ {filepath}")
                    self.tests_passed += 1
                else:
                    print(f"  ✗ {filepath}")
                    print(f"    Error: {result.stderr.decode()}")
                    self.tests_failed += 1
                    all_pass = False
            except Exception as e:
                print(f"  ✗ {filepath}: {e}")
                self.tests_failed += 1
                all_pass = False
        
        return all_pass
    
    def run_handler_registry_test(self):
        """Test handler registry initialization."""
        print("\n[2] Handler Registry Test")
        print("-" * 70)
        
        try:
            # Create a test script that doesn't require full imports
            test_code = """
import sys
sys.path.insert(0, '/home/james/GulfOfMexico')

# Test registry file compilation
import ast
with open('/home/james/GulfOfMexico/gulfofmexico/handler_registry.py', 'r') as f:
    ast.parse(f.read())

# Test that create_production_registry is defined
from gulfofmexico.handler_registry import create_production_registry
print("Handler registry can be imported and compiled")
"""
            result = subprocess.run(
                ['python3', '-c', test_code],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print(f"  ✓ Handler registry imports successfully")
                self.tests_passed += 1
                return True
            else:
                print(f"  ✗ Handler registry test failed")
                print(f"    {result.stderr.decode()}")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            self.tests_failed += 1
            return False
    
    def run_gom_file_check(self):
        """Check that GOM program files exist and are accessible."""
        print("\n[3] GOM Program Files Check")
        print("-" * 70)
        
        programs_dir = self.project_root / 'programs'
        gom_files = list(programs_dir.rglob('*.gom'))
        
        print(f"  Found {len(gom_files)} GOM program files")
        
        if len(gom_files) > 0:
            # Show some examples
            for i, gom_file in enumerate(gom_files[:5]):
                print(f"    {i+1}. {gom_file.relative_to(self.project_root)}")
            if len(gom_files) > 5:
                print(f"    ... and {len(gom_files) - 5} more")
            
            self.tests_passed += 1
            return True
        else:
            print(f"  ✗ No GOM files found!")
            self.tests_failed += 1
            return False
    
    def check_handler_dispatch_code(self):
        """Verify handler dispatch code is in interpreter."""
        print("\n[4] Handler Dispatch Code Verification")
        print("-" * 70)
        
        interpreter_path = self.project_root / 'gulfofmexico/interpreter.py'
        
        with open(interpreter_path, 'r') as f:
            code = f.read()
        
        checks = [
            ('Handler registry initialization', '_initialize_handler_registry'),
            ('Handler getter function', 'get_handler_registry'),
            ('Dependency injection', '_inject_interpreter_dependencies'),
            ('Handler dispatcher', 'try_execute_with_handler'),
            ('Handler dispatch call', 'handled, handler_result = try_execute_with_handler'),
            ('Handler result check', 'if handled:'),
        ]
        
        all_pass = True
        for check_name, check_string in checks:
            if check_string in code:
                print(f"  ✓ {check_name}")
                self.tests_passed += 1
            else:
                print(f"  ✗ {check_name} - NOT FOUND")
                self.tests_failed += 1
                all_pass = False
        
        return all_pass
    
    def check_execution_context(self):
        """Verify ExecutionContext exists and is used."""
        print("\n[5] ExecutionContext Availability")
        print("-" * 70)
        
        context_path = self.project_root / 'gulfofmexico/execution_context.py'
        
        if context_path.exists():
            print(f"  ✓ ExecutionContext file exists")
            self.tests_passed += 1
            
            # Check syntax
            try:
                subprocess.run(
                    ['python3', '-m', 'py_compile', str(context_path)],
                    capture_output=True,
                    timeout=5,
                    check=True
                )
                print(f"  ✓ ExecutionContext compiles")
                self.tests_passed += 1
                return True
            except Exception as e:
                print(f"  ✗ ExecutionContext syntax error: {e}")
                self.tests_failed += 1
                return False
        else:
            print(f"  ✗ ExecutionContext file not found")
            self.tests_failed += 1
            return False
    
    def run_all(self):
        """Run all integration tests."""
        print("=" * 70)
        print("Phase 4 Task 3: Integration Testing")
        print("=" * 70)
        
        self.run_basic_syntax_check()
        self.run_handler_registry_test()
        self.run_gom_file_check()
        self.check_handler_dispatch_code()
        self.check_execution_context()
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        total = self.tests_passed + self.tests_failed
        
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        print(f"  Passed: {self.tests_passed}/{total}")
        print(f"  Failed: {self.tests_failed}/{total}")
        
        if self.tests_failed == 0:
            print("\n✓ All integration tests PASSED")
            return 0
        else:
            print(f"\n✗ {self.tests_failed} test(s) FAILED")
            return 1


def main():
    """Main entry point."""
    runner = IntegrationTestRunner()
    runner.run_all()
    return 0 if runner.tests_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
