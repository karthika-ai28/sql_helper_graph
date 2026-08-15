# Mental Wellness Practice Suggester - Learn LangGraph Step by Step

A beginner-friendly LangGraph project that suggests personalized calming
practices based on how a user is feeling.

The project demonstrates a clear LangGraph pattern:

```text
[User Feeling]
      |
      v
understand_mood
      |
      +--> suggest_breathing ----+
      +--> suggest_mindfulness --+--> pick_best_practice
      +--> suggest_movement -----+          |
                                         conditional
                                      /              \
                              quick_practice     deep_practice
                                      |              |
                                     END            END
```

---

## What This Project Does

A user enters a feeling such as:

- `I feel stressed before my exam`
- `I cannot sleep and my mind is racing`
- `I feel anxious and overwhelmed`

The graph then:

1. Understands the user mood.
2. Runs three specialist suggestion nodes in parallel:
   - breathing specialist
   - mindfulness specialist
   - gentle movement specialist
3. Uses a decision node to choose whether the user needs:
   - a quick practice under 5 minutes, or
   - a deeper 10-15 minute session
4. Routes to the correct final node.
5. Prints the personalized wellness practice and message log.

---

## LangGraph Concepts Covered

| Concept | Where It Appears |
|---|---|
| State | `WellnessState` Pydantic model |
| Nodes | `understand_mood`, `suggest_breathing`, `suggest_mindfulness`, `suggest_movement`, `pick_best_practice`, `quick_practice`, `deep_practice` |
| Parallel execution | Three suggestion nodes run after `understand_mood` |
| Fan-in | All three specialist suggestions flow into `pick_best_practice` |
| Conditional edges | `route_after_decision` sends the graph to quick or deep practice |
| Final output | `quick_practice` or `deep_practice` |
| Message accumulation | `messages: Annotated[list, operator.add]` |

---

## Project Files

```text
mental_wellness_graph.py   Main LangGraph project
architecture.md            Architecture explanation
architecture.drawio        Diagram source file
requirements.txt           Python dependencies
.env.example               Example environment file
.gitignore                 Ignored local files
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
python mental_wellness_graph.py
```

---

## Expected Flow

Example input:

```text
I feel anxious and overwhelmed because I have too much work.
```

The graph will:

1. Acknowledge the feeling.
2. Generate a breathing technique.
3. Generate a mindfulness or grounding exercise.
4. Generate a gentle movement suggestion.
5. Decide whether the user needs a quick or deeper practice.
6. Print the final personalized practice.
7. Print the message log showing which nodes executed.

---

## Code Walkthrough

| Step | What Happens | File |
|---|---|---|
| 1 | Define `WellnessState` | `mental_wellness_graph.py` |
| 2 | Initialize `ChatOpenAI` | `mental_wellness_graph.py` |
| 3 | Define graph node functions | `mental_wellness_graph.py` |
| 4 | Define `route_after_decision` | `mental_wellness_graph.py` |
| 5 | Add nodes and edges to `StateGraph` | `mental_wellness_graph.py` |
| 6 | Compile graph as `app` | `mental_wellness_graph.py` |
| 7 | Run with `run_wellness_check()` | `mental_wellness_graph.py` |

---

## Important Note

This is a learning project, not a medical or therapy tool. The output is meant
for general wellness practice suggestions only. For crisis situations, medical
concerns, self-harm thoughts, or severe distress, users should contact local
emergency services or a qualified mental health professional.

---

## Key Takeaways

1. State holds the data that travels through the graph.
2. Nodes are normal Python functions that read state and return updates.
3. Parallel execution happens when one node connects to multiple next nodes.
4. Fan-in happens when multiple nodes connect into one later node.
5. Conditional edges let the graph choose the next path at runtime.
