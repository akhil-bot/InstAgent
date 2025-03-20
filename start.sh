#!/bin/bash

echo "===================================================================="
echo "🚀 Starting InstAgent Docker container..."
echo "===================================================================="

# Start Streamlit in the background
streamlit run main.py --server.port=8502 --server.address=0.0.0.0 &
STREAMLIT_PID=$!

# Wait for Streamlit to initialize
sleep 3

echo ""
echo "===================================================================="
echo "✅ InstAgent is now running in Docker!"
echo "🌐 Access the application at: http://localhost:8502"
echo "📌 Press Ctrl+C to stop the container"
echo "===================================================================="
echo ""

# Keep the container running until Streamlit process exits
wait $STREAMLIT_PID 