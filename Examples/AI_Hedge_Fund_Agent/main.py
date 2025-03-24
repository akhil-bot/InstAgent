#!/usr/bin/env python
# coding: utf-8
# fileName: AIHedgeFundAgent.py

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
tools_tavily_serpapi = toolset.get_tools(apps=[App.TAVILY, App.SERPAPI])
tools_codeinterpreter = toolset.get_tools(apps=[App.CODEINTERPRETER])
tools_googlesheets = toolset.get_tools(apps=[App.GOOGLESHEETS])
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
    "fundamental_node_output": "",
    "technical_node_output": "",
    "data_scientist_node_output": "",
    "risk_manager_node_output": "",
    "portfolio_manager_node_output": ""
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

def fundamental_node(state: MessagesState) -> Command:
    print("## Fundamental Analyst Execution In-progress: ")
    fundamental_prompt = ("You are a Fundamental Analyst. Your task is to conduct an in-depth fundamental analysis of the specified stock. "
                          "Use the TAVILY and SERPAPI tools to gather financial statements and market data.")
    fundamental_prompt += "\n#Input: \n" + f"{agent_state.get('user_input')}"
    
    fundamental_agent = create_react_agent(
        llm,
        tools=tools_tavily_serpapi,
        prompt=make_system_prompt(fundamental_prompt),
    )
    result = fundamental_agent.invoke(state)
    agent_state["fundamental_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "technical_analyst")
    print("#### Fundamental Analyst Output: ", agent_state["fundamental_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["fundamental_node_output"], name="fundamental_analyst"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def technical_node(state: MessagesState) -> Command:
    print("## Technical Analyst Execution In-progress: ")
    technical_prompt = ("You are a Technical Analyst. Your task is to perform technical analysis on the specified stock. "
                        "Use the CODEINTERPRETER tool to analyze chart patterns and apply technical indicators.")
    technical_prompt += "\n#Input: \n" + f"{agent_state.get('fundamental_node_output')}"
    
    technical_agent = create_react_agent(
        llm,
        tools=tools_codeinterpreter,
        prompt=make_system_prompt(technical_prompt),
    )
    result = technical_agent.invoke(state)
    agent_state["technical_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "data_scientist")
    print("#### Technical Analyst Output: ", agent_state["technical_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["technical_node_output"], name="technical_analyst"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def data_scientist_node(state: MessagesState) -> Command:
    print("## Data Scientist Execution In-progress: ")
    data_scientist_prompt = ("You are a Data Scientist. Your task is to develop machine learning models to improve stock prediction accuracy. "
                             "Use the CODEINTERPRETER tool to build and train models using historical stock data.")
    data_scientist_prompt += "\n#Input: \n" + f"{agent_state.get('technical_node_output')}"
    
    data_scientist_agent = create_react_agent(
        llm,
        tools=tools_codeinterpreter,
        prompt=make_system_prompt(data_scientist_prompt),
    )
    result = data_scientist_agent.invoke(state)
    agent_state["data_scientist_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "risk_manager")
    print("#### Data Scientist Output: ", agent_state["data_scientist_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["data_scientist_node_output"], name="data_scientist"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def risk_manager_node(state: MessagesState) -> Command:
    print("## Risk Manager Execution In-progress: ")
    risk_manager_prompt = ("You are a Risk Manager. Your task is to assess and manage the risks associated with the stock recommendations. "
                           "Use GOOGLESHEETS to organize and analyze risk factors.")
    risk_manager_prompt += "\n#Input: \n" + f"{agent_state.get('data_scientist_node_output')}"
    
    risk_manager_agent = create_react_agent(
        llm,
        tools=tools_googlesheets,
        prompt=make_system_prompt(risk_manager_prompt),
    )
    result = risk_manager_agent.invoke(state)
    agent_state["risk_manager_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "portfolio_manager")
    print("#### Risk Manager Output: ", agent_state["risk_manager_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["risk_manager_node_output"], name="risk_manager"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def portfolio_manager_node(state: MessagesState) -> Command:
    print("## Portfolio Manager Execution In-progress: ")
    portfolio_manager_prompt = ("You are a Portfolio Manager. Your task is to integrate the analysis and recommendations from the team into actionable investment strategies. "
                                "Use NOTION to compile and organize the insights.")
    portfolio_manager_prompt += "\n#Input: \n" + f"{agent_state.get('risk_manager_node_output')}"
    
    portfolio_manager_agent = create_react_agent(
        llm,
        tools=tools_notion,
        prompt=make_system_prompt(portfolio_manager_prompt),
    )
    result = portfolio_manager_agent.invoke(state)
    agent_state["portfolio_manager_node_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], END)
    print("#### Portfolio Manager Output: ", agent_state["portfolio_manager_node_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["portfolio_manager_node_output"], name="portfolio_manager"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

# Define the graph
workflow = StateGraph(MessagesState)
workflow.add_node("fundamental_analyst", fundamental_node)
workflow.add_node("technical_analyst", technical_node)
workflow.add_node("data_scientist", data_scientist_node)
workflow.add_node("risk_manager", risk_manager_node)
workflow.add_node("portfolio_manager", portfolio_manager_node)

workflow.add_edge(START, "fundamental_analyst")
workflow.add_edge("fundamental_analyst", "technical_analyst")
workflow.add_edge("technical_analyst", "data_scientist")
workflow.add_edge("data_scientist", "risk_manager")
workflow.add_edge("risk_manager", "portfolio_manager")
workflow.add_edge("portfolio_manager", END)

graph = workflow.compile()
user_input = input("Enter the stock symbol to analyze: ")  # Make this dynamic according to the task to be achieved and store it in the agent_state with same name
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