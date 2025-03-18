import sys
import os
sys.path.append(os.getcwd())
import streamlit as st
import json
import pyperclip
import os
import re
import traceback
import time
import zipfile
import io
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from Prompts import Prompts
from graphviz import Digraph
from PIL import Image
from Tools import Tools

# Set page configuration
st.set_page_config(
    page_title="InstAgent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
session_defaults = {
    'openai_api_key': '',
    'agent_output': None,
    'events': [],
    'running': False,
    'current_agent': None,
    'team_creator_output': None,
    'tool_picker_output': None,
    'agent_code_output': None,
    'agent_name': None
}

for key, value in session_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Update the CSS to use Streamlit's default dark theme
st.markdown("""
    <style>
    /* Keep Streamlit's default dark theme */
    
    /* Layout improvements without changing default colors */
    .custom-card {
        background: rgba(49, 51, 63, 0.7);
        border: 1px solid rgba(250, 250, 250, 0.2);
        border-radius: 8px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Code Blocks */
    .code-block {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(49, 51, 63, 0.7);
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid rgba(250, 250, 250, 0.2);
        overflow-x: auto;
    }
    
    .code-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    /* Error Handling */
    .error-box {
        background: rgba(49, 51, 63, 0.7);
        border: 1px solid rgba(255, 75, 75, 0.5);
        border-radius: 4px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Larger Tabs with default styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        padding: 10px 16px;
        font-size: 0.95em;
    }
    
    /* Tab content area */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 15px;
        min-height: 300px;
    }
    
    /* Spinner */
    .stSpinner {
        display: inline-block;
        width: 36px;
        height: 36px;
        border: 3px solid rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        border-top-color: #ffffff;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* Stepper Styles */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .stepper-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }
    .stepper-item:not(:last-child)::after {
        content: '';
        position: absolute;
        top: 50%;
        right: -50%;
        width: 100%;
        height: 2px;
        background-color: #ccc;
        z-index: -1;
    }
    .stepper-active .stepper-icon {
        background-color: #198754;
        color: white;
    }
    .stepper-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #ccc;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Load the logo from the assets folder
# logo_path = "assets/InstAgent_logo.png"
# logo = Image.open(logo_path)

# # Display the logo at the top of the app
# st.image(logo, width=100)  # Adjust width as needed

# def copy_to_clipboard(text):
#     try:
#         pyperclip.copy(text)
#         st.toast("Copied to clipboard!", icon="✅")
#     except Exception as e:
#         st.error(f"Failed to copy: {str(e)}")

def copy_to_clipboard(text):
    """Helper function to copy text to clipboard"""
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        st.error(f"Failed to copy: {str(e)}")
        return False

def set_openai_api_key(api_key: str):
    st.session_state.openai_api_key = api_key
    os.environ['OPENAI_API_KEY'] = api_key

def extract_code_blocks(text):
    if not text:
        return []
    pattern = r'```python(.*?)```'
    code_blocks = re.findall(pattern, text, re.DOTALL)
    if not code_blocks:
        pattern = r'```(.*?)```'
        code_blocks = re.findall(pattern, text, re.DOTALL)
    return [block.strip() for block in code_blocks]

def format_json(json_str):
    try:
        data = json.loads(json_str)
        return json.dumps(data, indent=2)
    except:
        return json_str

def create_zip_file(code, agent_name):
    """Create a zip file containing the agent code, requirements.txt, and README.md."""
    # Create a BytesIO object to store the ZIP file
    zip_buffer = io.BytesIO()
    
    # Define the README.md content
    readme_content = f'''# 🤖 {agent_name}

This README provides instructions on how to set up and run the generated agent system.

## 📋 Prerequisites

Ensure you have the following installed on your system:

- Python 3.10 or higher
- pip (Python package manager)

## 📦 Installation

1. **Clone the repository** (if applicable) or download the code files.

2. **Navigate to the project directory**:
   ```bash
   cd path/to/your/project
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set up Composio API Key**

   To use Composio's features, you'll need to set up your Composio API key. Follow the instructions provided in the <a href="https://docs.composio.dev/getting-started/quickstart" target="_blank">Composio Quickstart Guide</a> to obtain and configure your API key.

## 🚀 Running the Agent System

1. **Set up environment variables** (if required):
   - Create a `.env` file in the project directory.
   - Add your API keys and other necessary configurations.

2. **Execute the main script**:
   ```bash
   python main.py
   ```

## 🛠️ Customization

- Modify the `main.py` file to adjust the agent's behavior or integrate additional tools.
- Update the `.env` file to change configurations or API keys.

## 📞 Support

For any issues or questions, please contact the project maintainer.

---

*This agent system was generated using [InstAgent](https://github.com/akhil-bot/InstAgent), a tool for creating sophisticated multi-agent systems from natural language descriptions.*
'''

    # Create a ZIP file
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main.py with the generated code
        zipf.writestr('main.py', code)
        
        # Add requirements.txt
        # Read the content of the requirements.txt file
        try:
            with open('requirements.txt', 'r') as req_file:
                requirements_content = req_file.read()
            zipf.writestr('requirements.txt', requirements_content)
        except FileNotFoundError:
            # If requirements.txt is not found, add a default one
            default_requirements = """
                # Core dependencies
                langchain-core==0.3.40
                langchain-openai==0.2.14
                langgraph==0.2.76
                langchain-experimental==0.3.4
                pyperclip==1.8.2


                # Composio integration
                composio_langchain==0.7.5
                composio_langgraph==0.7.5

                # OpenAI
                openai==1.64.0

                # Utility packages
                python-dotenv==1.0.0
                pydantic==2.10.6
                """
            zipf.writestr('requirements.txt', default_requirements)
        
        # Add README.md
        zipf.writestr('README.md', readme_content)
    
    # Reset the buffer position to the beginning
    zip_buffer.seek(0)
    return zip_buffer

def display_workflow_progress():
    """Display a compact, visually appealing progress indicator that optimizes screen space"""
    
    # Define agent steps and their statuses
    agents = [
        {"name": "Team Creator", "id": "team_creator", "icon": "👥", "output": st.session_state.team_creator_output},
        {"name": "Tool Picker", "id": "tool_picker", "icon": "🛠️", "output": st.session_state.tool_picker_output},
        {"name": "Code Generator", "id": "agent_code_generation", "icon": "💻", "output": st.session_state.agent_code_output}
    ]
    
    # Calculate completed steps for overall progress
    completed_steps = sum(1 for agent in agents if agent["output"])
    total_steps = len(agents)
    overall_progress = completed_steps / total_steps
    
    # Create a compact header with overall progress - using consistent heading style
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="flex-grow: 1; font-size: 16px; text-align: right; color: #{'198754' if overall_progress == 1 else '0d6efd'};">
                {int(overall_progress * 100)}% Complete
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Progress bar styling - slimmer and more integrated
    progress_html = f"""
    <div style="height: 8px; background-color: #{'198754' if overall_progress == 1 else '0d6efd'}; 
                border-radius: 4px; margin: 5px 0 20px 0; width: {max(5, int(overall_progress * 100))}%"></div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)
    
    # Now create a compact step indicator that takes less vertical space
    step_cols = st.columns(3)
    
    for i, (col, agent) in enumerate(zip(step_cols, agents)):
        with col:
            # Determine status styling
            if agent["output"]:
                status = "✓ Completed"
                color = "#198754"  # green
                progress = 100
            elif st.session_state.current_agent == agent["id"]:
                status = "⟳ Running"
                color = "#0d6efd"  # blue
                progress = 50
            else:
                status = "Pending"
                color = "#6c757d"  # gray
                progress = 0
            
            # Create a compact card-like display with consistent font sizing
            st.markdown(
                f"""
                <div style="padding: 10px; border-radius: 6px; border: 1px solid {color}; margin-bottom: 10px;">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div style="width: 28px; height: 28px; background-color: {color}; color: white; 
                                border-radius: 50%; text-align: center; line-height: 28px; margin-right: 10px; font-size: 16px;">
                            {i+1}
                        </div>
                        <div style="font-weight: 600; font-size: 16px;">{agent["name"]}</div>
                    </div>
                    <div style="font-size: 14px; color: {color}; margin-bottom: 8px;">{status}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Add a slightly thicker progress bar to match tab styling
            st.progress(progress/100)

def run_agent_creator(task, model="gpt-4o", temperature=0.0, workflow_placeholder=None):
    prompts_obj = Prompts()
    llm = ChatOpenAI(model=model, temperature=temperature)

    def team_creation_node(state: MessagesState) -> Command:
        print("Executing team_creation_node")
        st.session_state.current_agent = "team_creator"
        if workflow_placeholder:
            with workflow_placeholder.container():
                display_workflow_progress()
                display_agent_workflow()
                
        team_creation_prompt = prompts_obj.team_creation_prompt.replace("{input}", task)
        # print("team_creation_prompt****", team_creation_prompt)
        team_creation_agent = create_react_agent(llm, [], prompt=team_creation_prompt)
        result = team_creation_agent.invoke(state)
        team_creation_output = result["messages"][-1].content
        
        st.session_state.team_creator_output = team_creation_output
        
        # Extract team name and save it to session state
        try:
            team_data = json.loads(team_creation_output.replace('```json', '').replace('```', ''))
            if "name" in team_data:
                st.session_state.agent_name = team_data["name"]
        except:
            pass
        
        result["messages"][-1] = HumanMessage(content=team_creation_output, name="team_creator")
        return Command(update={"messages": result["messages"]}, goto="tool_picker")

    def tool_picker_node(state: MessagesState) -> Command:
        print("Executing tool_picker_node")
        st.session_state.current_agent = "tool_picker"
        if workflow_placeholder:
            with workflow_placeholder.container():
                display_workflow_progress()
                display_agent_workflow()
        available_tools = Tools().get_available_tools()
        team_creation_output = state["messages"][-1].content
        tool_picker_prompt = prompts_obj.tool_picker_prompt.replace("{input}", team_creation_output).replace("{available_tools}", str(available_tools))
        # print("tool_picker_prompt****", tool_picker_prompt)
        tool_picker_agent = create_react_agent(llm, [], prompt=tool_picker_prompt)
        result = tool_picker_agent.invoke(state)
        tool_picker_output = result["messages"][-1].content
        
        st.session_state.tool_picker_output = tool_picker_output
        
        result["messages"][-1] = HumanMessage(content=tool_picker_output, name="tool_picker")
        return Command(update={"messages": result["messages"]}, goto="agent_code_generation")

    def agent_code_generation_node(state: MessagesState) -> Command:
        print("Executing agent_code_generation_node")
        st.session_state.current_agent = "agent_code_generation"
        if workflow_placeholder:
            with workflow_placeholder.container():
                display_workflow_progress()
                display_agent_workflow()
                
        tool_picker_output = state["messages"][-1].content
        agent_code_generation_prompt = prompts_obj.agent_code_generation_prompt.replace("{input}", tool_picker_output)
        # print("agent_code_generation_prompt****", agent_code_generation_prompt)
        agent_code_generation_agent = create_react_agent(llm, [], prompt=agent_code_generation_prompt)
        result = agent_code_generation_agent.invoke(state)
        agent_code_generation_output = result["messages"][-1].content
        
        st.session_state.agent_code_output = agent_code_generation_output
        
        result["messages"][-1] = HumanMessage(content=agent_code_generation_output, name="agent_code_generation")
        return Command(update={"messages": result["messages"]}, goto=END)

    workflow = StateGraph(MessagesState)
    workflow.add_node("team_creator", team_creation_node)
    workflow.add_node("tool_picker", tool_picker_node)
    workflow.add_node("agent_code_generation", agent_code_generation_node)

    workflow.add_edge(START, "team_creator")
    workflow.add_edge("team_creator", "tool_picker")
    workflow.add_edge("tool_picker", "agent_code_generation")
    workflow.add_edge("agent_code_generation", END)

    graph = workflow.compile()

    events = graph.stream(
        {
            "task": task,
            "messages": [("user", f"{task}")]
        },
        {"recursion_limit": 250},
    )
    
    st.session_state.events = []
    for event in events:
        st.session_state.events.append(event)
        time.sleep(0.1)
    
    st.session_state.current_agent = None
    if workflow_placeholder:
        with workflow_placeholder.container():
            display_workflow_progress()
            display_agent_workflow()
    
    return st.session_state.events

def display_agent_workflow():
    """Display completed agent outputs in a space-efficient tabbed interface"""
    # Only display outputs if any agents have completed
    if any([st.session_state.team_creator_output,
            st.session_state.tool_picker_output,
            st.session_state.agent_code_output]):
        
        # Create a more subtle separator that creates a smooth transition
        st.markdown("<div style='margin: 25px 0 20px 0; border-top: 1px solid rgba(49, 51, 63, 0.2);'></div>", unsafe_allow_html=True)
        
        # Create more visually consistent tabs with larger, more prominent titles
        st.markdown("""
            <style>
            /* Increase specificity and force font size for tab titles */
            .stTabs [data-baseweb="tab"] {
                font-size: 20px !important;
                padding: 15px 20px !important;
                font-weight: 600 !important;
                height: auto !important;
                background-color: transparent !important;
            }
            
            /* Make active tab more prominent */
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                font-weight: 600 !important;
                color: #0d6efd !important;
                border-bottom: 3px solid #0d6efd !important;
            }
            
            /* Adjust tab list container for larger tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 15px !important;
                margin-bottom: 8px !important;
                padding-bottom: 0px !important;
                border-bottom: 1px solid rgba(49, 51, 63, 0.2) !important;
            }
            
            /* Ensure tab text is centered and properly sized */
            .stTabs [data-baseweb="tab"] > div {
                font-size: 20px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                min-height: 40px !important;
            }
            
            /* Adjust icons in tab titles */
            .stTabs [data-baseweb="tab"] span {
                font-size: 22px !important;
                margin-right: 8px !important;
            }
            
            /* Rest of your existing styles... */
            </style>
        """, unsafe_allow_html=True)
        
        # Create tabs with more descriptive titles
        tab_titles = []
        if st.session_state.team_creator_output:
            tab_titles.append("👥 Team Configuration")
        if st.session_state.tool_picker_output:
            tab_titles.append("🛠️ Tool Selection")
        if st.session_state.agent_code_output:
            tab_titles.append("💻 Generated Code")
        
        tabs = st.tabs(tab_titles)
        
        # Display content in tabs that exist
        tab_index = 0
        
        if st.session_state.team_creator_output:
            with tabs[tab_index]:
                display_team_output(st.session_state.team_creator_output)
            tab_index += 1
        
        if st.session_state.tool_picker_output:
            with tabs[tab_index]:
                display_tool_output(st.session_state.tool_picker_output)
            tab_index += 1
        
        if st.session_state.agent_code_output:
            with tabs[tab_index]:
                # Add a more prominent header for the generated code
                st.markdown("<h3>📝 Generated Agent Code</h3>", unsafe_allow_html=True)
                display_code_output(st.session_state.agent_code_output, key_suffix="main_tab")

def display_team_output(output):
    try:
        output = output.replace('```json', '').replace('```', '')
        team_data = json.loads(output)
        
        # Display team name at the top
        if "name" in team_data:
            st.markdown(f"### 🚀 {team_data['name']}")
        
        # Create tabs for formatted view and raw JSON
        view_tab1, view_tab2 = st.tabs(["Formatted View", "Raw JSON"])
        
        with view_tab1:
            st.markdown("### Team Members")
            if "team" in team_data:
                # Display team members
                for member in team_data["team"]:
                    with st.container():
                        st.markdown(f"""
                        <div class="custom-card">
                            <h4>{member.get('name', 'Team Member')}</h4>
                            <p><strong>Role:</strong> {member.get('role', 'N/A')}</p>
                            <p><strong>Goal:</strong> {member.get('goal', 'N/A')}</p>
                            <p><strong>Backstory:</strong> {member.get('backstory', 'N/A')}</p>
                            <p><strong>ID:</strong> {member.get('id', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Display connections as a flowchart
                if "connections" in team_data and team_data["connections"]:
                    st.markdown("### Workflow Connections")
                    
                    # Create a mapping of IDs to names for easier reference
                    id_to_name = {member['id']: member['name'] for member in team_data['team'] if 'id' in member and 'name' in member}
                    
                    # Create a Graphviz diagram
                    graph = Digraph('Workflow')
                    graph.attr('node', shape='box', style='filled', fontname='Arial', margin='0.2,0.1')
                    graph.attr('edge', fontname='Arial', color='#aaaaaa')
                    graph.attr(rankdir='LR')  # Left to right layout
                    graph.attr('graph', bgcolor='transparent')  # Transparent background
                    
                    # Add START and END nodes with special styling
                    graph.node('START', shape='oval', fillcolor='#2ecc71', fontcolor='#ffffff', style='filled')
                    graph.node('END', shape='oval', fillcolor='#e74c3c', fontcolor='#ffffff', style='filled')
                    
                    # Add team member nodes with better contrast for dark theme
                    for member in team_data["team"]:
                        member_id = member.get('id', '')
                        member_name = member.get('name', '')
                        member_role = member.get('role', '')
                        if member_id and member_name:
                            node_label = f"{member_name}\n({member_role})"
                            graph.node(member_id, label=node_label, fillcolor='#3498db', style='filled,rounded', fontcolor='#ffffff')
                    
                    # Add connections
                    for conn in team_data["connections"]:
                        from_id = conn.get("from", "")
                        to_id = conn.get("to", "")
                        if from_id and to_id:
                            graph.edge(from_id, to_id, color='#aaaaaa')
                    
                    # Display the graph
                    st.graphviz_chart(graph)
            else:
                st.markdown(f'<div class="code-block">{format_json(output)}</div>', unsafe_allow_html=True)
        
        with view_tab2:

            # Display raw JSON with copy button
            st.code(json.dumps(team_data, indent=2), language="json")
            
                
    except Exception as e:
        st.markdown(f'<div class="code-block">{output}</div>', unsafe_allow_html=True)
        st.error(f"Could not parse team data: {str(e)}")

def display_tool_output(output):
    try:
        output = output.replace('```json', '').replace('```', '')
        tools_data = json.loads(output)
        
        # Display team name at the top
        if "name" in tools_data:
            st.markdown(f"### 🚀 {tools_data['name']}")
        
        # Create tabs for formatted view and raw JSON
        view_tab1, view_tab2 = st.tabs(["Formatted View", "Raw JSON"])
        
        with view_tab1:
            if "team" in tools_data:
                cols = st.columns(2)
                for idx, member in enumerate(tools_data["team"]):
                    with cols[idx % 2]:
                        st.markdown(f"""
                        <div class="custom-card">
                            <h4>{member.get('name', 'Member')}</h4>
                            <p><strong>Role:</strong> {member.get('role', 'N/A')}</p>
                            <p><strong>Tools:</strong> {', '.join(member.get('tools', ['None']))}</p>
                            <p><strong>Prompt:</strong> {member.get('prompt', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="code-block">{format_json(output)}</div>', unsafe_allow_html=True)
        
        with view_tab2:
            # Display raw JSON with copy button
            st.code(json.dumps(tools_data, indent=2), language="json")
            # if st.button("📋 Copy JSON", key=f"copy_btn"):
            #     if copy_to_clipboard(json.dumps(tools_data, indent=2)):
            #         st.toast("Copied to clipboard!", icon="✅")
            #     else:
            #         st.error("Failed to copy to clipboard")
                
    except Exception as e:
        st.markdown(f'<div class="code-block">{output}</div>', unsafe_allow_html=True)
        st.error(f"Could not parse tools data: {str(e)}")

def display_code_output(output, key_suffix=""):
    code_blocks = extract_code_blocks(output)
    if code_blocks:
        with st.container():
            st.markdown("<h4>Generated Agent Code</h4>", unsafe_allow_html=True)
            
            # Extract filename from the code comment
            code = code_blocks[0]
            filename = "agent_code.py"  # default filename
            
            # Look for the filename in the code comments with updated pattern
            filename_match = re.search(r'# fileName: ([\w.]+\.py)', code)
            if filename_match:
                extracted_filename = filename_match.group(1).strip()
                if extracted_filename:
                    filename = extracted_filename  # No need to add .py as it's already in the filename
            
            # Format the code for display
            st.code(code, language="python")
            
            # Create columns for download buttons
            col1, col2, col3 = st.columns(3)
            
            # Add download button for Python file in the first column
            with col1:
                unique_key = f"download_code_{key_suffix}_{int(time.time() * 1000)}"
                st.download_button(
                    label="📥 Download Python File",
                    data=code,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True,
                    key=unique_key
                )
            
            # Add download button for ZIP file in the second column
            with col2:
                # Get the agent name for the zip file name
                agent_name = st.session_state.agent_name or "InstAgent"
                # Create sanitized filename
                zip_filename = f"{agent_name.replace(' ', '_')}.zip"
                
                # Create zip file
                zip_buffer = create_zip_file(code, agent_name)
                
                zip_key = f"download_zip_{key_suffix}_{int(time.time() * 1000)}"
                st.download_button(
                    label="📦 Download as Project",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip",
                    use_container_width=True,
                    key=zip_key
                )
            
            # # Add copy button with better feedback
            # with col3:
            #     copy_key = f"copy_code_{key_suffix}_{int(time.time() * 1000)}"
            #     copied = st.session_state.get(f"copied_{copy_key}", False)
                
            #     if not copied:
            #         if st.button("📋 Copy Code", key="copy_btn_2", use_container_width=True):
            #             try:
            #                 if copy_to_clipboard(code):
            #                     st.toast("Copied to clipboard!", icon="✅")
            #                 else:
            #                     st.error("Failed to copy to clipboard")
            #                 st.session_state[f"copied_{copy_key}"] = True
            #                 # st.experimental_rerun()
            #             except Exception as e:
            #                 st.error(f"Failed to copy: {str(e)}")
            #     else:
            #         # Show success message as a button with green color
            #         st.success("✅ Copied to clipboard!")
                    
            #         # Reset after 3 seconds
            #         time.sleep(0.1)
            #         st.session_state[f"copied_{copy_key}"] = False
    else:
        st.markdown(f'<div class="code-block">{output}</div>', unsafe_allow_html=True)

def main():
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        with st.expander("🔑 API Settings", expanded=True):
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.openai_api_key,
                help="Get your API key from platform.openai.com"
            )
            if api_key:
                set_openai_api_key(api_key)
        
        with st.expander("🧠 Model Settings", expanded=True):
            model = st.selectbox(
                "Model Version",
                ["gpt-4o", "gpt-4", "gpt-3.5-turbo"],
                index=0
            )
            
            temperature = st.slider(
                "Creativity Level",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.1
            )
        
        with st.expander("⚡ System Controls"):
            if st.button("🔄 Reset Workflow", use_container_width=True):
                for key in session_defaults:
                    if key != 'openai_api_key':
                        st.session_state[key] = session_defaults[key]
                st.rerun()

    # Create a row with two columns
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            """
            <div style="margin-bottom: 2rem;">
                <h1>🤖 InstAgent</h1>
                <p style="color: #94a3b8;">🚀 Instant Multi-Agent Systems at Your Fingertips</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        task = "Create a prompt writer agent that writes a prompt based on the user given task"

        example_tasks = [
            "Create a prompt writer agent that writes a prompt based on the user given task",
            "Create a web scraper agent that scrapes a website and saves the data to a database",
            "Create a data analysis agent that analyzes a dataset and provides a report",
            "Create a social media post generator agent that generates a post based on the user given task"
        ]
        # Add a dropdown to select an example task
        selected_example = st.selectbox(
            "🔍 Example Tasks",
            options=["Select an example..."] + example_tasks,
            index=0
        )

    # Update the task input area based on the selected example
    if selected_example != "Select an example...":
        task = selected_example

    # Set a default input for testing
    
    task = st.text_area(
        "Describe your agent task:",
        value=task,  # Use the selected example or default value
        height=100  # Reduced from 150 to 100 for a more compact layout
    )

    # Place the button before the workflow placeholder to keep it in a fixed position
    generate_button = st.button("✨ Generate Agent", type="primary", use_container_width=True)
    
    # Create the workflow placeholder after the button
    workflow_placeholder = st.empty()

    # Display existing outputs in the placeholder if they exist
    if st.session_state.running or any([st.session_state.team_creator_output,
                                      st.session_state.tool_picker_output,
                                      st.session_state.agent_code_output]):
        with workflow_placeholder.container():
            display_workflow_progress()
            display_agent_workflow()

    # Handle button click after defining the placeholder
    if generate_button:
        if task and st.session_state.openai_api_key:
            try:
                # Clear the placeholder to remove the previous output from the UI
                workflow_placeholder.empty()
                
                # Also refresh the container to ensure it's fully cleared
                with workflow_placeholder.container():
                    pass  # This refreshes the container
                
                # # Reset all output-related session state
                st.session_state.team_creator_output = None
                st.session_state.tool_picker_output = None
                st.session_state.agent_code_output = None
                st.session_state.agent_name = None
                # st.session_state.events = []
                
                # Now set running state
                st.session_state.running = True
                st.session_state.current_agent = "starting"

                
                events = run_agent_creator(
                    task, 
                    model=model,
                    temperature=temperature,
                    workflow_placeholder=workflow_placeholder
                )
                
                st.session_state.running = False
                st.toast("Agent creation completed!", icon="✅")
                
            except Exception as e:
                st.session_state.running = False
                st.session_state.current_agent = None
                st.error("Agent creation failed")
                st.markdown(f'<div class="error-box">{traceback.format_exc()}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please provide both a task description and valid API key")

if __name__ == "__main__":
    main()