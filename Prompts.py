from Tools import Tools
class Prompts:
  def __init__(self):
    self.tools = Tools().get_available_tools()
    self.team_creation_prompt = '''
    Create a team of members to achieve a user-given task without any supervision. Each team member should have a defined role, goal, and backstory based on the task assigned to them. Additionally, establish connections between team members to represent collaboration and workflow, similar to edges in a graph.

# Task
{input}

# Steps

1. **Understand the Task**: Analyze the user-given task to determine the skills and roles required to accomplish it.
2. **Define Roles**: Identify and define the roles necessary for the task. Each role should be distinct and contribute to the overall goal.
3. **Assign Goals**: For each role, specify a clear goal that aligns with the task's objectives.
4. **Create Backstories**: Develop a backstory for each team member that justifies their role and goal. The backstory should provide context and motivation.
5. **Assign Unique IDs**: Generate a unique identifier for each team member to ensure structured connections.
6. **Establish Connections**: Define connections between team members, representing dependencies, collaboration, and information flow. Each connection should specify the source and target members using their unique IDs. And alwasys start the connection with START and ends with END.
7. **Assemble the Team**: Compile the team members into a cohesive unit, ensuring that their roles and goals are complementary.
8. **Create a Name for the Team**: Create a name for the team that is relevant to the task and always try to use word Agent in the name.

# Output Format

The output should be in JSON format, consisting of only team members and connections between them structured as follows. Do not include any additional text or commentary outside of the JSON.

```json
{
  "name": "[Team Name]",
  "team": [
    {
      "id": "[Unique Member ID]",
      "name": "[Member Name]",
      "role": "[Role]",
      "goal": "[Goal]",
      "backstory": "[Backstory]"
    }
    // Add more team members as needed
  ],
  "connections": [
    {
      "id": "[Unique Connection ID]",
      "from": "[Source Member ID]",
      "to": "[Target Member ID]"
    }
    // Add more connections as needed
  ]
}
```

# Examples

**Example Input**: "Develop a new marketing strategy for a tech startup."

**Example Output**:

```json
{
  "name": "Marketing Agent",
  "team": [
    {
      "id": "t1",
      "name": "Alex Johnson",
      "role": "Marketing Strategist",
      "goal": "Create a comprehensive marketing plan to increase brand awareness.",
      "backstory": "Alex has a decade of experience in digital marketing and has successfully launched campaigns for several startups."
    },
    {
      "id": "t2",
      "name": "Jamie Lee",
      "role": "Data Analyst",
      "goal": "Analyze market trends and consumer data to inform strategy decisions.",
      "backstory": "Jamie is a data enthusiast with a background in economics and a passion for uncovering insights from complex datasets."
    },
    {
      "id": "t3",
      "name": "Taylor Smith",
      "role": "Creative Director",
      "goal": "Develop engaging content and visuals to support the marketing strategy.",
      "backstory": "Taylor has a strong background in graphic design and has worked with various tech companies to enhance their visual branding."
    }
  ],
  "connections": [
    {
      "id": "c1",
      "from": "START",
      "to": "t1"
    }
    {
      "id": "c2",
      "from": "t1",
      "to": "t2"
    },
    {
      "id": "c3",
      "from": "t2",
      "to": "t3"
    },
    {
      "id": "c4",
      "from": "t3",
      "to": "END"
    }
  ]
}
```

# Notes

- Ensure that each team member's role and goal are directly relevant to the task.
- The backstory should provide enough detail to understand the member's expertise and motivation.
- Assign unique IDs to each team member to maintain structured connections.
- Define logical connections between members, representing collaboration, dependencies, or knowledge transfer.
- Consider the diversity of skills and perspectives to create a well-rounded team.


    '''

    
    self.tool_picker_prompt = '''
Identify the appropriate tools for each team member based on their role, goal, and backstory, using only the provided available tools list.

Consider the following when selecting tools:
- Match the tool's capabilities with the team member's role and goal.
- Ensure the tool is enabled and does not require authentication if the team member cannot provide it.
- Use only the provided available tools and nothing more.
- Refer to the tool's description and categories to determine its suitability.
- If user specifies a tool, make sure to use that tool whenever the team member's goal is related to that tool.

# Available Tools:
{available_tools}

# Steps

1. **Tool Assignment:**  
   - **Analyze Team Member Details:** For each team member, carefully review their role, goal, and backstory.  
   - **Review Available Tools:** Examine the provided list of tools. Check each tool’s description, categories, enabled status, and authentication requirements.  
   - **Match Tools to Needs:** Select the tool(s) that best align with the team member’s responsibilities. Only choose tools that are enabled and require no authentication (unless the team member can provide it).  
   - **Assign Tools:** Add a `"tools"` field (an array of tool keys) to each team member. If no tool is appropriate, leave the array empty.
   - **Priority**: Prioritize tools that require no authentication or are free over those that require authorization.



2. **Team Member-Specific Prompt Generation:**  
   - **Generate a Clear, Role-Specific Prompt:** For each team member, generate an actionable prompt based on their role and goal. The generated prompt should:
     - **Start with a Role Statement:** E.g., "You are a [Role]."
     - **Clearly Define the Task:** E.g., "Your task is to [Goal]."
     - **Provide Step-by-Step Guidance:** Offer specific instructions or steps the team member should follow to achieve their goal.
     - **Suggest Using Tools:** Optionally mention the assigned tools if they can assist in completing the task.
     - **Specify Expected Output:** Indicate the expected structure or format of the outcome, if relevant.
     - Examples: Include high-quality examples if helpful, using placeholders [in brackets] for complex elements.
        - What kinds of examples may need to be included, how many, and whether they are complex enough to benefit from placeholders.
     - Clarity and Conciseness: Use clear, specific language. Avoid unnecessary instructions or bland statements.
     - Formatting: Use markdown features for readability. DO NOT USE ``` CODE BLOCKS UNLESS SPECIFICALLY REQUESTED. Use ```json for JSON output. DO NOT USE H1, H2 of markdowns.
     - Preserve User Content: If the input task or prompt includes extensive guidelines or examples, preserve them entirely, or as closely as possible. If they are vague, consider breaking down into sub-steps. Keep any details, guidelines, examples, variables, or placeholders provided by the user.


# Output Format

    Produce a valid JSON object with the following structure:
    - A `"team"` array where each team member object includes:
     - `"id"`, `"name"`, `"role"`, `"goal"`, and `"backstory"` (as provided),
     - A new `"tools"` field listing the assigned tool keys,
     - A new `"prompt"` field containing the generated team member-specific prompt.
    - A `"connections"` array as provided in the input.


# Example

**Input:**

```json
{
  "name": "Marketing Agent",
  "team": [
    {
      "id": "t1",
      "name": "Alice Smith",
      "role": "Data Analyst",
      "goal": "Analyze sales data to identify trends and insights.",
      "backstory": "Alice has a strong background in data science and is skilled in using analytical tools to derive actionable insights."
    },
    {
      "id": "t2",
      "name": "Bob Johnson",
      "role": "Marketing Specialist",
      "goal": "Develop a marketing strategy based on current market trends.",
      "backstory": "Bob is an experienced marketer with a knack for identifying emerging trends and crafting effective strategies."
    }
  ],
  "connections": [
    {
      "id": "c1",
      "from": "START",
      "to": "t1"
    },
    {
      "id": "c2",
      "from": "t1",
      "to": "t2"
    },
    {
      "id": "c3",
      "from": "t2",
      "to": "END"
    }
  ]
}
```

**Output:**


```json
{
  "name": "Marketing Agent",
  "team": [
    {
      "id": "t1",
      "name": "Alice Smith",
      "role": "Data Analyst",
      "goal": "Analyze sales data to identify trends and insights.",
      "backstory": "Alice has a strong background in data science and is skilled in using analytical tools to derive actionable insights.",
      "tools": ["COMPOSIO_SEARCH"],
      "prompt": "You are a skilled Data Analyst. Your task is to analyze the provided sales data to identify key trends and insights. Use statistical methods and visualization techniques to highlight patterns, outliers, and actionable insights. Leverage the COMPOSIO_SEARCH tool if needed to gather additional context and data. Present your findings in a clear, structured report with supporting data points."
    },
    {
      "id": "t2",
      "name": "Bob Johnson",
      "role": "Marketing Specialist",
      "goal": "Develop a marketing strategy based on current market trends.",
      "backstory": "Bob is an experienced marketer with a knack for identifying emerging trends and crafting effective strategies.",
      "tools": [],
      "prompt": "As a Marketing Specialist, your task is to develop an effective marketing strategy based on the latest market trends. Identify key customer behaviors, competitor strategies, and emerging market trends. Use data-driven insights to propose actionable recommendations. Structure your strategy in a concise report and consider any available tools that can assist in market research."
    }
  ],
  "connections": [
    {
      "id": "c1",
      "from": "START",
      "to": "t1"
    },
    {
      "id": "c2",
      "from": "t1",
      "to": "t2"
    },
    {
      "id": "c3",
      "from": "t2",
      "to": "END"
    }
  ]
}
```

# Input:
{input}

Now, let's think step by step and determine the right armory of tools from the available list along with a dedicated prompt for each team member.

'''

    self.agent_code_generation_prompt = '''
            Generate a Langgraph code for a multi-agent network using the provided team member details in JSON format. The code should define agents based on their roles, goals, and tools, and establish connections between them to achieve the task.
        
        # Steps
        
        1. **Parse JSON Input**: Extract team member details and connections from the provided JSON.
        2. **Define Tools**: Identify and define the tools each agent will use.
        3. **Use Prompts**: Use the system prompt provided under "prompt" key for each team member.
        4. **Define Agent Nodes**: Create agent nodes using Langgraph, specifying the tools and system prompts for each agent.
        5. **Establish Connections**: Use the connections from the JSON to define the flow between agents.
        6. **Inputs from User**: Ask user to input all the details to successfully run the code to achieve the task.
        7. **Compile the Graph**: Combine all nodes and connections to compile the Langgraph.
        8. **Invoke the Graph**: Set up the graph to be invoked with a specific task, ensuring each agent performs its role in sequence.
        9. **Environment Variables**: Ensure the code includes environment variable checks for OPENAI_API_KEY and COMPOSIO_API_KEY.
        10. **Error Handling**: Add error handling to the code to handle any potential issues with the API keys or tool usage.
        
        # Output Format
          ## Requirements
          
          - The output must be a complete, syntactically correct Python script.
          - The output must contain only the Python code without any additional commentary or explanation.
          - Create a unique file name for the output file based on the team name.
          - Do not include any text outside of the Python code.
          - Import statements for necessary libraries.
          - Definitions for each agent node with their respective tools and system prompts.
          - Connections between nodes as specified in the JSON.
          - A compiled graph ready for invocation.
        
      
        
        # Examples
        
        **Input JSON:**
        ```json
        ```json
{
  "name": "Research Agent",
  "team": [
    {
      "id": "t1",
      "name": "Dr. Emily Carter",
      "role": "Research Specialist",
      "goal": "Conduct thorough research on the given topic to gather reliable and relevant data.",
      "backstory": "Dr. Carter holds a PhD in Information Science and has spent years refining her ability to source and synthesize data from diverse, credible sources. Her meticulous nature ensures no detail is overlooked.",
      "tools": ["COMPOSIO_SEARCH", "CODEINTERPRETER"],
      "prompt": "You are a Research Specialist. Your task is to conduct comprehensive research on the assigned topic to gather reliable and relevant data. Begin by identifying key aspects of the topic that require investigation. Use the COMPOSIO_SEARCH tool to locate high-quality articles, papers, and credible sources. If data analysis or summarization is needed, utilize the CODEINTERPRETER tool to process datasets or extract insights. Organize your findings in a well-structured document, clearly citing all sources and highlighting critical information that may inform future stages of content creation."
    },
    {
      "id": "t2",
      "name": "Marcus Lee",
      "role": "Outline Architect",
      "goal": "Transform researched data into a logical and engaging blog structure.",
      "backstory": "Marcus is a former content strategist who excels at organizing complex information into digestible frameworks. His ability to translate raw data into reader-friendly formats makes him indispensable for content planning.",
      "tools": ["COMPOSIO_SEARCH"],
      "prompt": "You are an expert Outline Architect. Your task is to take the researched data and create a logical, engaging blog structure that flows smoothly for readers. Begin by identifying key themes and insights from the data. Use COMPOSIO_SEARCH if you need additional context or examples to enrich the outline. Structure the blog with clear sections, headings, and subheadings, ensuring a logical flow from introduction to conclusion. Your final output should be a detailed outline ready for the drafting phase, including notes on tone, key points for each section, and any important transitions."
    }
  ],
  "connections": [
    {
      "id": "c1",
      "from": "START",
      "to": "t1"
    },
    {
      "id": "c2",
      "from": "t1",
      "to": "t2"
    },
    {
      "id": "c3",
      "from": "t2",
      "to": "END"
    }
  ]
}
```
        ```
        
        **Langgraph Code Output:**
        ```python
        #!/usr/bin/env python
        # coding: utf-8
        # fileName: ResearchAgent.py
        
        # Import necessary libraries
        import getpass
        import os
        from langchain_core.tools import tool
        from langchain_experimental.utilities import PythonREPL
        from langchain_openai import ChatOpenAI
        from langgraph.prebuilt import create_react_agent
        from langgraph.graph import MessagesState, START,END, StateGraph
        from langgraph.types import Command
        from langchain_core.messages import BaseMessage, HumanMessage
        
        # Define tools
        from composio_langgraph import Action, ComposioToolSet, App
        toolset = ComposioToolSet()
        tools = toolset.get_tools(apps=[App.COMPOSIO_SEARCH]) # contains comma separate tools list and ALWAYS prefix with "App." for each tool

        if not os.environ.get("OPENAI_API_KEY"):
            api_key = input("Enter your OpenAI API key: ")
            os.environ["OPENAI_API_KEY"] = api_key
        
        if not os.environ.get("COMPOSIO_API_KEY"):
            api_key = input("Enter your Composio API key: ")
            os.environ["COMPOSIO_API_KEY"] = api_key
        
        # Define agent nodes
        llm = ChatOpenAI(model="gpt-4o")
        
        # Define system prompts
        def make_system_prompt(suffix: str) -> str:
            return (
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                f"\n{suffix}"
            )

        def get_next_node(last_message: BaseMessage, goto: str):
          if "FINAL ANSWER" in last_message.content:
              # Any agent decided the work is done
              return END
          return goto
        
        research_agent = create_react_agent(
            llm,
            tools=tools,
            prompt=make_system_prompt(
                "You are a Research Specialist. Your task is to conduct comprehensive research on the assigned topic to gather reliable and relevant data. Begin by identifying key aspects of the topic that require investigation. Use the COMPOSIO_SEARCH tool to locate high-quality articles, papers, and credible sources. If data analysis or summarization is needed, utilize the CODEINTERPRETER tool to process datasets or extract insights. Organize your findings in a well-structured document, clearly citing all sources and highlighting critical information that may inform future stages of content creation."
            ),
        )
        
        def research_node(state: MessagesState) -> Command:
            print("## Research Agent Execution In-progress: ")
            result = research_agent.invoke(state)
            goto = get_next_node(result["messages"][-1], "outline_architect")
            print("#### Research Agent Output: ", result["messages"][-1].content)
            result["messages"][-1] = HumanMessage(
                content=result["messages"][-1].content, name="researcher"
            )
            return Command(
                update={"messages": result["messages"]},
                goto=goto,
            )
        
        outline_agent = create_react_agent(
            llm,
            tools=tools,
            prompt=make_system_prompt(
                "You are an expert Outline Architect. Your task is to take the researched data and create a logical, engaging blog structure that flows smoothly for readers. Begin by identifying key themes and insights from the data. Use COMPOSIO_SEARCH if you need additional context or examples to enrich the outline. Structure the blog with clear sections, headings, and subheadings, ensuring a logical flow from introduction to conclusion. Your final output should be a detailed outline ready for the drafting phase, including notes on tone, key points for each section, and any important transitions."
            ),
        )
        
        def outline_node(state: MessagesState) -> Command:
            print("## Outline Agent Execution In-progress: ")
            result = outline_agent.invoke(state)
            goto = get_next_node(result["messages"][-1], END)
            print("#### Outline Agent Output: ", result["messages"][-1].content)
            result["messages"][-1] = HumanMessage(
                content=result["messages"][-1].content, name="outline_architect"
            )
            return Command(
                update={"messages": result["messages"]},
                goto=goto,
            )
        
        # Define the graph
        workflow = StateGraph(MessagesState)
        workflow.add_node("researcher", research_node)
        workflow.add_node("outline_architect", outline_node)
        
        workflow.add_edge(START, "researcher")
        workflow.add_edge("researcher", "outline_architect")
        workflow.add_edge("outline_architect", END)
        
        graph = workflow.compile()
        user_input = input("Enter the topic to research on: ") # Make this dynamic according to the task to be achieved
        
        # Invoke the graph
        events = graph.stream(
            {
                "messages": [
                    (
                        "user",
                        f"{user_input}"
                    )
                ],
            },
            {"recursion_limit": 150},
        )
        for s in events:
            print(s)
            print("----")
        ```
        
        # Notes
        
        - Ensure each agent's role and tools are accurately represented in the system prompts and node definitions.
        - The graph should reflect the connections specified in the JSON, ensuring a logical flow of tasks.
        - The example provided is a simplified version; real-world applications may require more complex logic and error handling.
        
        #Input:
        {input}
        
        Now Think step by step to write the langgraph code for the given team

        '''