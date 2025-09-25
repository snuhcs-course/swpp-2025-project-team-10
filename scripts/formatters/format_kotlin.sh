#!/bin/bash

# Kotlin Code Formatter Script
# This script formats Kotlin code using ktlint and runs detekt for static analysis
#
# Usage:
#   ./scripts/formatters/format_kotlin.sh [--check] [--diff] [paths...]
#
# Arguments:
#   --check: Don't write back modified files, just return status
#   --diff: Show diffs instead of rewriting files  
#   paths: Specific paths to format (default: frontend/src)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
CHECK_MODE=false
SHOW_DIFF=false
PATHS=("frontend/src")
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Parse command line arguments
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
            echo "Usage: $0 [--check] [--diff] [paths...]"
            echo ""
            echo "Options:"
            echo "  --check    Don't write back modified files, just return status"
            echo "  --diff     Show diffs instead of rewriting files"
            echo "  --help     Show this help message"
            echo ""
            echo "Default paths: frontend/src"
            exit 0
            ;;
        *)
            PATHS=("$@")
            break
            ;;
    esac
done

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to download ktlint if not present
ensure_ktlint() {
    local ktlint_version="0.50.0"
    local ktlint_jar="$PROJECT_ROOT/tools/linting/ktlint-${ktlint_version}.jar"
    
    if [[ ! -f "$ktlint_jar" ]]; then
        print_status $YELLOW "Downloading ktlint ${ktlint_version}..."
        mkdir -p "$PROJECT_ROOT/tools/linting"
        curl -sSLO "https://github.com/pinterest/ktlint/releases/download/${ktlint_version}/ktlint" \
            && chmod a+x ktlint \
            && mv ktlint "$PROJECT_ROOT/tools/linting/ktlint"
    fi
    
    KTLINT_CMD="$PROJECT_ROOT/tools/linting/ktlint"
}

# Function to download detekt if not present
ensure_detekt() {
    local detekt_version="1.23.1"
    local detekt_jar="$PROJECT_ROOT/tools/linting/detekt-cli-${detekt_version}.jar"
    
    if [[ ! -f "$detekt_jar" ]]; then
        print_status $YELLOW "Downloading detekt ${detekt_version}..."
        mkdir -p "$PROJECT_ROOT/tools/linting"
        curl -sSL "https://github.com/detekt/detekt/releases/download/v${detekt_version}/detekt-cli-${detekt_version}.jar" \
            -o "$detekt_jar"
    fi
    
    DETEKT_CMD="java -jar $detekt_jar"
}

# Function to run ktlint formatting
run_ktlint() {
    local paths=("$@")
    local existing_paths=()
    
    # Filter existing paths
    for path in "${paths[@]}"; do
        if [[ -d "$PROJECT_ROOT/$path" ]]; then
            existing_paths+=("$path")
        else
            print_status $YELLOW "Warning: Path $path does not exist, skipping..."
        fi
    done
    
    if [[ ${#existing_paths[@]} -eq 0 ]]; then
        print_status $RED "No valid paths found to format"
        return 1
    fi
    
    print_status $BLUE "Running ktlint on: ${existing_paths[*]}"
    
    cd "$PROJECT_ROOT"
    
    local ktlint_args=()
    
    if [[ "$CHECK_MODE" == "true" ]]; then
        ktlint_args+=("--reporter=plain")
    else
        ktlint_args+=("-F")
    fi
    
    # Add paths with Kotlin file patterns
    for path in "${existing_paths[@]}"; do
        ktlint_args+=("$path/**/*.kt" "$path/**/*.kts")
    done
    
    if $KTLINT_CMD "${ktlint_args[@]}"; then
        if [[ "$CHECK_MODE" == "true" ]]; then
            print_status $GREEN "✅ Ktlint formatting check passed"
        else
            print_status $GREEN "✅ Ktlint formatting completed"
        fi
        return 0
    else
        if [[ "$CHECK_MODE" == "true" ]]; then
            print_status $RED "❌ Ktlint formatting check failed"
        else
            print_status $RED "❌ Ktlint formatting failed"
        fi
        return 1
    fi
}

# Function to run detekt static analysis
run_detekt() {
    local paths=("$@")
    local existing_paths=()
    
    # Filter existing paths
    for path in "${paths[@]}"; do
        if [[ -d "$PROJECT_ROOT/$path" ]]; then
            existing_paths+=("$path")
        fi
    done
    
    if [[ ${#existing_paths[@]} -eq 0 ]]; then
        return 0
    fi
    
    print_status $BLUE "Running detekt static analysis..."
    
    cd "$PROJECT_ROOT"
    
    local detekt_args=("--input" "$(IFS=,; echo "${existing_paths[*]}")")
    detekt_args+=("--report" "txt:build/reports/detekt.txt")
    detekt_args+=("--report" "html:build/reports/detekt.html")
    
    # Create reports directory
    mkdir -p build/reports
    
    if $DETEKT_CMD "${detekt_args[@]}"; then
        print_status $GREEN "✅ Detekt static analysis passed"
        return 0
    else
        print_status $RED "❌ Detekt static analysis failed"
        print_status $YELLOW "Check build/reports/detekt.html for detailed report"
        return 1
    fi
}

# Main execution
main() {
    print_status $BLUE "Kotlin Code Formatter and Analyzer"
    print_status $BLUE "=================================="
    
    # Ensure tools are available
    ensure_ktlint
    ensure_detekt
    
    local success=true
    
    # Run ktlint
    if ! run_ktlint "${PATHS[@]}"; then
        success=false
    fi
    
    # Run detekt (only if not in diff mode)
    if [[ "$SHOW_DIFF" != "true" ]]; then
        if ! run_detekt "${PATHS[@]}"; then
            success=false
        fi
    fi
    
    print_status $BLUE "=================================="
    
    if [[ "$success" == "true" ]]; then
        print_status $GREEN "🎉 All Kotlin formatting and checks passed!"
        exit 0
    else
        print_status $RED "💥 Some Kotlin formatting or checks failed!"
        exit 1
    fi
}

# Run main function
main "$@"
