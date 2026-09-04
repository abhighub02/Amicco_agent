# Business Insights Agent — Approach & Rationale

## The problem as I read it

A BU head does not want a dashboard. They want the answer to *"is my business
OK, and if not, what do I do about it this morning?"* — without waiting on an
analyst.

So the product is a **daily brief**, not a chat toy. The agent's job every
morning is: tell me how yesterday went, tell me the one thing that changed and
why, and tell me who to call. Chat exists for the follow-up question.

That framing drove every decision below.

---

## Architecture: compute once, let the model narrate

```
Raw_Data.xlsx
     ↓  preprocess.py      clean, derive outcome flags, anchor the clock
     ↓  insights.py        ALL arithmetic happens here, once
     ↓  priority_flag.py   P1/P2/P3 + urgency score
     ↓  build_prompt.py    ~2,600-word briefing
     ↓  agent.py           the LLM reads the briefing and writes the answer
     ↓  app.py             Streamlit
```

The provider is a one-line switch (`config.LLM_PROVIDER`). Gemini 3.6 Flash
is primary; the Claude path is fully implemented and stays live in the code
rather than commented out. Nothing above `agent.py` knows or cares which is
running — the briefing and the guardrails are identical either way, which is
the point of keeping all the logic below the model.

**The model never calculates anything.** It is given roughly 200 pre-computed
numbers and told to select, interpret and phrase. Every figure in every answer
traces to a line in `insights.py`.

I considered natural-language-to-pandas instead. I rejected it because the
failure mode is fatal here: a BU head cannot audit generated code, and
"conversion" has at least four defensible definitions in this data (does
`Returned` count? does `Partially Delivered`? line-level or order-level?). A
text-to-SQL agent would answer the same question differently on Tuesday than
on Monday. Fixing definitions in code, once, is what makes the tool
trustworthy — which is the whole point.

The honest cost: questions outside the pre-computed set cannot be answered.
The prompt therefore instructs the model to say *"I don't have that in the
daily figures"* rather than guess. A missing answer is recoverable; a
confidently wrong one is not.

The dataset is small enough that this trade is free — 35k rows, one grain,
fixed schema, and a bounded question space.

---

## What I found in the data before building

Profiling first changed the design substantially. Five findings mattered:

**1. June is a fake month.** The file starts 4 June, but weeks 1–3 contain
1, 1 and 19 rows. Real volume begins **22 June**. A naive agent asked "how did
we grow?" would report *July enquiries up 600% on June*. The analysis window
is hard-cut at 22 June and the pre-window rows are excluded.

**2. The clock must be anchored to the data, not the system.** Data ends
31 Aug 2026; I built this in September. Anchoring "last 30 days" to
`datetime.now()` would silently push every customer toward "Gone Quiet" as the
file ages on disk. Everything is measured back from `AS_OF` = max enquiry date.

**3. `Order Value ≠ Quantity × Unit Price` on ~45% of priced lines.** Ratios
cluster at 1.00, 0.92, 0.90, dropping to 0.48 — an undisclosed discount is
already baked in (median 8%). The brief's own column definition says
otherwise. I trust the supplied `Order Value` and expose the implied discount
as its own metric; recomputing would have overstated revenue.

**4. 6,246 enquiries were never priced at all.** 30% of all `Not Delivered`
lines have no `Unit Price`. That splits the 61% non-conversion into two
completely different businesses problems — **never quoted** (a response-speed
failure, entirely ours, and the cheapest conversion available) versus
**quoted and lost** (price or availability). This became a headline metric.
It is trending the right way: 20.9% → 18.5% → 16.9% across Jun/Jul/Aug.

**5. `Supplier` is leakage, not a lever.** Supplier A converts at 54% against
17.5% for "Unspecified". The tempting conclusion — route more volume to
Supplier A — is wrong: Supplier is stamped *when sourcing succeeds*, so it is
downstream of the outcome. The prompt explicitly forbids the model from
framing it causally, and reframes "Unspecified" as a sourcing-failure
diagnostic.

Two smaller ones: conversion is genuinely **line-level** (54% of multi-line
orders are fully lost, 40% fully delivered, 5.6% split), and delivery is
effectively same-day (median 0 days, p95 3 days) — so the right-censoring in
recent days is real but small, handled with a maturity flag rather than
dropped.

---

## Key assumptions

| Assumption | Why |
|---|---|
| Conversion = `Delivered` / all lines | The brief's definition. Returns are tracked separately as a quality signal rather than silently counted as success. |
| Revenue = `Order Value` on delivered lines only | An enquiry is not money. |
| Analysis window starts 22 Jun 2026 | Earlier rows are a partial extract, not slow trading. |
| "Month on month" = trailing 30d vs prior 30d | Calendar months would compare a full August against a June holding nine real days. |
| `AS_OF` = latest enquiry date | Keeps windows stable as the file ages. |
| Enquiries < 3 days old are immature | p95 delivery lag. Reported, not hidden. |
| Streak grain = consecutive **orders** | See below. |
| Silence = >3x the customer's own median order gap (floor 10 days) | A daily customer quiet 10 days is in trouble; a monthly one is not. |

---

## Two decisions I'd defend in the room

**Grain for "consecutive non-deliveries."** At a threshold of 6, line-grain
flags 107 of 330 customers; order-grain flags 60. A P1 list covering a third
of the customer base is not a priority list. Order grain also matches what a
person means by "six in a row", and does not punish a customer for one large
multi-line order falling through. It is switchable in `config.py`, and both
figures are computed so the choice stays auditable.

**Explanations must reconcile.** The "why" behind a conversion move is a
shift-share decomposition into a **rate effect** (the same segment converting
differently) and a **mix effect** (volume moving between segments). My first
implementation used the textbook prior-weighted form, whose parts summed to
+0.17 points against an actual change of −0.1 — it silently dropped the
interaction term. I switched to the current-weighted form, which telescopes to
the exact total, and added an assertion. An explanation whose parts do not add
up to the headline number is worse than no explanation.

---

## The Sales Priority Flag

**Definition.** P1 = act today. P2 = act this week. P3 = monitor only.

**The idea that organises everything: a run of undelivered orders is a broken
promise, not automatically a lost customer.** Which one it is depends entirely
on whether the customer is still calling us — and those are two different
problems with two different owners.

| Situation | Priority | Owner | Why |
|---|---|---|---|
| Undelivered streak, **still enquiring** | **P2** | Amicco | We are failing them and they are *still calling*. That is an operations problem. Sending a salesperson to apologise does not fix a sourcing failure. |
| Undelivered streak, **then silence** | **P1** | Sales | They gave up on us and are buying elsewhere. This is the real churn signal, and it is urgent because the window to win them back is closing. |

On this data that splits cleanly:

- **29 customers (₹5.59 L)** went quiet after we failed them → the sales call list.
- **101 customers (₹94.71 L)** have 3+ undelivered orders but are *still
  enquiring* → an operations queue, not a sales one.

Collapsing those into a single "at risk" number is what makes most churn
reports unactionable — it sends the wrong team at the wrong problem.

**Full rules**

| | Trigger |
|---|---|
| **P1** | 3+ consecutive undelivered orders **then silence** · High-value + quiet 30+ days · High-value + revenue down >50% MoM |
| **P2** | 3+ consecutive undelivered orders **but still enquiring** · Mid-value + quiet 20+ days · returns >20% of last month's lines |
| **P3** | Everything else |

**Three design choices worth naming:**

*Silence is relative, not absolute.* It is measured against each customer's
own median order gap (3× their rhythm, floor 10 days). Workshop 0186 normally
orders **every day** — 15 days of silence is an emergency. A monthly customer
at 15 days is fine. A flat day threshold gets this wrong in both directions.

*Momentum is relative too.* A customer down 60% on ₹2L is a bigger emergency
than one down 5% on ₹5L. Ranking by absolute size just reprints the
top-customer list every week until the sales team stops reading it.

*P1 and P2 signals are scored in separate buckets.* Ranking a P1 on a total
that included its P2 points let a merely-noisy customer outrank a genuinely
lost one. P1s are ranked on P1 evidence; P2 points only break ties. The list
is then capped at 25 — a list that does not fit in a morning is a report, not
a priority — with the overflow stated openly.

**Example output** — the top of today's call list:

| Customer | BU | Revenue | Failed orders | Silent | Normal gap | Why |
|---|---|---|---|---|---|---|
| Workshop 0186 | Tier II Cities | ₹3.73 L | 4 | 15 days | **1 day** | Gave up after 4 undelivered orders |
| Workshop 0142 | Gurgaon | ₹9.8k | 11 | 30 days | 2 days | Gave up after 11 undelivered orders |
| Workshop 0213 | Tyre Segment | ₹79.3k | 0 | 40 days | — | Top-tier, silent 40 days, revenue down 100% |

Workshop 0186 is the case that justifies the whole exercise: a high-value
account that ordered *every single day*, hit four undelivered orders, and has
now been silent for fifteen. No revenue-sorted dashboard surfaces that, and by
the time it shows up in a monthly report they are gone.

The contrast case is **Workshop 0098** — ₹8.76 L, twelve consecutive
undelivered orders, and they enquired *today*. Under a naive rule that is the
loudest P1 on the board. Here it is correctly **P2 / Amicco**: we have not
lost them, we are failing them, and the fix is sourcing rather than a phone
call.

Full output in `SAMPLE_INSIGHTS.md` and `outputs/priority_flags.csv`.

---

## Known limitations

- **Bounded question space.** Outside the pre-computed metrics the agent
  declines rather than guesses. A tool-calling layer over the metric functions
  is the natural next step.
- **Three months of data.** Enough for month-on-month, not enough for
  seasonality. "Gone Quiet at 30 days" is a reasonable default, not a
  calibrated figure — with a year of data I would derive it per segment from
  observed reorder gaps.
- **Small-base segments.** Retail (148 lines) and Tyre (143) swing wildly.
  Findings are volume-gated, but the caution belongs with the reader too.
- **Causal language.** The rate/mix split is arithmetic, not causation. The
  agent is instructed not to speculate past it.
- **No write-back.** Priorities are computed, not recorded. There is no
  feedback loop on whether calling a P1 customer actually worked — that is the
  single highest-value thing to add next.
