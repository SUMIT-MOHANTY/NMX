
echo "===== Verifying JWT Setup ====="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo " Python is not installed"
    exit 1
fi

# Check if necessary packages are installed
echo "Checking installed packages..."
pip list | grep -E 'fastapi|uvicorn|python-jose|passlib'

# Check if files exist
echo -e "\nChecking required files..."
for file in \
    "/workspace/backend/app/core/security.py" \
    "/workspace/backend/app/core/config.py" \
    "/workspace/backend/app/api/auth.py" \
    "/workspace/backend/main.py"
do
    if [ -f "$file" ]; then
        echo " $file exists"
    else
        echo " $file is missing"
    fi
done

echo -e "\nAll verification checks complete!"
echo "To run the API server: cd /workspace/backend && python3 main.py"
echo "To test the JWT flow: python3 /workspace/test_jwt.py"
echo "===== End of Verification ====="
