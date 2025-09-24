#!/bin/bash

# Universal Code Formatter Script
# This script runs all code formatters for the project
#
# Usage:
#   ./scripts/formatters/format_all.sh [--check] [--diff]
#
# Arguments:
#   --check: Don't write back modified files, just return status
#   --diff: Show diffs instead of rewriting files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Parse command line arguments
CHECK_MODE=false
SHOW_DIFF=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --check)
            CHECK_MODE=true
            shift
            ;;
        --diff)
            SHOW_DIFF=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--check] [--diff]"
            echo ""
            echo "Options:"
            echo "  --check    Don't write back modified files, just return status"
            echo "  --diff     Show diffs instead of rewriting files"
            echo "  --help     Show this help message"
            echo ""
            echo "This script runs formatters for Python and Kotlin code."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to run formatter with proper arguments
run_formatter() {
    local formatter_name=$1
    local formatter_script=$2
    shift 2
    local args=("$@")
    
    print_status $BLUE "Running $formatter_name formatter..."
    print_status $BLUE "$(printf '=%.0s' {1..50})"
    
    if [[ "$CHECK_MODE" == "true" ]]; then
        args+=("--check")
    fi
    
    if [[ "$SHOW_DIFF" == "true" ]]; then
        args+=("--diff")
    fi
    
    if "$formatter_script" "${args[@]}"; then
        print_status $GREEN "✅ $formatter_name formatting completed successfully"
        return 0
    else
        print_status $RED "❌ $formatter_name formatting failed"
        return 1
    fi
}

# Main execution
main() {
    print_status $BLUE "Universal Code Formatter"
    print_status $BLUE "========================"
    
    cd "$PROJECT_ROOT"
    
    local overall_success=true
    
    # Run Python formatter
    if [[ -d "backend" ]] || [[ -d "ai-model" ]]; then
        if ! run_formatter "Python" "python" "$SCRIPT_DIR/format_python.py"; then
            overall_success=false
        fi
    else
        print_status $YELLOW "No Python directories found, skipping Python formatting"
    fi
    
    echo ""
    
    # Run Kotlin formatter
    if [[ -d "frontend" ]]; then
        if ! run_formatter "Kotlin" "$SCRIPT_DIR/format_kotlin.sh"; then
            overall_success=false
        fi
    else
        print_status $YELLOW "No Kotlin directories found, skipping Kotlin formatting"
    fi
    
    echo ""
    print_status $BLUE "========================"
    
    if [[ "$overall_success" == "true" ]]; then
        print_status $GREEN "🎉 All code formatting completed successfully!"
        exit 0
    else
        print_status $RED "💥 Some code formatting failed!"
        exit 1
    fi
}

# Run main function
main "$@"
