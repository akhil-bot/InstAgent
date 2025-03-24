#!/usr/bin/env python
# coding: utf-8
# fileName: BlogWriterAgent.py

# Import necessary libraries
import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, START, END, StateGraph
from langgraph.types import Command
from langchain_core.messages import BaseMessage, HumanMessage

# Define tools
from composio_langgraph import Action, ComposioToolSet, App
toolset = ComposioToolSet()
tools_tavily = toolset.get_tools(apps=[App.TAVILY])
tools_notion = toolset.get_tools(apps=[App.NOTION])
verbose = False

if not os.environ.get("OPENAI_API_KEY"):
    api_key = input("Enter your OpenAI API key: ")
    os.environ["OPENAI_API_KEY"] = api_key

if not os.environ.get("COMPOSIO_API_KEY"):
    api_key = input("Enter your Composio API key: ")
    os.environ["COMPOSIO_API_KEY"] = api_key

# Define agent nodes
llm = ChatOpenAI(model="gpt-4o")

# will maintain the state of the whole team include inputs and outputs
agent_state = {
    "research_node_output": "",
    "outline_node_output": "",
    "writing_node_output": "",
    "editing_node_output": ""
}

# Define system prompts
def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards answering the question."
        " If you are unable to fully answer, that's OK, another assistant with different tools "
        " will help where you left off. Execute what you can to make progress."
        " If you or any of the other assistants have the final answer or deliverable,"
        " prefix your response with FINAL ANSWER so the team knows to stop."
        "\nTask:\n"
        f"{suffix}"
    )

def get_next_node(last_message: BaseMessage, goto: str):
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return END
    return goto

def research_node(state: MessagesState) -> Command:
    print("## Research Agent Execution In-progress: ")
    research_prompt = ("You are a Research Specialist. Your task is to conduct thorough online research to gather accurate and relevant information on the given topic. "
                       "Use the TAVILY tool to perform advanced searches, including image inclusion and domain filtering, to find credible sources.")
    research_prompt += "\n#Input: \n" + f"{agent_state.get('user_input')}"
    
    research_agent = create_react_agent(
        llm,
        tools=tools_tavily,
        prompt=make_system_prompt(research_prompt),
    )
    result = research_agent.invoke(state)
    agent_state["research_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "content_strategist")
    print("#### Research Agent Output: ", agent_state["research_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["research_node_output"], name="researcher"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def outline_node(state: MessagesState) -> Command:
    print("## Outline Agent Execution In-progress: ")
    outline_prompt = ("You are a Content Strategist. Your task is to organize and structure the gathered information into a coherent outline for the blog. "
                      "Use Notion to create a structured outline that logically organizes the information into sections and subsections.")
    outline_prompt += "\n#Input: \n" + f"{agent_state.get('research_node_output')}"
    
    outline_agent = create_react_agent(
        llm,
        tools=tools_notion,
        prompt=make_system_prompt(outline_prompt),
    )
    result = outline_agent.invoke(state)
    agent_state["outline_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "writer")
    print("#### Outline Agent Output: ", agent_state["outline_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["outline_node_output"], name="content_strategist"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def writing_node(state: MessagesState) -> Command:
    print("## Writing Agent Execution In-progress: ")
    writing_prompt = ("You are a Writer. Your task is to compose a comprehensive and engaging blog post based on the structured outline provided by the Content Strategist.")
    writing_prompt += "\n#Input: \n" + f"{agent_state.get('outline_node_output')}"
    
    writing_agent = create_react_agent(
        llm,
        tools=[],
        prompt=make_system_prompt(writing_prompt),
    )
    result = writing_agent.invoke(state)
    agent_state["writing_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "editor")
    print("#### Writing Agent Output: ", agent_state["writing_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["writing_node_output"], name="writer"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def editing_node(state: MessagesState) -> Command:
    print("## Editing Agent Execution In-progress: ")
    editing_prompt = ("You are an Editor. Your task is to review and refine the blog post to ensure clarity, coherence, and grammatical accuracy.")
    editing_prompt += "\n#Input: \n" + f"{agent_state.get('writing_node_output')}"
    
    editing_agent = create_react_agent(
        llm,
        tools=[],
        prompt=make_system_prompt(editing_prompt),
    )
    result = editing_agent.invoke(state)
    agent_state["editing_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], END)
    print("#### Editing Agent Output: ", agent_state["editing_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["editing_node_output"], name="editor"
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
user_input = input("Enter the topic to research on: ")
agent_state["user_input"] = user_input

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
    if verbose:
        print(s)
        print("----")
    pass