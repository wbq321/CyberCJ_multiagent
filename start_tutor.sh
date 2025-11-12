#!/bin/bash
# start_tutor.bat - Startup script for Windows

echo "Starting CyberJustice Improved Tutor..."
echo "Make sure your conda environment is activated!"
echo ""

# Check if required packages are available
python -c "
try:
    import flask
    import langchain_groq
    import faiss
    print('✅ All required packages found')
except ImportError as e:
    print('❌ Missing package:', e)
    print('Please activate your conda environment first')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Starting server..."
    echo "📱 Open your browser to: http://localhost:5000"
    echo "🛑 Press Ctrl+C to stop"
    echo ""
    python app.py
else
    echo ""
    echo "💡 Please activate your conda environment first, then run this script again"
fi