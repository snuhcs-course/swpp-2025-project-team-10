#!/usr/bin/env python3
"""
Python Code Formatter Script

This script formats Python code using black, isort, and runs flake8 for linting.
It can be used as a standalone script or integrated into pre-commit hooks.

Usage:
    python scripts/formatters/format_python.py [--check] [--diff] [paths...]
    
Arguments:
    --check: Don't write back modified files, just return status
    --diff: Show diffs instead of rewriting files
    paths: Specific paths to format (default: backend/src ai-model/src backend/tests ai-model/tests)
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class PythonFormatter:
    """Python code formatter using black, isort, and flake8."""
    
    def __init__(self, check_mode: bool = False, show_diff: bool = False):
        self.check_mode = check_mode
        self.show_diff = show_diff
        self.project_root = Path(__file__).parent.parent.parent
        
    def run_command(self, cmd: List[str], description: str) -> bool:
        """Run a command and return True if successful."""
        print(f"Running {description}...")
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
                
            return result.returncode == 0
        except FileNotFoundError:
            print(f"Error: Command not found. Please install the required tools.")
            return False
    
    def format_with_black(self, paths: List[str]) -> bool:
        """Format code with black."""
        cmd = ["python", "-m", "black"]
        
        if self.check_mode:
            cmd.append("--check")
        if self.show_diff:
            cmd.append("--diff")
            
        cmd.extend(paths)
        return self.run_command(cmd, "black formatting")
    
    def sort_imports_with_isort(self, paths: List[str]) -> bool:
        """Sort imports with isort."""
        cmd = ["python", "-m", "isort"]
        
        if self.check_mode:
            cmd.append("--check-only")
        if self.show_diff:
            cmd.append("--diff")
            
        cmd.extend(paths)
        return self.run_command(cmd, "isort import sorting")
    
    def lint_with_flake8(self, paths: List[str]) -> bool:
        """Lint code with flake8."""
        cmd = ["python", "-m", "flake8"] + paths
        return self.run_command(cmd, "flake8 linting")
    
    def type_check_with_mypy(self, paths: List[str]) -> bool:
        """Type check with mypy."""
        cmd = ["python", "-m", "mypy"] + paths
        return self.run_command(cmd, "mypy type checking")
    
    def security_check_with_bandit(self, paths: List[str]) -> bool:
        """Security check with bandit."""
        # Filter to only source directories for bandit
        src_paths = [p for p in paths if "src" in p and not p.endswith("tests")]
        if not src_paths:
            print("No source paths found for bandit security check")
            return True
            
        cmd = ["python", "-m", "bandit", "-r"] + src_paths
        return self.run_command(cmd, "bandit security checking")
    
    def format_all(self, paths: List[str]) -> bool:
        """Run all formatting and checking tools."""
        success = True
        
        # Filter existing paths
        existing_paths = []
        for path in paths:
            path_obj = self.project_root / path
            if path_obj.exists():
                existing_paths.append(path)
            else:
                print(f"Warning: Path {path} does not exist, skipping...")
        
        if not existing_paths:
            print("No valid paths found to format")
            return False
        
        print(f"Formatting Python code in: {', '.join(existing_paths)}")
        print("=" * 60)
        
        # Run formatters (only if not in check mode)
        if not self.check_mode:
            if not self.sort_imports_with_isort(existing_paths):
                success = False
            
            if not self.format_with_black(existing_paths):
                success = False
        else:
            # In check mode, run checks
            if not self.sort_imports_with_isort(existing_paths):
                print("❌ Import sorting check failed")
                success = False
            else:
                print("✅ Import sorting check passed")
                
            if not self.format_with_black(existing_paths):
                print("❌ Black formatting check failed")
                success = False
            else:
                print("✅ Black formatting check passed")
        
        # Always run linting
        if not self.lint_with_flake8(existing_paths):
            print("❌ Flake8 linting failed")
            success = False
        else:
            print("✅ Flake8 linting passed")
        
        # Run type checking
        if not self.type_check_with_mypy(existing_paths):
            print("❌ MyPy type checking failed")
            success = False
        else:
            print("✅ MyPy type checking passed")
        
        # Run security checking
        if not self.security_check_with_bandit(existing_paths):
            print("❌ Bandit security check failed")
            success = False
        else:
            print("✅ Bandit security check passed")
        
        print("=" * 60)
        if success:
            print("🎉 All Python formatting and checks passed!")
        else:
            print("💥 Some Python formatting or checks failed!")
            
        return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Format Python code using black, isort, and run quality checks"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Don't write back modified files, just return status"
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Show diffs instead of rewriting files"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["backend/src", "ai-model/src", "backend/tests", "ai-model/tests"],
        help="Paths to format (default: backend/src ai-model/src backend/tests ai-model/tests)"
    )
    
    args = parser.parse_args()
    
    formatter = PythonFormatter(check_mode=args.check, show_diff=args.diff)
    success = formatter.format_all(args.paths)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
