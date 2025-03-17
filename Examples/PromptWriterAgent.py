#!/usr/bin/env python
# coding: utf-8
# fileName: PromptWriterAgent.py

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
        f"{suffix}"
    )

def get_next_node(last_message: BaseMessage, goto: str):
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    return goto

task_analyst_agent = create_react_agent(
    llm,
    tools=tools,
    prompt=make_system_prompt(
        "You are a Task Analyst. Your task is to understand and break down the user-given task into key components. Start by thoroughly reading the task description. Use the COMPOSIO_SEARCH tool to gather any additional context or information that might be needed. Identify the main objectives, sub-tasks, and any dependencies. Document these components clearly, ensuring they are easy to understand and logically organized."
    ),
)

def task_analyst_node(state: MessagesState) -> Command:
    result = task_analyst_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "creative_writer")
    print("#### Task Analyst Output: ", result["messages"][-1].content)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="task_analyst"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

creative_writer_agent = create_react_agent(
    llm,
    tools=tools,
    prompt=make_system_prompt(
        "You are a Creative Writer. Your task is to craft a coherent and engaging prompt based on the analyzed task components provided by the Task Analyst. Use your creativity to make the prompt engaging and clear. Leverage the COMPOSIO_SEARCH tool to find inspiration or examples of similar prompts. Ensure the prompt aligns with the task requirements and is structured in a way that guides the user effectively."
    ),
)

def creative_writer_node(state: MessagesState) -> Command:
    result = creative_writer_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], "quality_reviewer")
    print("#### Creative Writer Output: ", result["messages"][-1].content)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="creative_writer"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

quality_reviewer_agent = create_react_agent(
    llm,
    tools=[],
    prompt=make_system_prompt(
        "You are a Quality Reviewer. Your task is to review the prompt crafted by the Creative Writer for clarity, coherence, and alignment with the task requirements. Carefully read through the prompt, checking for any grammatical errors, unclear instructions, or inconsistencies. Ensure that the prompt is engaging and effectively communicates the task. Provide feedback or make necessary edits to enhance the quality of the prompt."
    ),
)

def quality_reviewer_node(state: MessagesState) -> Command:
    result = quality_reviewer_agent.invoke(state)
    goto = get_next_node(result["messages"][-1], END)
    print("#### Quality Reviewer Output: ", result["messages"][-1].content)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="quality_reviewer"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

# Define the graph
workflow = StateGraph(MessagesState)
workflow.add_node("task_analyst", task_analyst_node)
workflow.add_node("creative_writer", creative_writer_node)
workflow.add_node("quality_reviewer", quality_reviewer_node)

workflow.add_edge(START, "task_analyst")
workflow.add_edge("task_analyst", "creative_writer")
workflow.add_edge("creative_writer", "quality_reviewer")
workflow.add_edge("quality_reviewer", END)

graph = workflow.compile()
user_input = input("Enter the task to analyze and create a prompt for: ") # Make this dynamic according to the task to be achieved

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