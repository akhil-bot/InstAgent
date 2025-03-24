#!/usr/bin/env python
# coding: utf-8
# fileName: LinkedInPostAgent.py

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
tools_codeinterpreter = toolset.get_tools(apps=[App.CODEINTERPRETER])
tools_linkedin = toolset.get_tools(apps=[App.LINKEDIN])
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
    "trend_node_output": "",
    "insight_node_output": "",
    "content_node_output": ""
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

def trend_node(state: MessagesState) -> Command:
    print("## Trend Researcher Execution In-progress: ")
    trend_prompt = ("You are a Trend Researcher. Your task is to identify and analyze trending topics that are relevant to our target audience. "
                    "Use the TAVILY tool to perform advanced searches and gather data on current trends.")
    trend_prompt += "\n#Input: \n" + f"{agent_state.get('user_input')}"
    
    trend_agent = create_react_agent(
        llm,
        tools=tools_tavily,
        prompt=make_system_prompt(trend_prompt),
    )
    result = trend_agent.invoke(state)
    agent_state["trend_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "insight_summarizer")
    print("#### Trend Researcher Output: ", agent_state["trend_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["trend_node_output"], name="trend_researcher"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def insight_node(state: MessagesState) -> Command:
    print("## Insight Summarizer Execution In-progress: ")
    insight_prompt = ("You are an Insight Summarizer. Your task is to take the research findings provided by Sophia and summarize the key insights. "
                      "Use the CODEINTERPRETER tool to analyze the data and extract the most relevant information.")
    insight_prompt += "\n#Input: \n" + f"{agent_state.get('trend_node_output')}"
    
    insight_agent = create_react_agent(
        llm,
        tools=tools_codeinterpreter,
        prompt=make_system_prompt(insight_prompt),
    )
    result = insight_agent.invoke(state)
    agent_state["insight_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "content_writer")
    print("#### Insight Summarizer Output: ", agent_state["insight_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["insight_node_output"], name="insight_summarizer"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def content_node(state: MessagesState) -> Command:
    print("## Content Writer Execution In-progress: ")
    content_prompt = ("You are a Content Writer. Your task is to craft an engaging LinkedIn post based on the insights summarized by Ethan. "
                      "Focus on creating a compelling narrative that effectively communicates the topic and insights to our audience.")
    content_prompt += "\n#Input: \n" + f"{agent_state.get('insight_node_output')}"
    
    content_agent = create_react_agent(
        llm,
        tools=[],
        prompt=make_system_prompt(content_prompt),
    )
    result = content_agent.invoke(state)
    agent_state["content_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "social_media_specialist")
    print("#### Content Writer Output: ", agent_state["content_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["content_node_output"], name="content_writer"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def social_media_node(state: MessagesState) -> Command:
    print("## Social Media Specialist Execution In-progress: ")
    social_media_prompt = ("You are a Social Media Specialist. Your task is to publish the LinkedIn post crafted by Liam and monitor its performance. "
                           "Use the LINKEDIN tool to post the content and track engagement metrics such as likes, shares, and comments.")
    social_media_prompt += "\n#Input: \n" + f"{agent_state.get('content_node_output')}"
    
    social_media_agent = create_react_agent(
        llm,
        tools=tools_linkedin,
        prompt=make_system_prompt(social_media_prompt),
    )
    result = social_media_agent.invoke(state)
    print("#### Social Media Specialist Output: ", result["messages"][-1].content)
    return Command(
        update={"messages": result["messages"]},
        goto=END,
    )

# Define the graph
workflow = StateGraph(MessagesState)
workflow.add_node("trend_researcher", trend_node)
workflow.add_node("insight_summarizer", insight_node)
workflow.add_node("content_writer", content_node)
workflow.add_node("social_media_specialist", social_media_node)

workflow.add_edge(START, "trend_researcher")
workflow.add_edge("trend_researcher", "insight_summarizer")
workflow.add_edge("insight_summarizer", "content_writer")
workflow.add_edge("content_writer", "social_media_specialist")
workflow.add_edge("social_media_specialist", END)

graph = workflow.compile()
user_input = input("Enter the target audience or topic to research trends on: ")
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