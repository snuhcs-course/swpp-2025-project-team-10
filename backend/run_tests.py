#!/usr/bin/env python
"""
Simple test runner for the Book Bartering Social Network backend.
This script provides easy access to all test utilities.
"""

import os
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and display results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")

    try:
        # Change to backend directory
        backend_dir = Path(__file__).parent
        os.chdir(backend_dir)

        # Activate virtual environment and run command
        if os.name == "nt":  # Windows
            venv_activate = r".\.venv\Scripts\Activate.ps1"
            full_command = f'powershell -Command "{venv_activate}; {command}"'
        else:  # Unix/Linux/Mac
            venv_activate = "./.venv/bin/activate"
            full_command = f"source {venv_activate} && {command}"

        result = subprocess.run(
            full_command, shell=True, capture_output=True, text=True
        )

        if result.returncode == 0:
            print("SUCCESS!")
            print(result.stdout)
        else:
            print("FAILED!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

    except Exception as e:
        print(f"Error running command: {e}")


def show_menu():
    """Show the test menu."""
    print("\nBook Bartering Backend - Test Runner")
    print("=" * 50)
    print("\n📋 Unit Tests (pytest)")
    print("1. Run All Unit Tests")
    print("2. Run All Unit Tests with Coverage")
    print("3. Run Books App Tests")
    print("4. Run Books App Tests with Coverage")
    print("5. Run Accounts App Tests")
    print("6. Run Specific Test File")
    print("\n🔧 Integration & Debug Tests")
    print("7. Quick API Integration Test")
    print("8. Authentication Debug Test")
    print("9. Server Test (Django Client)")
    print("\n⚙️  Django Management")
    print("10. Show Available URLs")
    print("11. Run Django Checks")
    print("12. Run Database Migrations")
    print("13. Create Superuser")
    print("14. Start Development Server")
    print("\n0. Exit")


def main():
    """Main function."""
    while True:
        show_menu()
        choice = input("\nEnter your choice (0-14): ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        # Unit Tests (pytest)
        elif choice == "1":
            run_command(
                "python -m pytest -v",
                "Run All Unit Tests",
            )
        elif choice == "2":
            run_command(
                "python -m pytest --cov=. --cov-report=term-missing "
                "--cov-report=html",
                "Run All Unit Tests with Coverage",
            )
        elif choice == "3":
            run_command(
                "python -m pytest books/tests/ -v", "Run Books App Tests"
            )
        elif choice == "4":
            run_command(
                "python -m pytest books/tests/ --cov=books "
                "--cov-report=term-missing --cov-report=html",
                "Run Books App Tests with Coverage",
            )
        elif choice == "5":
            run_command(
                "python -m pytest accounts/tests/ -v",
                "Run Accounts App Tests",
            )
        elif choice == "6":
            test_file = input(
                "Enter test file path (e.g., books/tests/test_views_reviews.py): "
            ).strip()
            if test_file:
                run_command(
                    f"python -m pytest {test_file} -v",
                    f"Run {test_file}",
                )
            else:
                print("No file specified.")
        # Integration & Debug Tests
        elif choice == "7":
            run_command(
                "python tests/test_api_integration.py",
                "API Integration Test",
            )
        elif choice == "8":
            run_command(
                "python tests/test_auth_debug.py",
                "Authentication Debug Test",
            )
        elif choice == "9":
            run_command(
                "python tests/test_server.py test",
                "Server Test (Django Client)",
            )
        # Django Management
        elif choice == "10":
            run_command(
                "python tests/test_server.py urls", "Show Available URLs"
            )
        elif choice == "11":
            run_command("python manage.py check", "Django System Check")
        elif choice == "12":
            run_command(
                "python manage.py makemigrations && python manage.py migrate",
                "Database Migrations",
            )
        elif choice == "13":
            run_command("python manage.py createsuperuser", "Create Superuser")
        elif choice == "14":
            print("\nStarting development server...")
            print("Server will be available at: http://127.0.0.1:8000/")
            print("Admin interface: http://127.0.0.1:8000/admin/")
            print("Press Ctrl+C to stop the server")
            run_command("python manage.py runserver", "Development Server")
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
