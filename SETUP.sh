#!/bin/bash
# Quick Setup Script for Money Muling Detection Engine

echo "========================================"
echo "Money Muling Detection Engine - Setup"
echo "RIFT 2026 Hackathon Challenge"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}[1/4] Installing Backend Dependencies...${NC}"
cd backend
echo "Installing Python packages..."
pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Backend dependencies installed${NC}"
else
  echo -e "${YELLOW}✗ Failed to install backend dependencies${NC}"
  exit 1
fi

echo -e "\n${BLUE}[2/4] Generating Sample Test Data...${NC}"
python sample_csv_generator.py

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Sample data generated (sample_transactions.csv)${NC}"
else
  echo -e "${YELLOW}✗ Failed to generate sample data${NC}"
fi

cd ..

echo -e "\n${BLUE}[3/4] Installing Frontend Dependencies...${NC}"
cd frontend
npm install --quiet

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
  echo -e "${YELLOW}✗ Failed to install frontend dependencies${NC}"
  exit 1
fi

cd ..

echo -e "\n${BLUE}[4/4] Verification...${NC}"

# Check Python
if command -v python &> /dev/null; then
  PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
  echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"
else
  echo -e "${YELLOW}✗ Python not found${NC}"
fi

# Check Node
if command -v node &> /dev/null; then
  NODE_VERSION=$(node --version)
  echo -e "${GREEN}✓ Node ${NODE_VERSION}${NC}"
else
  echo -e "${YELLOW}✗ Node not found${NC}"
fi

# Check npm
if command -v npm &> /dev/null; then
  NPM_VERSION=$(npm --version)
  echo -e "${GREEN}✓ npm ${NPM_VERSION}${NC}"
else
  echo -e "${YELLOW}✗ npm not found${NC}"
fi

echo -e "\n${GREEN}========================================"
echo "Setup Complete!"
echo "========================================${NC}"

echo -e "\n${BLUE}Next Steps:${NC}"
echo "1. Start Backend:"
echo "   cd backend && python app.py"
echo ""
echo "2. Start Frontend (in another terminal):"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Open http://localhost:5173 in your browser"
echo ""
echo "4. Upload sample_transactions.csv from backend/ folder"
echo ""
echo -e "${YELLOW}Documentation: See PROJECT_README.md for detailed info${NC}"
