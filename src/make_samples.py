"""
make_samples.py
---------------
Regenerates SAMPLE_INSIGHTS.md -- the "sample of the insights it produces"
deliverable.

Two kinds of content, deliberately kept separate:

  * What the AGENT SAYS  -- real LLM output, generated live at run time.
  * What the AGENT KNOWS -- the deterministic tables behind every claim.

Putting them in the same document is the point. A reader can take any number
from the prose and find it in the tables below, which is the whole argument
for computing metrics in pandas and letting the model only write sentences.

Nothing in this file is hand-typed. Run it again and every figure updates.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
from insights import build_all
from priority_flag import assign_priority, priority_summary
from build_prompt import build_system_prompt, build_morning_brief_request, rupees
from narrator import morning_brief, generate_findings
from agent import BusinessInsightsAgent

QUESTIONS = [
    "How has conversion changed over the last couple of months, and why?",
    "Which customers are new, growing, or slipping away?",
    "Which product category is declining?",
    "How is Gurgaon performing versus Noida?",
    "Which customers should I call today?",
]

# A follow-up chain, run in one conversation, to show that context carries.
FOLLOW_UP = [
    "What happened to Battery conversion?",
    "Is that the same customers ordering, or new ones?",
    "Put the Battery problem in one line I can forward to my ops head.",
]


def _fresh_agent(prompt, I, flags):
    # Free-tier request-per-minute limits are easy to trip when generating a
    # whole document in one go. Pace the calls rather than rely on retries.
    time.sleep(C.SAMPLE_CALL_DELAY)
    return BusinessInsightsAgent(prompt, insights=I, flags=flags)


def main() -> Path:
    I = build_all()
    flags = assign_priority(I)
    psum = priority_summary(flags)
    prompt = build_system_prompt(I, flags)

    probe = _fresh_agent(prompt, I, flags)
    live = probe.mode == "live"
    engine = f"{probe.model} ({probe.provider})" if live else "deterministic narrator"

    L: list[str] = []
    add = L.append

    add("# Sample Insights\n")
    add(f"Generated from `Raw_Data.xlsx`, data to **{I['as_of']:%d %B %Y}** "
        f"({I['row_count']:,} enquiry lines, {len(flags)} customers).  ")
    add(f"Answers written by **{engine}**. Every figure it quotes was computed "
        "in `insights.py` and appears in the tables in section 5 - the model "
        "does no arithmetic of its own.\n")
    if not live:
        add("> No API key was available when this was generated, so the "
            "answers below come from the deterministic fallback rather than "
            "an LLM.\n")
    add("---\n")

    # 1 -----------------------------------------------------------------
    add("## 1. The morning brief\n")
    add("What lands in front of the BU head each morning.\n")
    if live:
        add(_fresh_agent(prompt, I, flags).brief(build_morning_brief_request(I)))
    else:
        add(morning_brief(I, flags))
    add("\n---\n")

    # 2 -----------------------------------------------------------------
    add("## 2. Questions a BU head actually asks\n")
    add("Each answered in a fresh conversation, verbatim, no editing.\n")
    for q in QUESTIONS:
        add(f"### *\"{q}\"*\n")
        add(_fresh_agent(prompt, I, flags).ask(q))
        add("")
    add("---\n")

    # 3 -----------------------------------------------------------------
    add("## 3. A follow-up conversation\n")
    add("One continuous chat, to show that context carries between turns - "
        "the reason this is a conversation and not a dashboard.\n")
    chat = _fresh_agent(prompt, I, flags)
    for i, q in enumerate(FOLLOW_UP, 1):
        add(f"**Q{i}. {q}**\n")
        add(chat.ask(q))
        add("")
    if live:
        add(f"*{chat.usage_summary()}*\n")
    add("---\n")

    # 4 -----------------------------------------------------------------
    add("## 4. Everything the agent can surface, ranked\n")
    add("Findings are scored so the brief leads with what matters rather than "
        "reciting metrics in schema order.\n")
    for f in generate_findings(I, flags):
        add(f"- **[{f.severity:.0f}]** {f.headline} {f.detail}")
        if f.action:
            add(f"  - *Action:* {f.action}")
    add("\n---\n")

    # 5 -----------------------------------------------------------------
    add("## 5. The numbers behind every answer\n")
    add("The audit trail. Any figure quoted above can be checked here.\n")

    add("### Conversion by business unit\n")
    add(I["conversion"]["by_business_unit"].to_markdown(index=False))

    add("\n### Why conversion moved - last 30 days vs previous 30\n")
    add("Rate effect = the same segment converting differently. "
        "Mix effect = volume shifting between segments. "
        "They sum exactly to the total change - no residual.\n")
    add(I["drivers_by_bu"].to_markdown(index=False))
    add("")
    add(I["drivers_by_category"].to_markdown(index=False))

    add("\n### Product category\n")
    cat = I["category_performance"].copy()
    cat["Revenue"] = cat["Revenue"].map(rupees)
    cat["Enquiry_Value"] = cat["Enquiry_Value"].map(rupees)
    add(cat.to_markdown(index=False))

    add("\n### Delivery speed by business unit\n")
    add(I["delivery_speed"]["by_business_unit"].to_markdown(index=False))

    add("\n### Weekly trend\n")
    tr = I["revenue_trend"].copy()
    tr["Week Of"] = tr["Enquiry Week"].dt.strftime("%d %b")
    tr["Revenue"] = tr["Revenue"].map(rupees)
    add(tr[["Week Of", "Enquiries", "Delivered", "Conversion %",
            "Revenue", "Complete"]].to_markdown(index=False))
    add("\n`Complete = False` marks a week not yet fully observed. The agent "
        "is instructed never to report it as a decline.\n")

    add("### Where the lost enquiries go\n")
    lb = I["conversion"]["loss_breakdown"]
    add(pd.DataFrame([
        {"Outcome": "Never quoted (no price ever given)",
         "Lines": lb["never_quoted"], "% of enquiries": lb["never_quoted_pct_of_all"]},
        {"Outcome": "Quoted but lost",
         "Lines": lb["quoted_but_lost"], "% of enquiries": lb["quoted_but_lost_pct_of_all"]},
        {"Outcome": "Returned", "Lines": lb["returned"], "% of enquiries": None},
        {"Outcome": "Still in progress", "Lines": lb["in_progress"], "% of enquiries": None},
    ]).to_markdown(index=False))

    add("\n### Customer lifecycle\n")
    lc = pd.DataFrame(sorted(I["lifecycle_counts"].items(), key=lambda x: -x[1]),
                      columns=["Lifecycle", "Customers"])
    add(lc.to_markdown(index=False))

    add("\n### Channel\n")
    add(I["channel_split"].to_markdown(index=False))
    add("\n---\n")

    # 6 -----------------------------------------------------------------
    add("## 6. Sales Priority Flag\n")
    add(f"**P1** {psum['counts']['P1']} customers "
        f"({rupees(psum['revenue_at_stake']['P1'])}, "
        f"{psum['p1_revenue_share_pct']}% of delivered revenue) &nbsp;|&nbsp; "
        f"**P2** {psum['counts']['P2']} &nbsp;|&nbsp; "
        f"**P3** {psum['counts']['P3']}\n")
    add(f"The call list is capped at {psum['call_list_size']}; "
        f"{psum['p1_overflow']} further P1 customers are queued behind it. "
        "A priority list that does not fit in a morning is a report, not a "
        "priority list.\n")

    streak = flags["Consecutive NDs"] >= C.CHURN_STREAK_WATCH
    gave_up = flags[streak & flags["Is Silent"]]
    opsq = flags[streak & ~flags["Is Silent"]]

    add("### The two lanes\n")
    add("A run of undelivered orders is a broken promise, not automatically a "
        "lost customer. Which one it is depends on whether they are still "
        "calling us.\n")
    add("| Lane | Customers | Revenue | Owner | What to do |")
    add("|---|---|---|---|---|")
    add(f"| Undelivered streak, **then silence** | {len(gave_up)} | "
        f"{rupees(gave_up['Total Revenue'].sum())} | Sales (P1) | "
        "They gave up on us. Call today, the window is closing. |")
    add(f"| Undelivered streak, **still enquiring** | {len(opsq)} | "
        f"{rupees(opsq['Total Revenue'].sum())} | Amicco (P2) | "
        "Operations problem. Fix sourcing before they go quiet. |")

    add("\n### Customers who gave up on us - the defining P1\n")
    add("Silence is measured against each customer's own ordering rhythm, "
        "not a flat number of days.\n")
    gu = gave_up.head(12).copy()
    gu["Total Revenue"] = gu["Total Revenue"].map(rupees)
    add(gu[["Customer Name", "Business Unit", "Value Tier", "Total Revenue",
            "Consecutive NDs", "Days Since Last Order", "Median Order Gap"]]
        .rename(columns={"Total Revenue": "Revenue",
                         "Consecutive NDs": "Failed orders",
                         "Days Since Last Order": "Silent (days)",
                         "Median Order Gap": "Normal gap (days)"})
        .to_markdown(index=False))

    add("\n### Today's call list (top P1 by urgency)\n")
    call = flags[flags["On Call List"]].copy()
    call["Total Revenue"] = call["Total Revenue"].map(rupees)
    call["Revenue Change %"] = call["Revenue Change %"].map(
        lambda v: "n/a" if v is None or pd.isna(v) else f"{v:.0f}%")
    add(call[["Customer Name", "Business Unit", "Issue Owner", "Value Tier",
              "Total Revenue", "Days Since Last Order", "Consecutive NDs",
              "Revenue Change %", "Priority Score", "Reason"]]
        .rename(columns={"Total Revenue": "Revenue",
                         "Days Since Last Order": "Days Quiet",
                         "Consecutive NDs": "ND Streak",
                         "Revenue Change %": "Rev Chg",
                         "Priority Score": "Score"})
        .to_markdown(index=False))

    add("\n### P2 sample (top 10 by urgency)\n")
    p2 = flags[flags["Priority"] == "P2"].head(10).copy()
    p2["Total Revenue"] = p2["Total Revenue"].map(rupees)
    add(p2[["Customer Name", "Business Unit", "Issue Owner", "Total Revenue",
            "Days Since Last Order", "Consecutive NDs", "Reason"]]
        .rename(columns={"Total Revenue": "Revenue",
                         "Days Since Last Order": "Days Quiet",
                         "Consecutive NDs": "ND Streak"})
        .to_markdown(index=False))

    p3 = flags[flags["Priority"] == "P3"]
    add(f"\n### P3\n{len(p3)} customers, {rupees(p3['Total Revenue'].sum())} of "
        "revenue. Reported in aggregate only - never listed individually, "
        "because nothing needs to be done about them.\n")

    out = C.ROOT / "SAMPLE_INSIGHTS.md"
    out.write_text("\n".join(L), encoding="utf-8")
    return out


if __name__ == "__main__":
    p = main()
    print(f"wrote {p}  ({len(p.read_text(encoding='utf-8').splitlines()):,} lines)")
