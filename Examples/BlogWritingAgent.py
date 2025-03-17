#!/usr/bin/env python
# coding: utf-8
# fileName: BlogWritingAgent.py

# Import necessary libraries
import getpass
import os
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.types import Command
from langchain_core.messages import BaseMessage, HumanMessage

# Define tools
from composio_langgraph import Action, ComposioToolSet, App
toolset = ComposioToolSet()
tools = toolset.get_tools(apps=[App.SERPAPI]) # contains comma separate tools list and ALWAYS prefix with "App." for each tool

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
        f"{suffix}"
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
        "You are a Topic Researcher. Your task is to conduct thorough research on the given topic to gather relevant information and insights. Use the COMPOSIO_SEARCH tool to find credible sources, statistics, and expert opinions. Compile your findings into a comprehensive research document, highlighting key points and insights that will inform the content strategy and writing process."
    ),
)

def research_node(state: MessagesState) -> Command:
    print("## Research Agent Execution In-progress: ")
    result = research_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "content_strategist")
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
    tools=[],
    prompt=make_system_prompt(
        "You are a Content Strategist. Your task is to outline the blog structure based on the research provided by Emma. Ensure the content aligns with the target audience's interests and preferences. Identify key sections, headings, and subheadings that will guide the writing process. Provide a clear and logical flow for the blog, ensuring it is engaging and informative."
    ),
)

def outline_node(state: MessagesState) -> Command:
    print("## Outline Agent Execution In-progress: ")
    result = outline_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "writer")
    print("#### Outline Agent Output: ", result["messages"][-1].content)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="content_strategist"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

writing_agent = create_react_agent(
    llm,
    tools=tools,
    prompt=make_system_prompt(
        "You are a Writer. Your task is to write a compelling and coherent blog draft based on the research and outline provided by Emma and Liam. Use the COMPOSIO_SEARCH tool to enhance your writing with context-aware suggestions and automation. Focus on creating an engaging narrative that captures the reader's attention while conveying the key messages effectively. Ensure the draft is well-structured and flows logically from one section to the next."
    ),
)

def writing_node(state: MessagesState) -> Command:
    print("## Writing Agent Execution In-progress: ")
    result = writing_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "editor")
    print("#### Writing Agent Output: ", result["messages"][-1].content)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="writer"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

editing_agent = create_react_agent(
    llm,
    tools=[],
    prompt=make_system_prompt(
        "You are an Editor. Your task is to review and refine the blog draft written by Sophia. Ensure the content is clear, coherent, and free of grammatical errors. Pay attention to the flow and structure of the blog, making adjustments as necessary to enhance readability and engagement. Provide feedback and suggestions for improvement, ensuring the final draft is publication-ready."
    ),
)

def editing_node(state: MessagesState) -> Command:
    print("## Editing Agent Execution In-progress: ")
    result = editing_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], END)
    print("#### Editing Agent Output: ", result["messages"][-1].content)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="editor"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

# Define the graph
workflow = StateGraph(MessagesState)
workflow.add_node("researcher", research_node)
workflow.add_node("content_strategist", outline_node)
workflow.add_node("writer", writing_node)
workflow.add_node("editor", editing_node)

workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "content_strategist")
workflow.add_edge("content_strategist", "writer")
workflow.add_edge("writer", "editor")
workflow.add_edge("editor", END)

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
    pass
    # print(s)
    # print("----")