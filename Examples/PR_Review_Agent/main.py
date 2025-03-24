#!/usr/bin/env python
# coding: utf-8
# fileName: PRReviewAgent.py

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
tools_github = toolset.get_tools(apps=[App.GITHUB, App.CODEINTERPRETER])
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
    "code_quality_output": "",
    "coding_principles_output": "",
    "bug_detection_output": "",
    "integration_output": ""
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

def code_quality_node(state: MessagesState) -> Command:
    print("## Code Quality Agent Execution In-progress: ")
    code_quality_prompt = ("You are a Code Quality Analyst. Your task is to evaluate the code quality of the provided pull request link. "
                           "Use GitHub to access the pull request and the CodeInterpreter tool to analyze the code.")
    code_quality_prompt += "\n#Input: \n" + f"{agent_state.get('user_input')}"
    
    code_quality_agent = create_react_agent(
        llm,
        tools=tools_github,
        prompt=make_system_prompt(code_quality_prompt),
    )
    result = code_quality_agent.invoke(state)
    agent_state["code_quality_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "coding_principles")
    print("#### Code Quality Agent Output: ", agent_state["code_quality_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["code_quality_output"], name="code_quality_analyst"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def coding_principles_node(state: MessagesState) -> Command:
    print("## Coding Principles Agent Execution In-progress: ")
    coding_principles_prompt = ("You are a Coding Principles Specialist. Your task is to assess the adherence of the code in the pull request to established coding principles and best practices. "
                                "Use GitHub to review the code and the CodeInterpreter tool to evaluate its structure and design patterns.")
    coding_principles_prompt += "\n#Input: \n" + f"{agent_state.get('code_quality_output')}"
    
    coding_principles_agent = create_react_agent(
        llm,
        tools=tools_github,
        prompt=make_system_prompt(coding_principles_prompt),
    )
    result = coding_principles_agent.invoke(state)
    agent_state["coding_principles_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "bug_detection")
    print("#### Coding Principles Agent Output: ", agent_state["coding_principles_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["coding_principles_output"], name="coding_principles_specialist"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def bug_detection_node(state: MessagesState) -> Command:
    print("## Bug Detection Agent Execution In-progress: ")
    bug_detection_prompt = ("You are a Bug Detection Expert. Your task is to identify potential bugs and vulnerabilities in the proposed changes of the pull request. "
                            "Use GitHub to access the code and the CodeInterpreter tool to simulate and test the code for any issues.")
    bug_detection_prompt += "\n#Input: \n" + f"{agent_state.get('coding_principles_output')}"
    
    bug_detection_agent = create_react_agent(
        llm,
        tools=tools_github,
        prompt=make_system_prompt(bug_detection_prompt),
    )
    result = bug_detection_agent.invoke(state)
    agent_state["bug_detection_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], "integration")
    print("#### Bug Detection Agent Output: ", agent_state["bug_detection_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["bug_detection_output"], name="bug_detection_expert"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

def integration_node(state: MessagesState) -> Command:
    print("## Integration Agent Execution In-progress: ")
    integration_prompt = ("You are an Integration Specialist. Your task is to ensure that the proposed changes in the pull request integrate smoothly with the existing codebase. "
                          "Use GitHub to review the changes and the CodeInterpreter tool to test the integration.")
    integration_prompt += "\n#Input: \n" + f"{agent_state.get('bug_detection_output')}"
    
    integration_agent = create_react_agent(
        llm,
        tools=tools_github,
        prompt=make_system_prompt(integration_prompt),
    )
    result = integration_agent.invoke(state)
    agent_state["integration_output"] = result["messages"][-1].content
    goto = get_next_node(result["messages"][-1], END)
    print("#### Integration Agent Output: ", agent_state["integration_output"])
    result["messages"][-1] = HumanMessage(
        content=agent_state["integration_output"], name="integration_specialist"
    )
    return Command(
        update={"messages": result["messages"]},
        goto=goto,
    )

# Define the graph
workflow = StateGraph(MessagesState)
workflow.add_node("code_quality_analyst", code_quality_node)
workflow.add_node("coding_principles_specialist", coding_principles_node)
workflow.add_node("bug_detection_expert", bug_detection_node)
workflow.add_node("integration_specialist", integration_node)

workflow.add_edge(START, "code_quality_analyst")
workflow.add_edge("code_quality_analyst", "coding_principles_specialist")
workflow.add_edge("coding_principles_specialist", "bug_detection_expert")
workflow.add_edge("bug_detection_expert", "integration_specialist")
workflow.add_edge("integration_specialist", END)

graph = workflow.compile()
user_input = input("Enter the GitHub pull request link: ")
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