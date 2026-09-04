"""
priority_flag.py
----------------
Assigns P1 / P2 / P3 to every customer.

THE DEFINITION
    P1  Act today.        Revenue is actively walking out of the door and
                          the customer is still reachable.
    P2  Act this week.    A clear warning sign, not yet an emergency.
    P3  Monitor only.     Behaving normally; no action required.

THE IDEA THAT ORGANISES EVERYTHING
A run of undelivered orders is not a lost customer -- it is a broken promise.
Those are different problems with different owners:

    Undelivered streak, still enquiring   ->  P2, owned by Amicco.
        We are failing them and they are still calling. That is an
        operations problem. Sending a salesperson to apologise does not
        fix a sourcing failure. Fix delivery before they go quiet.

    Undelivered streak, then silence      ->  P1, owned by Sales.
        They gave up on us and are buying somewhere else. This is the
        real churn signal, and it is urgent because the window to win
        them back is closing.

Everything else on the list is a supporting signal: value at stake, and
momentum against the customer's own baseline.

THREE JUDGEMENT CALLS WORTH DEFENDING
    a) Silence is relative to the customer's OWN rhythm. A workshop that
       orders daily going quiet for 10 days is in trouble; one that orders
       monthly is not. A flat day-count threshold gets this wrong in both
       directions.
    b) Momentum is measured against the customer's own baseline, not an
       absolute rupee threshold. A customer down 60% on 2 lakhs is a bigger
       emergency than one down 5% on 5 lakhs. Ranking purely by size just
       reprints the top-customer list every week until the team stops
       reading it.
    c) The P1 list is capped (config.MAX_P1_CUSTOMERS). A list that does not
       fit in a morning is a report, not a priority. Every flagged customer
       keeps their tier and reason; the overflow is stated openly.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
from insights import build_all


# --------------------------------------------------------------- value tiers
def assign_value_tier(customers: pd.DataFrame) -> pd.DataFrame:
    """
    Split customers into High / Mid / Low by delivered revenue.

    pd.qcut is used as specified, but it cannot cut three equal buckets when
    a large block of customers share the same value -- 68 of 330 here have
    zero delivered revenue, so the lower bin edges collide and qcut raises.
    We fall back to ranking, which produces the same three equal-sized groups
    and is stable no matter how the revenue distribution is shaped.
    """
    df = customers.copy()
    try:
        df["Value Tier"] = pd.qcut(
            df["Total Revenue"], 3, labels=["Low", "Mid", "High"]
        ).astype(str)
    except ValueError:
        df["Value Tier"] = pd.qcut(
            df["Total Revenue"].rank(method="first"), 3,
            labels=["Low", "Mid", "High"],
        ).astype(str)
    return df


# --------------------------------------------------------------- rules
def _evaluate(r) -> tuple[str, list[str], float, str]:
    """
    Apply the rule book to one customer.
    Returns (priority, human-readable reasons, urgency score, issue owner).

    THE CENTRAL DISTINCTION
    A run of undelivered orders is OUR failure, not a lost customer. While the
    customer keeps enquiring, we still have the relationship -- what we have is
    an operations problem, and sending a salesperson to apologise does not fix
    a sourcing failure.

    It becomes a sales emergency at the moment they stop calling. An undelivered
    streak followed by silence is a customer who has given up on us and is
    buying from someone else. That is P1, and it is urgent precisely because
    the window to win them back is closing.

    So the streak alone is P2 and owned by operations; the streak PLUS silence
    is P1 and owned by sales.
    """
    # P1 and P2 signals are scored into SEPARATE buckets. Ranking a P1 by a
    # total that includes its P2 points let a merely-noisy customer outrank a
    # genuinely lost one -- the ordering stopped meaning anything. A P1 is
    # ranked on P1 evidence; P2 points only break ties.
    p1_reasons: list[str] = []
    p2_reasons: list[str] = []
    p1_score = 0.0
    p2_score = 0.0
    p1 = p2 = False
    owner = "-"

    high = r["Value Tier"] == "High"
    mid = r["Value Tier"] == "Mid"
    quiet_days = r["Days Since Last Order"]
    nds = r["Consecutive NDs"]
    rev_chg = r["Revenue Change %"]
    ret30 = r["Return Rate 30d %"]
    silent = bool(r.get("Is Silent", False))
    gap = r.get("Median Order Gap")

    # ---- P1: the customer has walked away --------------------------------
    # The defining P1. We failed them repeatedly and then they stopped
    # calling. Scored highest because it is the most certain loss AND the
    # most explicable -- we know exactly what we did wrong.
    if nds >= C.CHURN_STREAK_WATCH and silent:
        p1 = True
        owner = "Sales"
        cadence = (f", against a normal gap of {gap:.0f} days"
                   if gap is not None and not pd.isna(gap) else "")
        p1_reasons.append(
            f"Stopped ordering after {int(nds)} undelivered orders - "
            f"silent {int(quiet_days)} days{cadence}"
        )
        p1_score += 60 + min(nds, 20) * 1.5 + min(quiet_days, 90) / 3

    if high and quiet_days > C.GONE_QUIET_DAYS:
        p1 = True
        owner = "Sales"
        p1_reasons.append(f"Top-tier customer, no enquiry in {int(quiet_days)} days")
        p1_score += 40 + min(quiet_days, 90) / 3

    if high and rev_chg is not None and rev_chg < -C.REVENUE_DROP_P1 * 100:
        p1 = True
        if owner == "-":
            owner = "Sales"
        p1_reasons.append(
            f"Top-tier revenue down {abs(rev_chg):.0f}% vs the previous 30 days"
        )
        p1_score += 30 + min(abs(rev_chg), 100) / 4

    # ---- P2: we are failing them, but they are still with us -------------
    if nds >= C.CHURN_STREAK_WATCH and not silent:
        p2 = True
        if owner == "-":
            owner = "Amicco (delivery)"
        p2_reasons.append(
            f"{int(nds)} orders in a row undelivered - our failure, and they "
            f"are still enquiring (last order {int(quiet_days)}d ago). "
            f"Fix delivery before they go quiet"
        )
        p2_score += 14 + min(nds, 20) * 1.2

    if mid and quiet_days > C.MID_VALUE_QUIET_DAYS:
        p2 = True
        if owner == "-":
            owner = "Sales"
        p2_reasons.append(f"Mid-tier customer quiet for {int(quiet_days)} days")
        p2_score += 15 + min(quiet_days, 60) / 6

    if ret30 is not None and ret30 > C.RETURN_RATE_P2 * 100:
        p2 = True
        if owner == "-":
            owner = "Amicco (quality)"
        p2_reasons.append(f"{ret30:.0f}% of last month's lines were returned")
        p2_score += 12

    # Value weighting applies to the whole score, never to a single rule.
    vw = {"High": 1.35, "Mid": 1.0, "Low": 0.7}.get(r["Value Tier"], 1.0)
    p1_score *= vw
    p2_score *= vw

    if p1:
        # P2 points break ties only -- they never lift a P1 above another P1.
        return ("P1", p1_reasons + p2_reasons,
                round(p1_score + min(p2_score, 10) / 10, 1), owner)
    if p2:
        return "P2", p2_reasons, round(p2_score, 1), owner
    return "P3", ["Ordering normally, no anomalies detected"], 0.0, "-"


def assign_priority(insights: dict = None) -> pd.DataFrame:
    if insights is None:
        insights = build_all()

    cust = assign_value_tier(insights["customers"])

    evaluated = cust.apply(_evaluate, axis=1)
    cust["Priority"] = [e[0] for e in evaluated]
    cust["Reason"] = ["; ".join(e[1]) for e in evaluated]
    cust["Priority Score"] = [e[2] for e in evaluated]
    cust["Issue Owner"] = [e[3] for e in evaluated]

    # Rank inside each tier so the top of the list is the most urgent.
    order = {"P1": 0, "P2": 1, "P3": 2}
    cust["_ord"] = cust["Priority"].map(order)
    cust = cust.sort_values(
        ["_ord", "Priority Score", "Total Revenue"], ascending=[True, False, False]
    ).drop(columns="_ord").reset_index(drop=True)

    # Capped call list -- what the morning brief reads out.
    cust["On Call List"] = False
    p1_idx = cust.index[cust["Priority"] == "P1"][: C.MAX_P1_CUSTOMERS]
    cust.loc[p1_idx, "On Call List"] = True

    cols = [
        "Customer ID", "Customer Name", "Business Unit", "Priority",
        "Priority Score", "Issue Owner", "On Call List", "Reason",
        "Value Tier", "Lifecycle",
        "Last_Order", "Days Since Last Order", "Median Order Gap",
        "Silence Threshold", "Is Silent", "Total Revenue",
        "Revenue Last 30d", "Revenue Prev 30d", "Revenue Change %",
        "Consecutive NDs", "Consecutive NDs (orders)", "Consecutive NDs (lines)",
        "Orders", "Conversion %", "Return Rate 30d %",
    ]
    cust = cust[[c for c in cols if c in cust.columns]]
    return cust.rename(columns={"Last_Order": "Last Order Date"})


# --------------------------------------------------------------- summary
def priority_summary(flags: pd.DataFrame) -> dict:
    counts = flags["Priority"].value_counts().to_dict()
    rev = flags.groupby("Priority")["Total Revenue"].sum().to_dict()
    total_rev = flags["Total Revenue"].sum()
    n_p1 = counts.get("P1", 0)
    return {
        "counts": {k: int(counts.get(k, 0)) for k in ("P1", "P2", "P3")},
        "revenue_at_stake": {k: float(rev.get(k, 0.0)) for k in ("P1", "P2", "P3")},
        "p1_revenue_share_pct": round(100 * rev.get("P1", 0.0) / total_rev, 1)
        if total_rev else 0.0,
        "call_list_size": int(flags["On Call List"].sum()),
        "p1_overflow": max(0, n_p1 - C.MAX_P1_CUSTOMERS),
        "total_customers": int(len(flags)),
    }


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 70)

    I = build_all()
    flags = assign_priority(I)
    s = priority_summary(flags)

    print("=" * 100)
    print(f" SALES PRIORITY FLAG  |  {s['total_customers']} customers  |  as of {I['as_of']:%d-%b-%Y}")
    print("=" * 100)
    for p in ("P1", "P2", "P3"):
        print(f"  {p}: {s['counts'][p]:>3d} customers   "
              f"revenue at stake {s['revenue_at_stake'][p]:>14,.0f}")
    print(f"\n  P1 holds {s['p1_revenue_share_pct']}% of all delivered revenue.")
    print(f"  Call list capped at {s['call_list_size']} "
          f"({s['p1_overflow']} further P1s queued behind it).")

    print("\n" + "-" * 100)
    print(" TODAY'S CALL LIST")
    print("-" * 100)
    show = ["Customer Name", "Business Unit", "Value Tier", "Total Revenue",
            "Days Since Last Order", "Consecutive NDs", "Priority Score", "Reason"]
    print(flags[flags["On Call List"]][show].to_string(index=False))

    print("\n" + "-" * 100)
    print(" P2 SAMPLE (top 10 by score)")
    print("-" * 100)
    print(flags[flags["Priority"] == "P2"][show].head(10).to_string(index=False))

    flags.to_csv(C.OUTPUT_DIR / "priority_flags.csv", index=False)
    print(f"\n  -> written to {C.OUTPUT_DIR / 'priority_flags.csv'}")
    print("=" * 100)
