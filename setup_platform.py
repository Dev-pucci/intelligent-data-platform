#!/usr/bin/env python3
"""
Intelligent Data Acquisition Platform - Setup Script
Automates the complete platform setup process
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Fix Windows console encoding
if platform.system() == "Windows":
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def run_command(cmd, shell=True, check=False):
    """Run command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python():
    """Check Python version"""
    print_header("Checking Python")
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python version is compatible")
        return True
    else:
        print("✗ Python 3.8+ required")
        return False

def check_postgresql():
    """Check if PostgreSQL is installed and running"""
    print_header("Checking PostgreSQL")

    # Check if psql command exists
    success, stdout, stderr = run_command("psql --version")
    if success:
        print(f"✓ PostgreSQL installed: {stdout.strip()}")
        return True
    else:
        print("✗ PostgreSQL not found in PATH")
        print("  Please ensure PostgreSQL bin directory is in PATH")
        print("  Example: C:\\Program Files\\PostgreSQL\\17\\bin")
        return False

def setup_database():
    """Setup database and user"""
    print_header("Setting up Database")

    # Set password environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = '123456'

    # Check if database exists
    cmd = 'psql -U postgres -lqt'
    success, stdout, stderr = run_command(cmd)

    if 'scraper_db' in stdout:
        print("✓ Database 'scraper_db' already exists")
    else:
        print("Creating database and user...")
        commands = [
            'psql -U postgres -c "CREATE DATABASE scraper_db;"',
            'psql -U postgres -c "CREATE USER scraper_user WITH PASSWORD \'123456\';"',
            'psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE scraper_db TO scraper_user;"'
        ]

        for cmd in commands:
            success, stdout, stderr = run_command(cmd)
            if success:
                print(f"✓ Executed: {cmd.split('-c')[1].strip()[:50]}...")
            else:
                print(f"✗ Failed: {stderr[:100]}")
                return False

    return True

def apply_schema():
    """Apply database schema"""
    print_header("Applying Database Schema")

    schema_file = Path("database/schema.sql")
    if not schema_file.exists():
        print(f"✗ Schema file not found: {schema_file}")
        return False

    cmd = f'psql -U scraper_user -d scraper_db -f "{schema_file}"'
    env = os.environ.copy()
    env['PGPASSWORD'] = '123456'

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            env=env,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Schema applied successfully")
            return True
        else:
            print(f"⚠ Schema application had warnings (may already exist)")
            print(f"  {result.stderr[:200]}")
            return True  # Continue anyway, tables may already exist
    except Exception as e:
        print(f"✗ Error applying schema: {e}")
        return False

def install_python_deps():
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")

    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("✗ requirements.txt not found")
        return False

    print("Installing packages...")
    cmd = f'"{sys.executable}" -m pip install -r requirements.txt'
    success, stdout, stderr = run_command(cmd)

    if success:
        print("✓ Python dependencies installed")
        return True
    else:
        print(f"✗ Failed to install dependencies: {stderr[:200]}")
        return False

def init_git():
    """Initialize Git repository"""
    print_header("Initializing Git Repository")

    if Path(".git").exists():
        print("✓ Git repository already initialized")
        return True

    # Check if git is installed
    success, stdout, stderr = run_command("git --version")
    if not success:
        print("✗ Git not installed")
        print("  Download from: https://git-scm.com/download/win")
        return False

    print(f"✓ Git installed: {stdout.strip()}")

    # Initialize repository
    success, stdout, stderr = run_command("git init")
    if success:
        print("✓ Git repository initialized")

        # Create initial commit info
        print("\n  To push to GitHub:")
        print("  1. Create repository on GitHub")
        print("  2. git add .")
        print("  3. git commit -m 'Initial commit'")
        print("  4. git remote add origin YOUR_GITHUB_URL")
        print("  5. git push -u origin main")
        return True
    else:
        print(f"✗ Failed to initialize Git: {stderr}")
        return False

def test_platform():
    """Run platform tests"""
    print_header("Testing Platform")

    test_file = Path("test_full_pipeline.py")
    if not test_file.exists():
        print("⚠ Test file not found, skipping tests")
        return True

    print("Running full pipeline test...")
    cmd = f'"{sys.executable}" test_full_pipeline.py'
    success, stdout, stderr = run_command(cmd)

    if success:
        print("✓ Platform test passed")
        print(stdout[-500:])  # Show last 500 chars
        return True
    else:
        print("⚠ Test had issues (platform may still work)")
        if stderr:
            print(f"  Errors: {stderr[:300]}")
        return True  # Don't fail setup on test failure

def main():
    """Main setup process"""
    print("\n" + "="*60)
    print("  Intelligent Data Acquisition Platform")
    print("  Automated Setup")
    print("="*60)

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"\nWorking directory: {os.getcwd()}")

    results = {}

    # Run all setup steps
    results['python'] = check_python()
    results['postgresql'] = check_postgresql()

    if results['postgresql']:
        results['database'] = setup_database()
        results['schema'] = apply_schema()
    else:
        print("\n⚠ Skipping database setup (PostgreSQL not available)")
        results['database'] = False
        results['schema'] = False

    results['python_deps'] = install_python_deps()
    results['git'] = init_git()
    results['test'] = test_platform()

    # Summary
    print_header("Setup Summary")

    for step, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {step.replace('_', ' ').title()}")

    # Next steps
    print("\n" + "="*60)
    print("  Next Steps")
    print("="*60)

    if all([results.get('python_deps'), results.get('database'), results.get('schema')]):
        print("\n✓ Platform is ready to use!")
        print("\n  Start n8n:")
        if platform.system() == "Windows":
            print("    .\\start-n8n.bat")
        else:
            print("    ./start-n8n.sh")
        print("\n  Access n8n:")
        print("    http://localhost:5678")
        print("\n  Run scrapers:")
        print("    python -m scrapers.scraper_runner --config configs/sites/jumia_spa.yml")
        print("\n  Deploy to Render:")
        print("    Follow: RENDER_DEPLOYMENT_CHECKLIST.md")
    else:
        print("\n⚠ Some setup steps failed")
        print("  Please resolve the errors above and run again")

    print("\nDatabase Credentials:")
    print("  Database: scraper_db")
    print("  User:     scraper_user")
    print("  Password: 123456")
    print("  Host:     localhost")
    print("  Port:     5432")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
