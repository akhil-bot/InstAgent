# 🤖 LinkedIn Post Agent

This README provides instructions on how to set up and run the generated agent system.

## 📋 Prerequisites

Ensure you have the following installed on your system:

- Python 3.10 or higher
- pip (Python package manager)


## 🚀 Running the Agent System


### Option 1: Local Installation

1. **Clone the repository** (if applicable) or download the code files.

2. **Navigate to the project directory**:
   ```bash
   cd path/to/your/project
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up Composio API Key**

   To use Composio's features, you'll need to set up your Composio API key. Follow the instructions provided in the <a href="https://docs.composio.dev/getting-started/quickstart" target="_blank">Composio Quickstart Guide</a> to obtain and configure your API key.

6. **Run the agent system**:
   ```bash
   python main.py
   ```

### Option 2: Docker Installation

1. **Create a Dockerfile** in the project directory:
   ```bash
   cat > Dockerfile << 'EOL'
   FROM python:3.10-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8502

   CMD ["python", "main.py"]
   EOL
   ```

2. **Build the Docker image**:
   ```bash
   docker build -t linkedin-post-agent .
   ```

3. **Run the Docker container**:
   ```bash
   docker run -e OPENAI_API_KEY=your_api_key -e COMPOSIO_API_KEY=your_composio_key linkedin-post-agent
   ```

## 🛠️ Customization

- Modify the `main.py` file to adjust the agent's behavior or integrate additional tools.
- Update the `.env` file to change configurations or API keys.

## 📞 Support

For any issues or questions, please contact the project maintainer.

---

*This agent system was generated using [InstAgent](https://github.com/akhil-bot/InstAgent), a tool for creating sophisticated multi-agent systems from natural language descriptions.*
