#!/usr/bin/env python3
"""
Utility script to safely update backend dependencies.
This script helps manage package updates with conflict detection.
"""

import subprocess
import sys
import os
from typing import List, Dict


def run_command(command: List[str]) -> tuple[bool, str]:
    """
    Run a shell command and return success status and output.
    
    Args:
        command: List of command parts
        
    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def check_package_versions() -> Dict[str, str]:
    """
    Check current package versions.
    
    Returns:
        Dictionary of package names to versions
    """
    success, output = run_command([sys.executable, "-m", "pip", "list"])
    
    if not success:
        print(f"❌ Failed to get package list: {output}")
        return {}
    
    packages = {}
    for line in output.strip().split('\n')[2:]:  # Skip header lines
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                packages[parts[0].lower()] = parts[1]
    
    return packages


def check_outdated_packages() -> List[str]:
    """
    Check for outdated packages.
    
    Returns:
        List of outdated package names
    """
    success, output = run_command([sys.executable, "-m", "pip", "list", "--outdated"])
    
    if not success:
        print(f"❌ Failed to check outdated packages: {output}")
        return []
    
    outdated = []
    for line in output.strip().split('\n')[2:]:  # Skip header lines
        if line.strip():
            parts = line.split()
            if len(parts) >= 3:
                outdated.append(parts[0])
    
    return outdated


def upgrade_packages(dry_run: bool = True) -> bool:
    """
    Upgrade packages based on requirements.txt.
    
    Args:
        dry_run: If True, only show what would be updated
        
    Returns:
        Success status
    """
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    # First, let's see what would be updated
    print("📦 Checking for package updates...")
    
    current_packages = check_package_versions()
    outdated_packages = check_outdated_packages()
    
    if outdated_packages:
        print("\n📋 Outdated packages found:")
        for pkg in outdated_packages:
            current_version = current_packages.get(pkg.lower(), "unknown")
            print(f"  • {pkg}: {current_version}")
    else:
        print("✅ All packages are up to date!")
        return True
    
    if dry_run:
        print("\n🔍 This is a dry run. To actually update packages, run:")
        print("   python update_packages.py --upgrade")
        return True
    
    # Actually perform the upgrade
    print("\n🚀 Upgrading packages...")
    
    # Upgrade pip first
    print("⬆️  Upgrading pip...")
    success, output = run_command([
        sys.executable, "-m", "pip", "install", "--upgrade", "pip"
    ])
    
    if not success:
        print(f"❌ Failed to upgrade pip: {output}")
        return False
    
    # Install/upgrade requirements
    print("⬆️  Installing requirements...")
    success, output = run_command([
        sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"
    ])
    
    if not success:
        print(f"❌ Failed to upgrade packages: {output}")
        return False
    
    print("✅ Packages upgraded successfully!")
    return True


def check_security_vulnerabilities() -> None:
    """
    Check for known security vulnerabilities.
    """
    print("\n🔒 Checking for security vulnerabilities...")
    
    # Try to use pip-audit if available
    success, output = run_command([sys.executable, "-m", "pip", "show", "pip-audit"])
    
    if success:
        print("🔍 Running pip-audit...")
        success, audit_output = run_command([sys.executable, "-m", "pip-audit"])
        
        if success and "No known vulnerabilities found" in audit_output:
            print("✅ No security vulnerabilities found!")
        else:
            print("⚠️  Security check results:")
            print(audit_output)
    else:
        print("💡 Consider installing pip-audit for security scanning:")
        print("   pip install pip-audit")


def main():
    """
    Main function to handle command line arguments and run updates.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Safely update backend dependencies")
    parser.add_argument(
        "--upgrade", 
        action="store_true", 
        help="Actually perform the upgrade (default is dry run)"
    )
    parser.add_argument(
        "--security", 
        action="store_true", 
        help="Check for security vulnerabilities"
    )
    
    args = parser.parse_args()
    
    print("🔧 Backend Package Update Tool")
    print("=" * 40)
    
    # Change to backend directory if not already there
    if os.path.basename(os.getcwd()) != "backend":
        if os.path.exists("backend"):
            os.chdir("backend")
            print("📁 Changed to backend directory")
        else:
            print("❌ Backend directory not found!")
            sys.exit(1)
    
    # Perform the update check/upgrade
    success = upgrade_packages(dry_run=not args.upgrade)
    
    # Optional security check
    if args.security:
        check_security_vulnerabilities()
    
    if not success:
        sys.exit(1)
    
    print("\n🎉 Update process completed successfully!")


if __name__ == "__main__":
    main() 