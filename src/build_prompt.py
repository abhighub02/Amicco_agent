"""
build_prompt.py
---------------
Turns the computed metrics into the system prompt that is sent to Claude on
every message, plus the standalone morning brief.

WHY A PRE-BUILT PROMPT RATHER THAN LIVE QUERYING
The whole dataset is 35,000 rows, but the *decisions* a BU head makes rest on
maybe 200 numbers. Those fit comfortably in a system prompt. Pre-computing
them means:
  * every answer in every session uses identical definitions;
  * the model never does arithmetic, so it cannot invent a figure;
  * responses are one API call -- fast enough to feel like a conversation;
  * the agent works with no database and no query layer to secure.

The trade-off is honest and worth stating: questions outside the pre-computed
set cannot be answered. The prompt therefore instructs the model to say so
plainly rather than guess. A confident wrong answer would destroy the trust
this tool depends on.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
from insights import build_all
from priority_flag import assign_priority, priority_summary


# --------------------------------------------------------------- formatting
def rupees(x) -> str:
    """Indian business shorthand -- a BU head reads Cr/L, not 8 digits."""
    if x is None or pd.isna(x):
        return "n/a"
    x = float(x)
    if abs(x) >= 1e7:
        return f"Rs {x / 1e7:.2f} Cr"
    if abs(x) >= 1e5:
        return f"Rs {x / 1e5:.2f} L"
    if abs(x) >= 1e3:
        return f"Rs {x / 1e3:.1f}k"
    return f"Rs {x:.0f}"


def signed(x, unit="%") -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{x:+.1f}{unit}"


def _presentable(df: pd.DataFrame) -> pd.DataFrame:
    """
    Round and humanise numbers BEFORE they enter the prompt. The model repeats
    what it is shown -- feed it -100.000000 and that is what the BU head reads.
    """
    d = df.copy()
    if "Total Revenue" in d:
        d["Total Revenue"] = d["Total Revenue"].map(rupees)
    for col in ("Revenue Change %", "Return Rate 30d %", "Conversion %"):
        if col in d:
            d[col] = d[col].map(lambda v: "n/a" if v is None or pd.isna(v) else f"{v:.0f}%")
    for col in ("Days Since Last Order", "Consecutive NDs", "Orders"):
        if col in d:
            d[col] = d[col].astype(int)
    return d


def _table(df: pd.DataFrame, cols: list, rename: dict = None) -> str:
    d = df[[c for c in cols if c in df.columns]].copy()
    if rename:
        d = d.rename(columns=rename)
    return d.to_string(index=False)


# --------------------------------------------------------------- sections
def _section_context(I: dict) -> str:
    return (
        "## WHAT YOU ARE\n"
        "You are a smart business analyst AND a helpful assistant for an "
        "automotive spare parts distributor selling spares, batteries, paint "
        "and engine oil to workshops and garages. You have deep knowledge of "
        "this business from the data below. You report to a Business Unit head "
        "who is commercially sharp but not technical.\n\n"
        "Answer any question the BU head asks - data questions with precision, "
        "strategy questions with judgement, and anything else helpfully. Never "
        "refuse a question. Every number listed below is already correct; you "
        "never need to recalculate one.\n\n"
        f"Data covers {I['window_start']:%d %b %Y} to {I['as_of']:%d %b %Y} "
        f"({I['row_count']:,} enquiry lines). Treat "
        f"{I['as_of']:%d %B %Y} as today.\n"
    )


def _section_definitions() -> str:
    return (
        "\n## DEFINITIONS (use these exactly)\n"
        "- Enquiry: one line item on an order -- a customer asking for one part.\n"
        "- Conversion: enquiry lines with status Delivered, divided by all lines.\n"
        "- Revenue: Order Value on delivered lines only. An enquiry is not money.\n"
        "- Never quoted: the enquiry has no price at all. We never responded. "
        "This is a response-speed failure and is fixable.\n"
        "- Quoted but lost: we priced it and still lost it. Price or availability.\n"
        f"- Consecutive non-deliveries: orders in a row where nothing shipped.\n"
        "\n"
        "IMPORTANT - the two lanes. A run of undelivered orders is a broken\n"
        "promise, not automatically a lost customer. Which it is depends on\n"
        "whether the customer is still calling us:\n"
        f"  * Streak of {C.CHURN_STREAK_WATCH}+ AND still enquiring -> P2, owned by\n"
        "    Amicco. An operations problem. The fix is sourcing and delivery,\n"
        "    not a sales call. They have not left yet.\n"
        f"  * Streak of {C.CHURN_STREAK_WATCH}+ AND then silence -> P1, owned by\n"
        "    Sales. They gave up on us and are buying elsewhere. This is the\n"
        "    real churn signal and the most urgent thing on the list.\n"
        "Never describe a customer who is still enquiring as lost or churned,\n"
        "and never send sales after a problem only operations can fix.\n"
        "- Silence is measured against each customer's own ordering rhythm, not\n"
        "  a flat number of days. A workshop that orders daily going quiet for\n"
        "  10 days is in trouble; one that orders monthly is not.\n"
    )


def _section_headline(I: dict) -> str:
    cv, pc = I["conversion"], I["period_comparison"]
    lb = cv["loss_breakdown"]
    d = pc["delta"]
    return (
        "\n## HEADLINE\n"
        f"Conversion {cv['overall']['conversion_pct']}% "
        f"({cv['overall']['delivered']:,} delivered of {cv['overall']['enquiries']:,} enquiries).\n"
        f"Last 30 days ({pc['current_window']}) vs previous 30 ({pc['previous_window']}):\n"
        f"  Enquiries  {pc['current']['enquiries']:,} vs {pc['previous']['enquiries']:,}  "
        f"({signed(d['enquiries_pct'])})\n"
        f"  Revenue    {rupees(pc['current']['revenue'])} vs {rupees(pc['previous']['revenue'])}  "
        f"({signed(d['revenue_pct'])})\n"
        f"  Conversion {pc['current']['conversion_pct']}% vs {pc['previous']['conversion_pct']}%  "
        f"({signed(d['conversion_pts'], ' pts')})\n"
        f"  Active customers {pc['current']['customers']} vs {pc['previous']['customers']}  "
        f"({signed(d['customers_pct'])})\n\n"
        f"Where the {100 - cv['overall']['conversion_pct']:.1f}% we did not convert went:\n"
        f"  Never quoted (no price ever given): {lb['never_quoted']:,} lines "
        f"({lb['never_quoted_pct_of_all']}% of all enquiries)\n"
        f"  Quoted but lost: {lb['quoted_but_lost']:,} lines "
        f"({lb['quoted_but_lost_pct_of_all']}%)\n"
        f"  Returned: {lb['returned']:,}   Still in progress: {lb['in_progress']:,}\n"
    )


def _section_why(I: dict) -> str:
    out = ["\n## WHY CONVERSION MOVED (last 30d vs previous 30d)\n"
           "Rate effect = the same segment converting better or worse.\n"
           "Mix effect  = volume shifting toward or away from strong segments.\n"
           "These add up exactly to the total change -- quote them with confidence.\n"]
    for label, key in (("By business unit", "drivers_by_bu"),
                       ("By product category", "drivers_by_category")):
        d = I[key]
        if not len(d):
            continue
        out.append(f"\n{label}:\n")
        out.append(_table(d, [
            d.columns[0], "Enquiries Prev 30d", "Enquiries Last 30d",
            "Conversion Prev", "Conversion Last",
            "Rate Effect (pts)", "Mix Effect (pts)", "Total Effect (pts)",
        ]))
        out.append("\n")
    return "".join(out)


def _section_priority(flags: pd.DataFrame, psum: dict) -> str:
    call = flags[flags["On Call List"]]
    p2 = flags[flags["Priority"] == "P2"]

    s = [
        "\n## SALES PRIORITY\n"
        f"P1 {psum['counts']['P1']} customers ({rupees(psum['revenue_at_stake']['P1'])} of revenue, "
        f"{psum['p1_revenue_share_pct']}% of the book) | "
        f"P2 {psum['counts']['P2']} | P3 {psum['counts']['P3']}\n"
        f"The call list below is the top {psum['call_list_size']} P1s by urgency; "
        f"{psum['p1_overflow']} further P1 customers are queued behind them. "
        "If asked for more, say the queue exists and give what is listed.\n\n"
        "### P1 -- CALL LIST (act today). Full detail, name these customers.\n"
    ]
    s.append(_table(_presentable(call), [
        "Customer Name", "Business Unit", "Value Tier", "Total Revenue",
        "Days Since Last Order", "Consecutive NDs", "Revenue Change %", "Reason",
    ], {"Total Revenue": "Revenue", "Days Since Last Order": "Days Quiet",
        "Consecutive NDs": "ND Streak", "Revenue Change %": "Rev Chg %"}))

    gave_up = flags[(flags["Consecutive NDs"] >= C.CHURN_STREAK_WATCH)
                    & flags["Is Silent"]]
    ops = flags[(flags["Consecutive NDs"] >= C.CHURN_STREAK_WATCH)
                & ~flags["Is Silent"]]
    s.append(
        f"\n\nLane split: {len(gave_up)} customers "
        f"({rupees(gave_up['Total Revenue'].sum())}) went silent after we failed "
        f"to deliver - these are the sales calls. Separately {len(ops)} customers "
        f"({rupees(ops['Total Revenue'].sum())}) have "
        f"{C.CHURN_STREAK_WATCH}+ undelivered orders but are STILL enquiring - "
        "that is an operations fix, not a sales call.\n"
    )

    s.append(f"\n\n### P2 -- act this week (top 15 of {len(p2)} by urgency)\n")
    s.append(_table(_presentable(p2.head(15)), [
        "Customer Name", "Business Unit", "Total Revenue",
        "Days Since Last Order", "Consecutive NDs", "Reason",
    ], {"Total Revenue": "Revenue", "Days Since Last Order": "Days Quiet",
        "Consecutive NDs": "ND Streak"}))

    p3 = flags[flags["Priority"] == "P3"]
    s.append(
        f"\n\n### P3 -- {len(p3)} healthy customers, {rupees(p3['Total Revenue'].sum())} "
        f"of revenue. Monitor only; do not list them individually.\n"
    )
    return "".join(s)


def _section_top_customers(flags: pd.DataFrame, n: int = 12) -> str:
    """
    The biggest accounts by revenue.

    Without this the prompt only ever names customers who are in trouble --
    everyone healthy is aggregated into a P3 count. That made "who are my
    top customers?" unanswerable, even though it is one of the first things
    any BU head asks. The two largest accounts here are both P3.
    """
    top = flags.nlargest(n, "Total Revenue").copy()
    total = flags["Total Revenue"].sum()
    share = 100 * top["Total Revenue"].sum() / total if total else 0
    body = _table(_presentable(top), [
        "Customer Name", "Business Unit", "Total Revenue", "Priority",
        "Lifecycle", "Orders", "Days Since Last Order",
    ], {"Total Revenue": "Revenue", "Days Since Last Order": "Days Since Order"})
    return (
        f"\n## TOP {n} CUSTOMERS BY REVENUE\n"
        f"These {n} are {share:.0f}% of all delivered revenue. Most are healthy "
        "(P3) and need no action - they are listed so you can answer questions "
        "about who the business actually rests on.\n" + body + "\n"
    )


def _section_segments(I: dict) -> str:
    s = ["\n## PERFORMANCE BY SEGMENT\n\nBusiness units:\n"]
    bu = I["business_unit_performance"].copy()
    bu["Revenue"] = bu["Revenue"].map(rupees)
    s.append(_table(bu, ["Business Unit", "Enquiries", "Customers", "Conversion %",
                         "Revenue", "Revenue Share %", "Mean_Delivery_Days"],
                    {"Mean_Delivery_Days": "Avg Days to Deliver"}))

    s.append("\n\nProduct categories:\n")
    cat = I["category_performance"].copy()
    cat["Revenue"] = cat["Revenue"].map(rupees)
    s.append(_table(cat, ["Product Category", "Enquiries", "Conversion %",
                          "Revenue", "Revenue Share %"]))

    s.append("\n\nChannel:\n")
    s.append(_table(I["channel_split"], ["Channel", "Enquiries", "Conversion %",
                                         "Share of Enquiries %"]))

    ds = I["delivery_speed"]
    s.append(
        f"\n\nDelivery speed: overall mean {ds['overall_mean_days']} days, "
        f"median {ds['overall_median_days']:.0f}, 95th percentile {ds['p95_days']:.0f}. "
        "Most deliveries are same-day; the tail is what hurts.\n"
    )
    return "".join(s)


def _section_lifecycle(I: dict) -> str:
    lc = I["lifecycle_counts"]
    cr = I["churn_risk"]["Churn Risk"].value_counts().to_dict()
    total = sum(lc.values())
    parts = ", ".join(f"{k} {v}" for k, v in sorted(lc.items(), key=lambda x: -x[1]))
    return (
        f"\n## CUSTOMER BASE ({total} customers)\n"
        f"Lifecycle: {parts}\n"
        f"Non-delivery streaks: High risk (>={C.CHURN_STREAK_HIGH}) {cr.get('High', 0)}, "
        f"Watch ({C.CHURN_STREAK_WATCH}-{C.CHURN_STREAK_HIGH - 1}) {cr.get('Watch', 0)}, "
        f"Low {cr.get('Low', 0)}\n"
    )


def _section_trend(I: dict) -> str:
    t = I["revenue_trend"].copy()
    t["Revenue"] = t["Revenue"].map(rupees)
    t["Week Of"] = t["Enquiry Week"].dt.strftime("%d %b")
    body = _table(t, ["Week Of", "Enquiries", "Conversion %", "Revenue", "Complete"])
    return ("\n## WEEKLY TREND\n" + body +
            "\n(Complete=False means the week is still partly unobserved -- "
            "never call it a decline.)\n")


def _section_yesterday(I: dict) -> str:
    d = I["daily_snapshot"]
    return (
        f"\n## MOST RECENT DAY -- {d['date']:%A %d %B %Y}\n"
        f"Enquiries {d['enquiries']} vs {d['baseline_enquiries']} typical "
        f"({signed(d['enquiries_vs_baseline_pct'])} vs {d['baseline_label']})\n"
        f"Orders {d['orders']} | Active customers {d['customers']} | "
        f"Delivered {d['delivered']} ({d['conversion_pct']}%)\n"
        f"Revenue {rupees(d['revenue'])} vs {rupees(d['baseline_revenue'])} typical "
        f"({signed(d['revenue_vs_baseline_pct'])})\n"
        f"Caveat: {d['caveat']}\n"
    )


def _section_rules() -> str:
    return (
        "\n## HOW TO ANSWER\n"
        "1. Lead with the answer immediately. No preamble.\n"
        "2. If the question is about specific numbers (revenue, conversion, "
        "customers, delivery) -- use ONLY the figures given above. Never "
        "invent a number. If a figure genuinely is not above, say which one "
        "is missing and give the closest one you do have.\n"
        "3. If the question asks for reasoning, opinion, recommendations or "
        "strategy -- answer as a smart business analyst would. Use the data "
        "as evidence but reason beyond it freely. When you go past what the "
        "data shows, make it audible: say 'likely', 'my read is', 'worth "
        "checking'. The BU head must always be able to tell a measured fact "
        "from your inference, because they will act on both.\n"
        "4. If asked to draft an email, message or report -- do it. Use real "
        "customer names and numbers from the data where relevant.\n"
        "5. If asked something completely outside the dataset (weather, "
        "general knowledge) -- answer it briefly as a helpful assistant "
        "would, then offer to refocus on the business.\n"
        "6. Always name customers by name when relevant, with their priority "
        "tag. That is the point of this tool.\n"
        "7. Write for a business head -- direct, specific, conversational. "
        "'Conversion fell 2 points in Noida', not 'the delivered-to-enquiry "
        "ratio decreased'. No jargon, no bullet dumps where a sentence works.\n"
        "8. Round numbers naturally. Rs 8.37 L, not Rs 837131.40. "
        "Percentages to one decimal.\n"
        "9. On causes: use rate effect and mix effect when available. You may "
        "also reason from patterns in the data -- delivery speed, unquoted "
        "enquiries, returns, customer mix are all fair ground.\n"
        "10. Supplier is a diagnostic, not a lever. 'Supplier A' is recorded "
        "when sourcing succeeds, so its high conversion is a consequence of "
        "delivery, not a cause. Never recommend shifting volume to it.\n"
        "11. If a question assumes something the data contradicts, correct it "
        "in one line first, then answer the question that was meant. Asked to "
        "write to 'our top customer who has gone quiet' when the top customer "
        "ordered today, say so and pick the largest one who actually has gone "
        "quiet. Never invent a customer's state to fit the question -- states "
        "(quiet, growing, at risk, P1) are data, exactly like numbers are.\n"
    )


# --------------------------------------------------------------- assembly
def build_system_prompt(I: dict = None, flags: pd.DataFrame = None) -> str:
    if I is None:
        I = build_all()
    if flags is None:
        flags = assign_priority(I)
    psum = priority_summary(flags)

    return "".join([
        _section_context(I),
        _section_definitions(),
        _section_headline(I),
        _section_yesterday(I),
        _section_why(I),
        _section_priority(flags, psum),
        _section_top_customers(flags),
        _section_segments(I),
        _section_lifecycle(I),
        _section_trend(I),
        _section_rules(),
    ])


def build_morning_brief_request(I: dict) -> str:
    """The user-turn that produces the daily brief. Kept separate from the
    system prompt so the same knowledge base serves both chat and briefing."""
    d = I["daily_snapshot"]
    return (
        f"Write this morning's brief for {d['date']:%A %d %B}. "
        "Six sentences maximum, no headings, no bullet points. Cover: how "
        "yesterday actually went against a normal day, the single most "
        "important thing that changed and why, and who the sales team should "
        "call today by name. Write it the way a trusted analyst would say it "
        "out loud over coffee -- direct, specific, no hedging."
    )


def word_count(text: str) -> int:
    return len(text.split())


if __name__ == "__main__":
    I = build_all()
    flags = assign_priority(I)
    prompt = build_system_prompt(I, flags)

    out = C.OUTPUT_DIR / "system_prompt.txt"
    out.write_text(prompt, encoding="utf-8")

    print(prompt)
    print("\n" + "=" * 70)
    print(f" system prompt: {word_count(prompt):,} words / {len(prompt):,} chars "
          f"(budget 3,000 words)")
    print(f" written to {out}")
    print("=" * 70)
