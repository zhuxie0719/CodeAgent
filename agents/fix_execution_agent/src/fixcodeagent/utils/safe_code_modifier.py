"""
Safe code modification utility that preserves indentation and verifies syntax.

This utility helps prevent indentation errors when modifying Python code files.
"""

import sys
import py_compile
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def safe_replace_in_file(
    file_path: str,
    replacements: Dict[str, str],
    verify_syntax: bool = True,
    context_lines: int = 5
) -> Tuple[bool, str]:
    """
    Safely replace strings in a file while preserving indentation.
    
    Args:
        file_path: Path to the file to modify
        replacements: Dictionary mapping old strings to new strings
        verify_syntax: Whether to verify Python syntax after modification
        context_lines: Number of context lines to show in error messages
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    try:
        # Read file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        original_lines = lines.copy()
        modified = False
        
        # Perform replacements while preserving indentation
        for i, line in enumerate(lines):
            original_line = line
            for old_str, new_str in replacements.items():
                if old_str in line:
                    # Preserve indentation
                    indent = len(line) - len(line.lstrip())
                    # Replace in the line content (without leading whitespace)
                    new_content = line.lstrip().replace(old_str, new_str)
                    # Reconstruct line with original indentation
                    lines[i] = ' ' * indent + new_content
                    modified = True
                    break
        
        if not modified:
            return True, "No replacements were made (strings not found in file)"
        
        # Verify syntax before writing (if Python file)
        if verify_syntax and file_path.suffix == '.py':
            # Write to temporary location first
            temp_file = file_path.with_suffix('.py.tmp')
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                # Verify syntax
                try:
                    py_compile.compile(str(temp_file), doraise=True)
                except py_compile.PyCompileError as e:
                    # Show context around the error
                    error_line = getattr(e, 'lineno', 0)
                    start = max(0, error_line - context_lines - 1)
                    end = min(len(lines), error_line + context_lines)
                    context = ''.join(f"{i+1:4d}: {lines[i]}" for i in range(start, end))
                    return False, f"Syntax error at line {error_line}:\n{e}\n\nContext:\n{context}"
                
                # Syntax is valid, replace original file
                temp_file.replace(file_path)
                return True, f"Successfully modified {file_path} with {len(replacements)} replacement(s)"
            except Exception as e:
                if temp_file.exists():
                    temp_file.unlink()
                return False, f"Error during syntax verification: {e}"
        else:
            # Write directly (non-Python file or syntax verification disabled)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True, f"Successfully modified {file_path} with {len(replacements)} replacement(s)"
    
    except Exception as e:
        return False, f"Error modifying file: {e}"


def safe_replace_multiple(
    file_path: str,
    old_string: str,
    new_string: str,
    verify_syntax: bool = True
) -> Tuple[bool, str]:
    """
    Convenience function for single string replacement.
    
    Args:
        file_path: Path to the file to modify
        old_string: String to replace
        new_string: Replacement string
        verify_syntax: Whether to verify Python syntax after modification
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    return safe_replace_in_file(file_path, {old_string: new_string}, verify_syntax)


def verify_file_syntax(file_path: str) -> Tuple[bool, str]:
    """
    Verify Python syntax of a file.
    
    Args:
        file_path: Path to the Python file to verify
    
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    if file_path.suffix != '.py':
        return True, "Not a Python file, skipping syntax check"
    
    try:
        py_compile.compile(str(file_path), doraise=True)
        return True, f"Syntax check passed for {file_path}"
    except py_compile.PyCompileError as e:
        return False, f"Syntax error in {file_path}: {e}"


def main():
    """Command-line interface for safe code modification."""
    if len(sys.argv) < 4:
        print("Usage: safe_code_modifier.py <file_path> <old_string> <new_string> [--no-verify]")
        print("   or: safe_code_modifier.py <file_path> --verify")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if sys.argv[2] == '--verify':
        success, message = verify_file_syntax(file_path)
        print(message)
        sys.exit(0 if success else 1)
    
    old_string = sys.argv[2]
    new_string = sys.argv[3]
    verify_syntax = '--no-verify' not in sys.argv
    
    success, message = safe_replace_multiple(file_path, old_string, new_string, verify_syntax)
    print(message)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

