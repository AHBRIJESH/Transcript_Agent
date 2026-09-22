import os
import json
import requests

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode,tools_condition

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

if not api_key:
    raise ValueError("api_key not found in .env")

llm = ChatOpenAI(
    model="ibm-granite/granite-4.2-8b",
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    temperature=0.7,
    max_tokens=4096,
    extra_body={
        "reasoning": {
            "enabled": False
        }
    }
)

def perform_initial_analysis():

    with open("transcripts.json", "r", encoding="utf-8") as file:
        transcripts = json.load(file)

    prompt = f"""
You are an expert interview research analyst.

Analyze the complete collection of interview transcripts provided below.

Generate a structured report containing:

1. Overall summary
2. Common themes across interviews
3. Disagreements and contrasting opinions
4. Key findings
5. Important follow-up areas
6. Frequently mentioned problems or needs

Rules:

- Use only the provided transcripts.
- Do not invent facts.
- Do not invent quotes.
- Do not invent timestamps.
- Distinguish common themes from isolated opinions.
- Identify disagreements only when supported by the transcripts.
- This report is for broad understanding.
- Return the result in clear Markdown format.

TRANSCRIPTS:

{json.dumps(transcripts, ensure_ascii=False, indent=2)}
"""

    response = llm.invoke([
        SystemMessage(
            content="You are an expert interview research analyst."
        ),
        HumanMessage(content=prompt)
    ])

    return response.content


# This variable will contain the initial analysis.
session_summary = perform_initial_analysis()

RETRIEVER_URL = "http://localhost:8001/retrive"

@tool
def retrieve_knowledge(query: str) -> str:
    """
    Retrieve relevant information from the interview transcript
    knowledge base.

    Use this tool for:
    - Specific interview questions
    - Exact quotes
    - Supporting timestamps
    - Detailed transcript questions
    - Comparing interviewees
    - Cross-transcript analysis
    - Evidence-based answers
    """

    response = requests.get(
        RETRIEVER_URL,
        params={
            "query": query
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2
    )


tools = [
    retrieve_knowledge
]


llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """
You are an AI assistant that analyzes interview transcripts.

You have access to two sources of information:

1. INITIAL TRANSCRIPT ANALYSIS
   - Use this for broad questions.
   - Use this to explain overall summaries and common themes.

2. RETRIEVAL TOOL
   - Use this for specific transcript questions.
   - Use this for exact quotes and timestamps.
   - Use this for interview guide questions.
   - Use this for detailed findings.
   - Use this for comparisons between interviews.
   - Use this for evidence-based answers.

Important rules:

- Use the retrieval tool when the user asks for specific evidence.
- Never invent quotes.
- Never invent timestamps.
- Do not claim that a participant said something unless it is supported
  by retrieved transcript evidence.
- Clearly distinguish between common themes and individual opinions.
- When comparing interviews, use retrieved evidence.
- Answer clearly and professionally.
- If the retrieved information is insufficient, say so.
"""

def agent(state: MessagesState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),

        SystemMessage(
            content=f"""
INITIAL TRANSCRIPT ANALYSIS:

{session_summary}

Use this analysis for broad questions.

For exact quotes, timestamps, specific interview questions,
detailed findings, and comparisons, use the retrieve_knowledge tool.
"""
        ),

        *state["messages"]
    ]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


tool_node = ToolNode(tools)

graph_builder = StateGraph(MessagesState)
graph_builder.add_node("agent", agent)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "agent")
graph_builder.add_conditional_edges("agent",tools_condition)
graph_builder.add_edge("tools", "agent")

graph = graph_builder.compile()

if __name__ == "__main__":
    
    print("=" * 70)
    print("INITIAL TRANSCRIPT ANALYSIS")
    print("=" * 70)
    print(session_summary)
    print("=" * 70)
    print("\nChatbot is ready.")
    print("Type 'exit' or 'quit' to stop.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        result = graph.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            }
        )
        print("\nAgent:")
        print(result["messages"][-1].content)
        print()