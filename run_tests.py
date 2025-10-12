#!/usr/bin/env python3
"""
COMP5241 Group 10 - API Test Runner
Run with: uv run python run_tests.py [option]

Options:
  genai       - Run GenAI API tests only
  all         - Run all API tests
  pytest      - Run pytest tests
  coverage    - Run with coverage report
"""
import sys
import subprocess
import requests
from colorama import init, Fore, Style

init(autoreset=True)

def print_error(msg):
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")

def print_success(msg):
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def print_info(msg):
    print(f"{Fore.CYAN}ℹ {msg}{Style.RESET_ALL}")

def check_server():
    """Check if Flask server is running"""
    try:
        response = requests.get("http://localhost:5001/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def run_genai_tests():
    """Run GenAI API tests"""
    print(f"\n{Fore.YELLOW}Running GenAI API Tests...{Style.RESET_ALL}\n")
    result = subprocess.run([sys.executable, "test_genai_simple.py"])
    return result.returncode

def run_all_tests():
    """Run all API tests"""
    print(f"\n{Fore.YELLOW}Running All API Tests...{Style.RESET_ALL}\n")
    result = subprocess.run([sys.executable, "test_all_apis.py"])
    return result.returncode

def run_pytest():
    """Run pytest tests"""
    print(f"\n{Fore.YELLOW}Running Pytest Tests...{Style.RESET_ALL}\n")
    result = subprocess.run([
        "pytest", 
        "backend/tests/test_genai_api.py", 
        "-v", 
        "--tb=short"
    ])
    return result.returncode

def run_pytest_coverage():
    """Run pytest with coverage"""
    print(f"\n{Fore.YELLOW}Running Pytest with Coverage...{Style.RESET_ALL}\n")
    result = subprocess.run([
        "pytest", 
        "backend/tests/test_genai_api.py", 
        "-v", 
        "--cov=backend/app/modules/genai",
        "--cov-report=term-missing",
        "--cov-report=html"
    ])
    if result.returncode == 0:
        print_info("\nCoverage report saved to: htmlcov/index.html")
    return result.returncode

def show_menu():
    """Show interactive menu"""
    print(f"{Fore.CYAN}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       COMP5241 Group 10 - API Test Runner                 ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}\n")
    
    print("Choose test option:")
    print(f"  {Fore.GREEN}1{Style.RESET_ALL}) GenAI API tests (simple)")
    print(f"  {Fore.GREEN}2{Style.RESET_ALL}) All API tests")
    print(f"  {Fore.GREEN}3{Style.RESET_ALL}) Pytest (detailed)")
    print(f"  {Fore.GREEN}4{Style.RESET_ALL}) Pytest with coverage")
    print(f"  {Fore.GREEN}q{Style.RESET_ALL}) Quit")
    print()
    
    choice = input("Enter choice [1-4, q]: ").strip().lower()
    return choice

def main():
    # Check if server is running
    if not check_server():
        print_error("Flask server is not running on port 5001")
        print_info("Start it with: uv run python start_system.py")
        sys.exit(1)
    
    print_success("Server is running\n")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
        
        if option == "genai":
            return run_genai_tests()
        elif option == "all":
            return run_all_tests()
        elif option == "pytest":
            return run_pytest()
        elif option == "coverage":
            return run_pytest_coverage()
        else:
            print_error(f"Unknown option: {option}")
            print_info("Valid options: genai, all, pytest, coverage")
            return 1
    
    # Interactive mode
    while True:
        choice = show_menu()
        
        if choice == "1":
            run_genai_tests()
        elif choice == "2":
            run_all_tests()
        elif choice == "3":
            run_pytest()
        elif choice == "4":
            run_pytest_coverage()
        elif choice == "q":
            print_info("Goodbye!")
            break
        else:
            print_error("Invalid choice. Please try again.")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        sys.exit(main() if len(sys.argv) > 1 else main() or 0)
    except KeyboardInterrupt:
        print_info("\n\nTests interrupted by user")
        sys.exit(1)

