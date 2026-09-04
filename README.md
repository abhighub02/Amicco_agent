# Business Insights Agent

A virtual analyst for a Business Unit head at an automotive spare parts
distributor. It reads the raw order extract, computes the business metrics
once, and lets the BU head ask questions in plain English — or just read the
morning brief and get on with their day.

**The product is the morning brief.** Chat is the follow-up mechanism.

---

## Quick start

```bash
cd project

python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS / Linux

pip install -r requirements.txt

python src/preprocess.py          # build the clean fact table
streamlit run app.py              # open the app
```

The app runs **without an API key**. All metrics, the priority list and the
morning brief are computed in pandas and narrated deterministically.

To enable conversational answers, create a `.env` file in `project/`:

```
GEMINI_API_KEY=...          # primary (see config.LLM_PROVIDER)
ANTHROPIC_API_KEY=sk-ant-...  # optional, for the Claude path
```

Then restart the app. The sidebar shows which provider and mode you are in.

**Switching provider** is one line in `src/config.py`:

```python
LLM_PROVIDER = "gemini"     # or "anthropic"
```

Both implementations are live in `agent.py` rather than commented out.
Gemini is primary only because the Anthropic account currently has no
credits; flip the string when it does.

---

## Running the pieces on their own

Each module runs standalone and prints a readable report:

```bash
python src/preprocess.py       # cleaning + data quality report
python src/insights.py         # every computed metric
python src/priority_flag.py    # P1/P2/P3 assignment + today's call list
python src/narrator.py         # the morning brief, and all findings ranked
python src/build_prompt.py     # the exact system prompt sent to Claude
python src/make_samples.py     # regenerates outputs/SAMPLE_INSIGHTS.md

python src/agent.py --brief                      # brief to stdout
python src/agent.py "why did conversion fall?"   # one-shot question
python src/agent.py                              # interactive REPL
```

---

## What is in here

```
project/
├── data/Raw_Data.xlsx
├── src/
│   ├── config.py          every threshold and business rule, in one place
│   ├── preprocess.py      load, clean, derive outcome flags
│   ├── insights.py        all metrics — the trust boundary
│   ├── priority_flag.py   P1/P2/P3 logic and scoring
│   ├── narrator.py        deterministic plain-English findings
│   ├── build_prompt.py    assembles the system prompt + brief request
│   ├── agent.py           Claude client, conversation state, offline fallback
│   └── make_samples.py    regenerates the sample insights document
├── app.py                 Streamlit UI
├── outputs/               generated: clean data, prompt, flags, samples
├── WRITEUP.md             approach, assumptions, and why
└── requirements.txt
```

## Documents

| File | What it is |
|---|---|
| `WRITEUP.md` | Approach, key assumptions, design rationale |
| `SAMPLE_INSIGHTS.md` | Sample of the insights produced, plus the priority flag output |
| `outputs/system_prompt.txt` | Exactly what Claude is given on every message |
| `outputs/priority_flags.csv` | Every customer with priority, reason and score |

---

## The four tabs

- **Morning brief** — yesterday against a normal day, the findings that
  matter, and who to call. The landing view.
- **Ask a question** — chat, with every customer mentioned tagged by priority.
- **Priority list** — full P1 / P2 / P3 breakdown, downloadable as CSV.
- **The numbers** — every figure the agent is allowed to use, including the
  exact system prompt. Nothing is hidden from the user.

---

## Architecture in one line

Metrics are computed **once, in pandas**, and passed to the model as a
pre-built briefing. The model chooses what to say and how to say it; it never
calculates. Any number in any answer traces back to a line in `insights.py`.

See `WRITEUP.md` for why.
