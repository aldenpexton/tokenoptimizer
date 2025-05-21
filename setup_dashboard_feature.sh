#!/bin/bash

# TokenOptimizer Dashboard Feature Setup Script
#
# This script:
# 1. Creates a new feature branch
# 2. Sets up necessary directories
# 3. Copies requirements and planning documents
# 4. Sets up the dummy data generation script

set -e  # Exit on any error

# Colors for pretty output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}TokenOptimizer Dashboard Feature Setup${NC}"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install git and try again."
    exit 1
fi

# Check if we're in the tokenoptimizer directory
if [[ ! -d "./backend" || ! -d "./frontend" ]]; then
    echo "Please run this script from the root of the tokenoptimizer project directory."
    exit 1
fi

# Create and switch to feature branch
echo -e "${YELLOW}Creating feature branch...${NC}"
git checkout develop || git checkout -b develop
git checkout -b feature/dashboard-foundation

# Create directories if they don't exist
echo -e "${YELLOW}Setting up directories...${NC}"
mkdir -p scripts
mkdir -p dummy_data
mkdir -p backend/services
mkdir -p frontend/src/hooks

# Copy requirement documents
echo -e "${YELLOW}Copying requirement documents...${NC}"
cp REQUIREMENTS.md .
cp DEVELOPMENT_PLAN.md .
cp README_DASHBOARD.md README_DASHBOARD.md

# Make dummy data generator script executable
echo -e "${YELLOW}Setting up dummy data generator...${NC}"
chmod +x scripts/generate_dummy_data.py

# Install required packages if not already installed
echo -e "${YELLOW}Checking dependencies...${NC}"

# Python dependencies
if ! pip list | grep -q "langchain"; then
    echo "Installing Python dependencies..."
    pip install langchain langchain-openai
fi

# Generate dummy data
echo -e "${YELLOW}Generating dummy data for development...${NC}"
python scripts/generate_dummy_data.py --days 30 --entries-per-day 25

# Summary
echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review REQUIREMENTS.md and DEVELOPMENT_PLAN.md"
echo "2. Start by implementing the dashboard_service.py in backend/services"
echo "3. Add the /api/dashboard endpoint in backend/routes/analytics_routes.py"
echo "4. Create the useDashboard hook in frontend/src/hooks"
echo ""
echo "Happy coding!" 