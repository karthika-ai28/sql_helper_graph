# SQL Helper Graph - Learn LangGraph Step by Step

A beginner-friendly LangGraph project that turns a natural-language data request
into SQL and explains the query.

The project demonstrates a clear LangGraph pattern:

```text
[User Request]
      |
      v
identify_tables
      |
      +--> generate_sql_query ------+
      |                              |
      +--> check_sql_risks ---------+---> decide_query_complexity
                                              |
                                         (conditional)
                                              /          \
                                        simple?      advanced?
                                            |             |
                                     simple_sql_response  advanced_sql_response
                                            |                     |
                                           END                   END
```

---

## What This Project Does

A user describes the data they need, for example:

- `Show me the top 10 customers by revenue in the last quarter.`
- `Find all orders placed in March with customer details.`
- `List active users who logged in more than 5 times this month.`

The graph then:

1. Infers likely tables and relevant fields.
2. Generates a clean SQL query.
3. Reviews the query for missing filters, joins, and assumptions.
4. Decides whether the query is simple or advanced.
5. Produces the final SQL answer and explanation.

---

## LangGraph Concepts Covered

| Concept | Where It Appears |
|---|---|
| State | `SQLState` Pydantic model |
| Nodes | `identify_tables`, `generate_sql_query`, `check_sql_risks`, `decide_query_complexity`, `simple_sql_response`, `advanced_sql_response` |
| Fan-in | `generate_sql_query` and `check_sql_risks` both flow into `decide_query_complexity` |
| Conditional edges | `route_after_decision` sends the graph to simple or advanced output |
| Final output | `simple_sql_response` or `advanced_sql_response` |
| Message accumulation | `messages: Annotated[list, operator.add]` |

---

## Project Files

```text
sql_helper_graph.py       Main LangGraph project
README.md                 Project overview and setup
requirements.txt          Python dependencies
architecture.md           Architecture explanation
architecture.drawio       Diagram source file
.env.example              Example environment file
.gitignore                Ignored local files
```

---

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure your OpenAI API key

```powershell
copy .env.example .env
```

Edit `.env` and add your API key:

```text
OPENAI_API_KEY=sk-...
```

Never commit your real `.env` file.

### 4. Run the project

```powershell
python sql_helper_graph.py
```

---

## Expected Flow

Example input:

```text
Show me the total revenue by customer for the last 6 months.
```

The graph will:

1. Infer likely tables such as `customers` or `orders`.
2. Generate a SQL query for the request.
3. Review the query for missing date filters, joins, or assumptions.
4. Decide if the query is simple or advanced.
5. Print the SQL and the explanation for the chosen response path.
6. Print the message log showing which nodes executed.

---

## Code Walkthrough

| Step | What Happens | File |
|---|---|---|
| 1 | Define `SQLState` | `sql_helper_graph.py` |
| 2 | Initialize `ChatOpenAI` | `sql_helper_graph.py` |
| 3 | Define specialist nodes | `sql_helper_graph.py` |
| 4 | Define `route_after_decision` | `sql_helper_graph.py` |
| 5 | Add nodes and edges to `StateGraph` | `sql_helper_graph.py` |
| 6 | Compile graph as `app` | `sql_helper_graph.py` |
| 7 | Run with `run_sql_helper()` | `sql_helper_graph.py` |

---

## Important Note

This project is a learning example for SQL generation and explanation. It is not
connected to a real database by default and should be treated as a prompt-based
workflow for learning LangGraph and LLM-driven query generation.

---

## Key Takeaways

1. State holds the data that travels through the graph.
2. Nodes are normal Python functions that read state and return updates.
3. Specialist nodes create a clean division of responsibility.
4. Fan-in happens when multiple nodes connect into one later node.
5. Conditional edges let the graph choose the next response path at runtime.
