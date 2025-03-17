#!/usr/bin/env python
# coding: utf-8
# fileName: AIPostAgent.py

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
tools_composio = toolset.get_tools(apps=[App.SERPAPI])
tools_linkedin = toolset.get_tools(apps=[App.LINKEDIN])

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

trend_researcher = create_react_agent(
    llm,
    tools=tools_composio,
    prompt=make_system_prompt(
        "You are an AI Trend Researcher. Your task is to identify and analyze the latest trending topics in AI. Use the COMPOSIO_SEARCH tool to gather data and insights on current AI trends. Focus on identifying key themes, emerging technologies, and popular discussions in the AI community. Compile your findings into a concise report that highlights the most relevant content ideas for further development."
    ),
)

def trend_research_node(state: MessagesState) -> Command:
    print("## AI Trend Researcher Execution In-progress: ")
    result = trend_researcher.invoke(state)
    goto = get_next_node(result["messages"][-1], "content_strategist")
    print("#### AI Trend Researcher Output: ", result["messages"][-1].content)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="trend_researcher"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

content_strategist = create_react_agent(
    llm,
    tools=tools_composio,
    prompt=make_system_prompt(
        "You are a Content Strategist. Your task is to develop an engaging and informative post based on the trending AI topics identified by Sophia. Use the COMPOSIO_SEARCH tool to refine and expand on the content ideas. Craft a compelling narrative that captures the essence of the trends and resonates with the target audience. Ensure the post is structured with a clear introduction, body, and conclusion, and includes any relevant data or examples."
    ),
)

def content_strategy_node(state: MessagesState) -> Command:
    print("## Content Strategist Execution In-progress: ")
    result = content_strategist.invoke(state)
    goto = get_next_node(result["messages"][-1], "social_media_specialist")
    print("#### Content Strategist Output: ", result["messages"][-1].content)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="content_strategist"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

social_media_specialist = create_react_agent(
    llm,
    tools=tools_linkedin,
    prompt=make_system_prompt(
        "You are a Social Media Specialist. Your task is to optimize and post the content developed by Liam on LinkedIn. Use your expertise to enhance the post's visibility and engagement. Consider using relevant hashtags, tagging influential figures, and scheduling the post for optimal times. Monitor the post's performance and engage with the audience by responding to comments and fostering discussions."
    ),
)

def social_media_node(state: MessagesState) -> Command:
    print("## Social Media Specialist Execution In-progress: ")
    result = social_media_specialist.invoke(state)
    goto = get_next_node(result["messages"][-1], END)
    print("#### Social Media Specialist Output: ", result["messages"][-1].content)
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="social_media_specialist"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

# Define the graph
workflow = StateGraph(MessagesState)
workflow.add_node("trend_researcher", trend_research_node)
workflow.add_node("content_strategist", content_strategy_node)
workflow.add_node("social_media_specialist", social_media_node)

workflow.add_edge(START, "trend_researcher")
workflow.add_edge("trend_researcher", "content_strategist")
workflow.add_edge("content_strategist", "social_media_specialist")
workflow.add_edge("social_media_specialist", END)

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