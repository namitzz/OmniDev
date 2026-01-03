#!/usr/bin/env python3
"""
Check system requirements and dependencies
"""

import sys
import subprocess
import importlib.util
from pathlib import Path


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11 or later required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_command(command: str) -> bool:
    """Check if a command exists"""
    try:
        subprocess.run(
            [command, "--version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_python_package(package: str) -> bool:
    """Check if a Python package is installed"""
    return importlib.util.find_spec(package) is not None


def main():
    print("🔍 Checking OmniDev requirements...\n")
    
    all_ok = True
    
    # Check Python version
    if not check_python_version():
        all_ok = False
    
    # Check Node.js
    if check_command("node"):
        print("✓ Node.js installed")
    else:
        print("❌ Node.js not found")
        all_ok = False
    
    # Check npm
    if check_command("npm"):
        print("✓ npm installed")
    else:
        print("❌ npm not found")
        all_ok = False
    
    # Check git
    if check_command("git"):
        print("✓ git installed")
    else:
        print("❌ git not found")
        all_ok = False
    
    # Check optional tools
    print("\nOptional tools:")
    if check_command("rg"):
        print("✓ ripgrep (rg) installed")
    else:
        print("⚠️  ripgrep not found (recommended for fast search)")
    
    # Check Python packages
    print("\nChecking Python packages...")
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "sqlalchemy",
        "openai", "chromadb", "structlog"
    ]
    
    for package in required_packages:
        if check_python_package(package):
            print(f"✓ {package}")
        else:
            print(f"❌ {package} not installed")
            all_ok = False
    
    # Check environment file
    print("\nChecking configuration...")
    if Path(".env").exists():
        print("✓ .env file exists")
    else:
        print("⚠️  .env file not found (run setup.sh)")
    
    # Check directories
    if Path("data").exists():
        print("✓ data directory exists")
    else:
        print("⚠️  data directory not found")
    
    if Path("logs").exists():
        print("✓ logs directory exists")
    else:
        print("⚠️  logs directory not found")
    
    print("\n" + "="*50)
    if all_ok:
        print("✅ All requirements met!")
    else:
        print("❌ Some requirements missing. Run scripts/setup.sh")
    print("="*50)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
