
echo "Checking for venv..."
if [ ! -d "venv" ]; then
    echo "Creating venv..."
    virtualenv venv
fi

echo "Checking if venv is activated..."
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating venv..."
    source venv/bin/activate
fi

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running job..."

python3 main.py

echo "Done."