"""
make_samples.py
---------------
Regenerates outputs/SAMPLE_INSIGHTS.md -- the "sample of the insights it
produces" deliverable. Every figure in it is computed at run time; nothing is
typed by hand.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
from insights import build_all
from priority_flag import assign_priority, priority_summary
from build_prompt import rupees
from narrator import morning_brief, generate_findings, answer_offline

QUESTIONS = [
    "How has conversion changed over the last couple of months, and why?",
    "Which customers are new, growing, or slipping away?",
    "Where is the business changing by category?",
    "How is delivery performance across regions?",
    "Who should my team call today?",
]


def main() -> Path:
    I = build_all()
    flags = assign_priority(I)
    psum = priority_summary(flags)

    L: list[str] = []
    add = L.append

    add("# Sample Insights\n")
    add(f"Generated from `Raw_Data.xlsx` on data up to **{I['as_of']:%d %B %Y}** "
        f"({I['row_count']:,} enquiry lines, {len(flags)} customers).  ")
    add("Every number below is computed by `insights.py`. Nothing here is "
        "hand-written or model-generated.\n")
    add("---\n")

    # 1 ---------------------------------------------------------------
    add("## 1. The daily morning brief\n")
    add("This is what lands in front of the BU head each morning.\n")
    add(morning_brief(I, flags))
    add("\n---\n")

    # 2 ---------------------------------------------------------------
    add("## 2. Answers to the questions in the brief\n")
    for q in QUESTIONS:
        add(f"### *\"{q}\"*\n")
        a = answer_offline(q, I, flags)
        add(a if a else "_No pre-computed finding matches this question._")
        add("")
    add("---\n")

    # 3 ---------------------------------------------------------------
    add("## 3. Every finding the agent can surface, ranked by severity\n")
    add("The agent leads with what matters rather than reciting metrics in "
        "schema order.\n")
    for f in generate_findings(I, flags):
        add(f"- **[{f.severity:.0f}]** {f.headline} {f.detail}")
        if f.action:
            add(f"  - *Action:* {f.action}")
    add("\n---\n")

    # 4 ---------------------------------------------------------------
    add("## 4. Supporting tables\n")
    add("### Conversion by business unit\n")
    add(I["conversion"]["by_business_unit"].to_markdown(index=False))

    add("\n### Why conversion moved - last 30 days vs previous 30\n")
    add("Rate effect = the same segment converting differently. "
        "Mix effect = volume shifting between segments. "
        "They sum exactly to the total change.\n")
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
    add("\n`Complete = False` marks a week that is not yet fully observed. "
        "The agent is instructed never to report it as a decline.\n")

    add("### Customer lifecycle\n")
    lc = pd.DataFrame(sorted(I["lifecycle_counts"].items(),
                             key=lambda x: -x[1]),
                      columns=["Lifecycle", "Customers"])
    add(lc.to_markdown(index=False))

    add("\n### Channel\n")
    add(I["channel_split"].to_markdown(index=False))
    add("\n---\n")

    # 5 ---------------------------------------------------------------
    add("## 5. Sales Priority Flag - example output\n")
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
    add(p2[["Customer Name", "Business Unit", "Total Revenue",
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
