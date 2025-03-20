FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code first
COPY . .

# Make the start script executable (fixing permission issues)
RUN chmod +x start.sh

# Expose the Streamlit port
EXPOSE 8502

# Set environment variable to make Streamlit run in headless mode
ENV STREAMLIT_SERVER_HEADLESS=true

# Command to run the application using the startup script
# Use the shell form to ensure proper execution
CMD bash ./start.sh


