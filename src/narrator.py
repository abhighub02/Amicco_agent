"""
narrator.py
-----------
Turns computed metrics into ranked, plain-English findings -- without an LLM.

Why this exists, given that the whole point is an LLM agent:

1. It is the deliverable when there is no API key. A reviewer can clone this
   repo, run it, and read real insights immediately.
2. It is the safety net. If the API is down, the tool degrades to slightly
   stiffer prose rather than to nothing.
3. It sharpens the division of labour. Anything that can be stated
   deterministically SHOULD be -- the LLM's job is interpretation, phrasing
   and follow-up conversation, not fact generation. Building this made it
   obvious which parts genuinely need a model and which do not.

Findings carry a severity score so the agent leads with what matters rather
than reciting metrics in schema order.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C


def _rupees(x) -> str:
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


class Finding:
    def __init__(self, headline: str, detail: str, action: str = "",
                 severity: float = 0.0, tag: str = ""):
        self.headline = headline
        self.detail = detail
        self.action = action
        self.severity = severity
        self.tag = tag

    def as_markdown(self) -> str:
        s = f"**{self.headline}**  \n{self.detail}"
        if self.action:
            s += f"  \n*What to do:* {self.action}"
        return s


# =============================================================== finders
def _f_headline(I: dict) -> list:
    pc, cv = I["period_comparison"], I["conversion"]
    d = pc["delta"]
    out = []

    direction = "up" if (d["revenue_pct"] or 0) >= 0 else "down"
    out.append(Finding(
        f"Revenue is {direction} {abs(d['revenue_pct'] or 0):.1f}% month on month.",
        f"{_rupees(pc['current']['revenue'])} in the last 30 days "
        f"({pc['current_window']}) against {_rupees(pc['previous']['revenue'])} "
        f"in the 30 before it. Enquiries moved {d['enquiries_pct']:+.1f}% and "
        f"conversion {d['conversion_pts']:+.1f} points, so the change is driven "
        f"by {'volume, not close rate' if abs(d['enquiries_pct'] or 0) > abs(d['conversion_pts'] or 0) * 2 else 'a mix of volume and close rate'}.",
        severity=40 + abs(d["revenue_pct"] or 0), tag="revenue",
    ))

    lb = cv["loss_breakdown"]
    out.append(Finding(
        f"{lb['never_quoted']:,} enquiries were never even priced.",
        f"That is {lb['never_quoted_pct_of_all']}% of everything customers asked "
        f"for. Separately, {lb['quoted_but_lost']:,} lines "
        f"({lb['quoted_but_lost_pct_of_all']}%) were quoted and still lost. "
        "These are two different problems: the first is response speed and "
        "coverage, the second is price or availability.",
        "Fixing the unquoted pile needs no pricing decision at all - it is the "
        "cheapest conversion available.",
        severity=55 + lb["never_quoted_pct_of_all"], tag="funnel",
    ))
    return out


def _f_drivers(I: dict) -> list:
    out = []
    for key, noun in (("drivers_by_bu", "business unit"),
                      ("drivers_by_category", "category")):
        d = I[key]
        if not len(d):
            continue
        dim = d.columns[0]
        worst = d.iloc[0]
        if abs(worst["Total Effect (pts)"]) < 0.05:
            continue

        rate, mix = worst["Rate Effect (pts)"], worst["Mix Effect (pts)"]
        # Only claim a single cause when one effect clearly dominates. When
        # they are close, saying "it was the mix" is a coin-flip dressed up
        # as a finding -- exactly the kind of false confidence that makes a
        # BU head stop believing the tool.
        if abs(rate) > abs(mix) * 1.5:
            cause = "it is converting worse, not because volume moved"
        elif abs(mix) > abs(rate) * 1.5:
            cause = "volume shifted away from it, not because it got worse at closing"
        else:
            cause = ("both a weaker close rate and a shift in volume, in "
                     "roughly equal measure")
        out.append(Finding(
            f"{worst[dim]} is the biggest drag on conversion this month.",
            f"It pulled overall conversion down {abs(worst['Total Effect (pts)']):.2f} "
            f"points. Its own conversion went from {worst['Conversion Prev']}% to "
            f"{worst['Conversion Last']}% on {int(worst['Enquiries Last 30d']):,} "
            f"enquiries. The cause is {cause} "
            f"(rate effect {rate:+.2f} pts, mix effect {mix:+.2f} pts).",
            severity=50 + abs(worst["Total Effect (pts)"]) * 12, tag=f"driver-{noun}",
        ))

        # a collapse worth naming even if its weight is small
        d2 = d[d["Enquiries Last 30d"] >= 50].copy()
        if len(d2):
            d2["swing"] = d2["Conversion Last"] - d2["Conversion Prev"]
            w = d2.sort_values("swing").iloc[0]
            if w["swing"] < -15:
                out.append(Finding(
                    f"{w[dim]} conversion fell off a cliff: "
                    f"{w['Conversion Prev']}% to {w['Conversion Last']}%.",
                    f"On {int(w['Enquiries Last 30d']):,} enquiries this month "
                    f"against {int(w['Enquiries Prev 30d']):,} last month. A drop "
                    f"of {abs(w['swing']):.0f} points is not noise.",
                    "Worth a direct look at what changed in sourcing or pricing there.",
                    severity=60 + abs(w["swing"]), tag=f"collapse-{noun}",
                ))
    return out


def _f_delivery(I: dict) -> list:
    bu = I["delivery_speed"]["by_business_unit"]
    if len(bu) < 2:
        return []
    slow, fast = bu.iloc[-1], bu.iloc[0]
    if slow["Mean_Days"] < fast["Mean_Days"] * 2:
        return []
    return [Finding(
        f"{slow['Business Unit']} takes {slow['Mean_Days']:.1f} days to deliver "
        f"against {fast['Mean_Days']:.2f} in {fast['Business Unit']}.",
        f"Measured across {int(slow['Lines']):,} delivered lines, so it is a "
        "settled pattern rather than a bad week. Everywhere else is effectively "
        "same-day.",
        "A customer who waits days learns to call someone else first.",
        severity=45 + slow["Mean_Days"] * 3, tag="delivery",
    )]


def _f_customers(I: dict, flags: pd.DataFrame) -> list:
    out = []
    lc = I["lifecycle_counts"]
    quiet, new = lc.get("Gone Quiet", 0), lc.get("New", 0)
    shrink, grow = lc.get("Shrinking", 0), lc.get("Growing", 0)

    out.append(Finding(
        f"{new} new customers this month, {quiet} have gone quiet.",
        f"{grow} customers are growing and {shrink} are shrinking. "
        f"{'The base is expanding.' if new >= quiet else 'We are losing customers faster than we are adding them.'}",
        severity=35 + abs(quiet - new) * 2, tag="lifecycle",
    ))

    top = flags[flags["On Call List"]].head(3)
    if len(top):
        names = "; ".join(
            f"{r['Customer Name']} ({r['Business Unit']}, "
            f"{_rupees(r['Total Revenue'])})" for _, r in top.iterrows()
        )
        out.append(Finding(
            f"{int((flags['Priority'] == 'P1').sum())} customers need a call today.",
            f"Top three by urgency: {names}.",
            f"Full list on the Priority tab; it holds "
            f"{_rupees(flags.loc[flags['Priority'] == 'P1', 'Total Revenue'].sum())} "
            "of revenue.",
            severity=70, tag="priority",
        ))

    # The two lanes, reported separately because they have different owners
    # and different fixes. Collapsing them into one "at risk" number is what
    # makes a churn report unactionable.
    streaked = flags[flags["Consecutive NDs"] >= C.CHURN_STREAK_WATCH]
    gave_up = streaked[streaked["Is Silent"]]
    still_here = streaked[~streaked["Is Silent"]]

    if len(gave_up):
        worst = gave_up.sort_values("Priority Score", ascending=False).iloc[0]
        gap = worst.get("Median Order Gap")
        cadence = ""
        if gap is not None and not pd.isna(gap):
            every = "day" if round(gap) <= 1 else f"{gap:.0f} days"
            cadence = f", a customer who normally orders every {every}"
        out.append(Finding(
            f"{len(gave_up)} customers stopped ordering after we failed to "
            "deliver to them.",
            f"They carry {_rupees(gave_up['Total Revenue'].sum())} between them. "
            f"The clearest case is {worst['Customer Name']} "
            f"({worst['Business Unit']}, {_rupees(worst['Total Revenue'])}): "
            f"{int(worst['Consecutive NDs'])} undelivered orders, then silence for "
            f"{int(worst['Days Since Last Order'])} days{cadence}.",
            "These are the calls that matter today - we know exactly what went "
            "wrong, and the window to win them back is closing.",
            severity=90 + len(gave_up) / 4, tag="churn",
        ))

    if len(still_here):
        worst = still_here.sort_values("Consecutive NDs", ascending=False).iloc[0]
        out.append(Finding(
            f"{len(still_here)} customers are still enquiring despite "
            f"{C.CHURN_STREAK_WATCH}+ undelivered orders in a row.",
            f"{_rupees(still_here['Total Revenue'].sum())} of revenue sits behind "
            f"them. Worst is {worst['Customer Name']} ({worst['Business Unit']}, "
            f"{_rupees(worst['Total Revenue'])}) at "
            f"{int(worst['Consecutive NDs'])} in a row, and they ordered again "
            f"{int(worst['Days Since Last Order'])} days ago.",
            "This is an operations problem, not a sales one. They have not left "
            "yet - fix the sourcing before they do.",
            severity=78 + len(still_here) / 6, tag="ops",
        ))
    return out


def _f_concentration(I: dict, flags: pd.DataFrame) -> list:
    rev = flags["Total Revenue"].sort_values(ascending=False)
    total = rev.sum()
    if not total:
        return []
    top20 = rev.head(20).sum() / total * 100
    return [Finding(
        f"The top 20 customers are {top20:.0f}% of revenue.",
        f"Out of {len(flags)} active customers. Concentration this high means a "
        "single quiet month from two or three names is a visible revenue miss.",
        severity=30 + top20 / 3, tag="concentration",
    )]


def _f_channel(I: dict) -> list:
    ch = I["channel_split"]
    if len(ch) < 2:
        return []
    v = ch[ch["Channel"] == "Virtual"]
    p = ch[ch["Channel"] == "Physical"]
    if not len(v) or not len(p):
        return []
    v, p = v.iloc[0], p.iloc[0]
    if v["Conversion %"] - p["Conversion %"] < 10:
        return []
    return [Finding(
        f"Virtual orders convert at {v['Conversion %']}% against "
        f"{p['Conversion %']}% for physical.",
        f"But virtual is only {v['Share of Enquiries %']}% of enquiries "
        f"({int(v['Enquiries']):,} lines). The gap is large enough to be worth "
        "understanding, though the volume is small and these customers may "
        "simply be the more organised ones.",
        "Treat as a question to investigate, not a proven lever.",
        severity=32, tag="channel",
    )]


# =============================================================== assembly
def generate_findings(I: dict, flags: pd.DataFrame) -> list:
    found = []
    for fn in (_f_headline, _f_drivers, _f_delivery, _f_concentration, _f_channel):
        try:
            found += fn(I)
        except Exception:
            continue
    try:
        found += _f_customers(I, flags)
    except Exception:
        pass
    return sorted(found, key=lambda f: -f.severity)


def morning_brief(I: dict, flags: pd.DataFrame, top_n: int = 5) -> str:
    """Deterministic morning brief -- the fallback when no model is available."""
    d = I["daily_snapshot"]
    findings = generate_findings(I, flags)[:top_n]

    vol = d["enquiries_vs_baseline_pct"]
    mood = ("a normal day" if vol is None or abs(vol) < 12
            else ("a strong day" if vol > 0 else "a slow day"))

    lines = [
        f"### Morning brief - {d['date']:%A %d %B %Y}",
        "",
        f"Yesterday was {mood}: {d['enquiries']:,} enquiries from "
        f"{d['customers']} customers across {d['orders']:,} orders, against a "
        f"typical {d['baseline_enquiries']:.0f} for a {d['weekday']}. "
        f"{d['delivered']:,} lines were delivered, worth {_rupees(d['revenue'])}.",
        "",
        f"*{d['caveat']}*",
        "",
        "**What matters this morning**",
        "",
    ]
    for i, f in enumerate(findings, 1):
        lines.append(f"{i}. {f.as_markdown()}")
        lines.append("")
    return "\n".join(lines)


def answer_offline(question: str, I: dict, flags: pd.DataFrame) -> str | None:
    """Narrated answer for the common question shapes. None = no match."""
    q = question.lower()
    F = generate_findings(I, flags)

    def pick(*tags):
        hits = [f for f in F if any(f.tag.startswith(t) for t in tags)]
        return hits or None

    if any(w in q for w in ("call", "p1", "urgent", "priorit", "today", "action")):
        sel = pick("priority", "churn", "ops")
    elif any(w in q for w in ("convers", "why", "drop", "fell", "improv", "driver")):
        sel = pick("driver", "collapse", "funnel", "revenue")
    elif any(w in q for w in ("custom", "quiet", "churn", "slip", "new", "growing", "lifecycle")):
        sel = pick("churn", "ops", "lifecycle", "concentration")
    elif any(w in q for w in ("deliver", "slow", "speed", "days", "region", "zone", "unit")):
        sel = pick("delivery", "driver-business")
    elif any(w in q for w in ("categor", "batter", "paint", "oil", "spare")):
        sel = pick("driver-categ", "collapse-categ")
    elif any(w in q for w in ("channel", "virtual", "physical")):
        sel = pick("channel")
    elif any(w in q for w in ("revenue", "sales", "trend", "growth", "month")):
        sel = pick("revenue", "funnel")
    elif any(w in q for w in ("brief", "yesterday", "morning", "overall", "how are we")):
        return morning_brief(I, flags)
    else:
        sel = None

    if not sel:
        return None
    return "\n\n".join(f.as_markdown() for f in sel[:3])


if __name__ == "__main__":
    from insights import build_all
    from priority_flag import assign_priority

    I = build_all()
    flags = assign_priority(I)
    print(morning_brief(I, flags))
    print("\n" + "=" * 70)
    print(" ALL FINDINGS, RANKED")
    print("=" * 70 + "\n")
    for f in generate_findings(I, flags):
        print(f"[{f.severity:5.1f}] {f.as_markdown()}\n")
