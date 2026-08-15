# =============================================================================
# SQL Helper Graph -- A LangGraph Learning Project
# =============================================================================
#
# This project teaches you how LangGraph works by building a SQL assistant that
# transforms a natural-language request into SQL and explains the result.
#
# WHAT THIS DOES:
# A user describes the data they need. The graph identifies likely tables and
# fields, writes a SQL query, checks for missing filters or joins, decides if
# the query is simple or advanced, and then returns the final SQL explanation.
#
# LANGGRAPH CONCEPTS COVERED:
# 1. State Management (Pydantic) -- request flows across specialist nodes
# 2. Nodes -- each function does one job
# 3. Parallel Execution -- generation and risk-check run together
# 4. Fan-in -- both specialist outputs feed the decision node
# 5. Conditional Edges -- route to simple or advanced final output
# 6. Graph Compilation -- convert the graph to an executable app
#
# GRAPH STRUCTURE:
#
#   START
#     |
#   identify_tables
#     |
#     +---> generate_sql_query ------+
#     |                              |
#     +---> check_sql_risks ---------+---> decide_query_complexity
#                                              |
#                                         (conditional)
#                                              /          \
#                                        simple?      advanced?
#                                            |             |
#                                     simple_sql_response  advanced_sql_response
#                                            |                     |
#                                           END                   END
#
# HOW TO RUN:
#   python sql_helper_graph.py
#
# DEPENDENCIES (same as requirements.txt):
#   langgraph, langchain-openai, python-dotenv, pydantic
#
# =============================================================================

import json
import operator
import sys
from typing import Annotated

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()


class SQLState(BaseModel):
    user_request: str = ""
    likely_tables: str = ""
    generated_query: str = ""
    risk_assessment: str = ""
    is_advanced_query: bool = False
    complexity_reason: str = ""
    final_sql_response: str = ""
    messages: Annotated[list, operator.add] = []


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def normalize_response(value):
    if isinstance(value, str):
        return value
    return json.dumps(value)


def identify_tables(state: SQLState) -> dict:
    response = llm.invoke(
        "You are a SQL schema analyst. "
        f"Here is the user's request: '{state.user_request}'. "
        "Infer the most likely tables and relevant fields. "
        "Mention only the tables and columns you would reasonably use, and do not invent unrelated data. "
        "Keep it concise but specific."
    )
    content = normalize_response(response.content)
    return {
        "likely_tables": content,
        "messages": [f"[identify_tables] {content}"]
    }


def generate_sql_query(state: SQLState) -> dict:
    response = llm.invoke(
        "You are a SQL expert. "
        f"The user wants: '{state.user_request}'. "
        f"These are the likely tables and fields: {state.likely_tables}. "
        "Write a clean SQL query that answers the request. "
        "Use standard SQL syntax and keep it readable. "
        "Do not add extra explanation inside the query."
    )
    content = normalize_response(response.content)
    return {
        "generated_query": content,
        "messages": [f"[generate_sql_query] Generated SQL query"]
    }


def check_sql_risks(state: SQLState) -> dict:
    response = llm.invoke(
        "You are a SQL risk reviewer. "
        f"The user wants: '{state.user_request}'. "
        f"This is the generated query: {state.generated_query}. "
        "Check for missing filters, missing joins, ambiguous assumptions, and risky fields. "
        "Point out the main areas that should be validated before running the query. "
        "Keep it short but helpful."
    )
    content = normalize_response(response.content)
    return {
        "risk_assessment": content,
        "messages": [f"[check_sql_risks] {content}"]
    }


def decide_query_complexity(state: SQLState) -> dict:
    response = llm.invoke(
        "You are a SQL complexity classifier. "
        f"The user needs: '{state.user_request}'.\n\n"
        f"Likely tables: {state.likely_tables}\n\n"
        f"SQL query: {state.generated_query}\n\n"
        f"Risk review: {state.risk_assessment}\n\n"
        "Decide whether this is a SIMPLE query or an ADVANCED query. "
        "Reply strictly in JSON format with this exact structure: "
        '{"is_advanced_query": true/false, "reason": "one sentence explanation"}'
    )
    content = normalize_response(response.content)

    try:
        result = json.loads(content)
        is_advanced_query = bool(result.get("is_advanced_query", False))
        reason = result.get("reason", "Defaulted to simple query.")
    except (TypeError, ValueError, json.JSONDecodeError):
        is_advanced_query = False
        reason = "Could not parse the decision, defaulting to a simple query."

    return {
        "is_advanced_query": is_advanced_query,
        "complexity_reason": reason,
        "messages": [f"[decide_query_complexity] advanced={is_advanced_query}"]
    }


def simple_sql_response(state: SQLState) -> dict:
    response = llm.invoke(
        "You are a helpful SQL teacher. "
        f"Explain this query in a simple way for a non-expert:\n\n"
        f"SQL query:\n{state.generated_query}\n\n"
        f"Risk check:\n{state.risk_assessment}\n\n"
        "Explain what the query is doing, which fields are selected, and why the filters matter. "
        "Keep it clear and beginner-friendly."
    )
    explanation = normalize_response(response.content)

    return {
        "final_sql_response": (
            "SIMPLE SQL QUERY\n"
            f"{'=' * 45}\n"
            f"SQL:\n{state.generated_query}\n\n"
            f"Explanation:\n{explanation}\n\n"
            f"Why this is simple:\n{state.complexity_reason}"
        ),
        "messages": ["[simple_sql_response] Generated simple response"]
    }


def advanced_sql_response(state: SQLState) -> dict:
    response = llm.invoke(
        "You are an advanced SQL analyst. "
        f"Explain this complex query in detail:\n\n"
        f"SQL query:\n{state.generated_query}\n\n"
        f"Risk check:\n{state.risk_assessment}\n\n"
        "Describe joins, filters, aggregation, edge cases, and the business logic behind the query. "
        "Keep it informative and precise."
    )
    explanation = normalize_response(response.content)

    return {
        "final_sql_response": (
            "ADVANCED SQL QUERY\n"
            f"{'=' * 45}\n"
            f"SQL:\n{state.generated_query}\n\n"
            f"Explanation:\n{explanation}\n\n"
            f"Why this is advanced:\n{state.complexity_reason}"
        ),
        "messages": ["[advanced_sql_response] Generated advanced response"]
    }


def route_after_decision(state: SQLState) -> str:
    if state.is_advanced_query:
        return "advanced"
    else:
        return "simple"


graph = StateGraph(SQLState)

graph.add_node("identify_tables", identify_tables)
graph.add_node("generate_sql_query", generate_sql_query)
graph.add_node("check_sql_risks", check_sql_risks)
graph.add_node("decide_query_complexity", decide_query_complexity)
graph.add_node("simple_sql_response", simple_sql_response)
graph.add_node("advanced_sql_response", advanced_sql_response)

graph.add_edge(START, "identify_tables")
graph.add_edge("identify_tables", "generate_sql_query")
graph.add_edge("identify_tables", "check_sql_risks")
graph.add_edge("generate_sql_query", "decide_query_complexity")
graph.add_edge("check_sql_risks", "decide_query_complexity")

graph.add_conditional_edges(
    "decide_query_complexity",
    route_after_decision,
    {
        "simple": "simple_sql_response",
        "advanced": "advanced_sql_response",
    }
)

graph.add_edge("simple_sql_response", END)
graph.add_edge("advanced_sql_response", END)

app = graph.compile()


def run_sql_helper(user_request: str):
    print("=" * 60)
    print("  SQL HELPER GRAPH")
    print(f"  User request: \"{user_request}\"")
    print("=" * 60)

    result = app.invoke({
        "user_request": user_request,
        "messages": [],
    })

    print("\n" + "=" * 60)
    print("  FINAL SQL RESPONSE")
    print("=" * 60)
    print(f"\n{result['final_sql_response']}")

    print("\n" + "-" * 60)
    print("  MESSAGE LOG")
    print("-" * 60)
    for msg in result["messages"]:
        print(f"  {msg}")

    return result


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  SQL HELPER GRAPH")
    print("=" * 60)
    print("\n  Describe the data you need and I'll turn it into SQL.")
    print("  Type 'quit' to exit.\n")

    while True:
        user_request = input("  Describe the data you need > ").strip()

        if user_request.lower() in ("quit", "exit", "q"):
            print("\n  Goodbye!\n")
            break

        if not user_request:
            continue

        run_sql_helper(user_request)
        print("\n")
