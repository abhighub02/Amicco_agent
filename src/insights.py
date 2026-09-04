"""
insights.py
-----------
Computes every business metric the agent is allowed to talk about, and
returns them as one structured dictionary.

This is the trust boundary of the whole system. Arithmetic happens here, in
pandas, once. The LLM downstream never calculates anything -- it only reads
these numbers and explains them. That is the single design decision that
stops the agent from inventing figures.

Conventions used throughout:
  * "Enquiry"  = one line item.
  * "Revenue"  = Order Value on lines with Delivery Status == Delivered.
  * "Conversion" = delivered lines / total lines.
  * Every window is measured back from AS_OF (the newest enquiry date in the
    file), never from the system clock.
  * Month-on-month is implemented as trailing 30 days vs the 30 days before
    it. Calendar months would compare a full August against a June that only
    holds nine real days.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
from preprocess import load_clean


# --------------------------------------------------------------- small helpers
def _trailing_streak(flags) -> int:
    """Length of the run of True values at the END of the sequence."""
    n = 0
    for v in reversed(list(flags)):
        if bool(v):
            n += 1
        else:
            break
    return n


def _safe_div(a, b):
    return float(a) / float(b) if b else 0.0


def _pct_change(new, old):
    """Percentage change, guarding the divide-by-zero case honestly."""
    if old in (0, None) or pd.isna(old):
        return None
    return (float(new) - float(old)) / float(old) * 100.0


# =============================================================== a) frequent customers
def frequent_customers(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    g = (
        df.groupby(["Customer ID", "Customer Name", "Business Unit"], observed=True)
        .agg(
            Orders=("Order ID", "nunique"),
            Enquiries=("Order ID", "size"),
            Delivered=("Converted", "sum"),
            Revenue=("Order Value Filled", lambda s: s[df.loc[s.index, "Converted"]].sum()),
            Last_Order=("Enquiry Date", "max"),
        )
        .reset_index()
    )
    g["Conversion %"] = (100 * g["Delivered"] / g["Enquiries"]).round(1)
    g = g.sort_values("Orders", ascending=False).reset_index(drop=True)
    return g.head(top_n)


# =============================================================== b) conversion
def conversion(df: pd.DataFrame) -> dict:
    mature = df[df["Is Mature"]]

    def _block(frame):
        return {
            "enquiries": int(len(frame)),
            "delivered": int(frame["Converted"].sum()),
            "conversion_pct": round(100 * frame["Converted"].mean(), 1) if len(frame) else 0.0,
        }

    by_bu = (
        df.groupby("Business Unit", observed=True)
        .agg(Enquiries=("Order ID", "size"), Delivered=("Converted", "sum"))
        .reset_index()
    )
    by_bu["Conversion %"] = (100 * by_bu["Delivered"] / by_bu["Enquiries"]).round(1)
    by_bu = by_bu.sort_values("Conversion %", ascending=False).reset_index(drop=True)

    # Why did we lose the rest? Two very different failures.
    nd = df["Is Not Delivered"].sum()
    return {
        "overall": _block(df),
        "overall_mature_only": _block(mature),
        "by_business_unit": by_bu,
        "loss_breakdown": {
            "never_quoted": int(df["Lost Unquoted"].sum()),
            "never_quoted_pct_of_all": round(100 * _safe_div(df["Lost Unquoted"].sum(), len(df)), 1),
            "quoted_but_lost": int(df["Lost Quoted"].sum()),
            "quoted_but_lost_pct_of_all": round(100 * _safe_div(df["Lost Quoted"].sum(), len(df)), 1),
            "returned": int(df["Is Returned"].sum()),
            "in_progress": int(df["Is In Progress"].sum()),
            "total_not_delivered": int(nd),
        },
    }


def conversion_trend(df: pd.DataFrame, weeks: int = 12) -> pd.DataFrame:
    """Weekly conversion, with a flag for weeks that are not fully observed."""
    w = (
        df.groupby("Enquiry Week", observed=True)
        .agg(
            Enquiries=("Order ID", "size"),
            Delivered=("Converted", "sum"),
            Revenue=("Order Value Filled", lambda s: s[df.loc[s.index, "Converted"]].sum()),
        )
        .reset_index()
        .sort_values("Enquiry Week")
    )
    w["Conversion %"] = (100 * w["Delivered"] / w["Enquiries"]).round(1)
    as_of = df.attrs["as_of"]
    start = pd.Timestamp(C.DATA_START_CUTOFF)
    w["Complete"] = (w["Enquiry Week"] >= start) & (
        w["Enquiry Week"] + pd.Timedelta(days=6) <= as_of
    )
    return w.tail(weeks).reset_index(drop=True)


# =============================================================== c) delivery speed
def delivery_speed(df: pd.DataFrame) -> dict:
    d = df[df["Delivery Days"].notna()]
    by_bu = (
        d.groupby("Business Unit", observed=True)["Delivery Days"]
        .agg(Mean_Days="mean", Median_Days="median", Lines="size")
        .reset_index()
    )
    by_bu["Mean_Days"] = by_bu["Mean_Days"].round(2)
    by_bu = by_bu.sort_values("Mean_Days").reset_index(drop=True)
    return {
        "overall_mean_days": round(float(d["Delivery Days"].mean()), 2),
        "overall_median_days": float(d["Delivery Days"].median()),
        "p95_days": float(d["Delivery Days"].quantile(0.95)),
        "by_business_unit": by_bu,
    }


# =============================================================== d) lifecycle
def customer_lifecycle(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify every customer into New / Growing / Steady / Shrinking / Gone Quiet.

    Precedence is deliberate: Gone Quiet wins over everything (if they have
    stopped, their growth rate last month is irrelevant), then New (too young
    to have a trend), then the trend bands.
    """
    as_of = df.attrs["as_of"]
    w0 = as_of - pd.Timedelta(days=30)     # start of current 30d window
    w1 = as_of - pd.Timedelta(days=60)     # start of previous 30d window

    base = (
        df.groupby(["Customer ID", "Customer Name", "Business Unit"], observed=True)
        .agg(
            First_Order=("Enquiry Date", "min"),
            Last_Order=("Enquiry Date", "max"),
            Orders=("Order ID", "nunique"),
            Enquiries=("Order ID", "size"),
        )
        .reset_index()
    )
    base["Days Since Last Order"] = (as_of - base["Last_Order"]).dt.days
    base["Days Since First Order"] = (as_of - base["First_Order"]).dt.days

    # Each customer's own ordering rhythm: the median gap between the distinct
    # days on which they placed orders. This is the yardstick for "silence" --
    # a daily customer quiet for 10 days is in trouble, a monthly one is not.
    gaps = (
        df[["Customer ID", "Enquiry Day"]].drop_duplicates()
        .sort_values(["Customer ID", "Enquiry Day"])
        .groupby("Customer ID", observed=True)["Enquiry Day"]
        .apply(lambda s: s.diff().dt.days.median())
    )
    base["Median Order Gap"] = base["Customer ID"].map(gaps)

    # One-time buyers have no gap to measure; fall back to the flat threshold.
    thresh = np.maximum(
        base["Median Order Gap"].fillna(C.GONE_QUIET_DAYS) * C.SILENCE_GAP_MULTIPLIER,
        C.SILENCE_MIN_DAYS,
    )
    base["Silence Threshold"] = thresh.round(1)
    base["Is Silent"] = base["Days Since Last Order"] > thresh

    cur = df[df["Enquiry Date"] > w0].groupby("Customer ID", observed=True)["Order ID"].nunique()
    prv = (
        df[(df["Enquiry Date"] > w1) & (df["Enquiry Date"] <= w0)]
        .groupby("Customer ID", observed=True)["Order ID"].nunique()
    )
    base["Orders Last 30d"] = base["Customer ID"].map(cur).fillna(0).astype(int)
    base["Orders Prev 30d"] = base["Customer ID"].map(prv).fillna(0).astype(int)
    base["Order Change %"] = [
        _pct_change(n, p) for n, p in zip(base["Orders Last 30d"], base["Orders Prev 30d"])
    ]

    # revenue over the same two windows -- used by the priority flag
    rev_cur = (
        df[(df["Enquiry Date"] > w0) & df["Converted"]]
        .groupby("Customer ID", observed=True)["Order Value Filled"].sum()
    )
    rev_prv = (
        df[(df["Enquiry Date"] > w1) & (df["Enquiry Date"] <= w0) & df["Converted"]]
        .groupby("Customer ID", observed=True)["Order Value Filled"].sum()
    )
    base["Revenue Last 30d"] = base["Customer ID"].map(rev_cur).fillna(0.0)
    base["Revenue Prev 30d"] = base["Customer ID"].map(rev_prv).fillna(0.0)
    base["Revenue Change %"] = [
        _pct_change(n, p) for n, p in zip(base["Revenue Last 30d"], base["Revenue Prev 30d"])
    ]

    def _label(r):
        if r["Days Since Last Order"] > C.GONE_QUIET_DAYS:
            return "Gone Quiet"
        if r["Days Since First Order"] <= C.NEW_CUSTOMER_DAYS:
            return "New"
        ch = r["Order Change %"]
        if ch is None:                       # no orders in the prior window
            return "New" if r["Orders Last 30d"] > 0 else "Gone Quiet"
        if ch > C.GROWTH_BAND * 100:
            return "Growing"
        if ch < -C.GROWTH_BAND * 100:
            return "Shrinking"
        return "Steady"

    base["Lifecycle"] = base.apply(_label, axis=1)
    return base


# =============================================================== e) churn risk
def churn_risk(df: pd.DataFrame, grain: str = None) -> pd.DataFrame:
    """
    Trailing run of consecutive non-deliveries per customer.

    Grain is configurable (see config.STREAK_GRAIN). Order grain counts
    consecutive orders in which NOTHING was delivered; line grain counts
    consecutive undelivered line items. Both are returned so the choice is
    auditable, but only the configured one drives the flag.
    """
    grain = grain or C.STREAK_GRAIN

    s = df.sort_values(["Customer ID", "Enquiry Date", "Order ID"])
    line_streak = s.groupby("Customer ID", observed=True)["Converted"].apply(
        lambda x: _trailing_streak(~x.astype(bool))
    )

    o = (
        s.groupby(["Customer ID", "Order ID", "Enquiry Date"], observed=True)["Converted"]
        .max()
        .reset_index()
        .sort_values(["Customer ID", "Enquiry Date", "Order ID"])
    )
    order_streak = o.groupby("Customer ID", observed=True)["Converted"].apply(
        lambda x: _trailing_streak(~x.astype(bool))
    )

    out = pd.DataFrame(
        {"Consecutive NDs (lines)": line_streak, "Consecutive NDs (orders)": order_streak}
    ).reset_index()
    out["Consecutive NDs"] = out[
        "Consecutive NDs (orders)" if grain == "order" else "Consecutive NDs (lines)"
    ]
    out["Churn Risk"] = np.where(
        out["Consecutive NDs"] >= C.CHURN_STREAK_HIGH, "High",
        np.where(out["Consecutive NDs"] >= C.CHURN_STREAK_WATCH, "Watch", "Low"),
    )
    return out.sort_values("Consecutive NDs", ascending=False).reset_index(drop=True)


# =============================================================== f) returns
def return_behaviour(df: pd.DataFrame) -> pd.DataFrame:
    as_of = df.attrs["as_of"]
    recent = df[df["Enquiry Date"] > as_of - pd.Timedelta(days=30)]

    all_time = df.groupby("Customer ID", observed=True).agg(
        Lines=("Order ID", "size"), Returns=("Is Returned", "sum")
    )
    rec = recent.groupby("Customer ID", observed=True).agg(
        Lines_30d=("Order ID", "size"), Returns_30d=("Is Returned", "sum")
    )
    out = all_time.join(rec, how="left").fillna(0).reset_index()
    out["Return Rate %"] = (100 * out["Returns"] / out["Lines"]).round(1)
    out["Return Rate 30d %"] = np.where(
        out["Lines_30d"] > 0, (100 * out["Returns_30d"] / out["Lines_30d"]).round(1), 0.0
    )
    for c in ("Lines_30d", "Returns_30d", "Returns"):
        out[c] = out[c].astype(int)
    return out.sort_values("Returns", ascending=False).reset_index(drop=True)


# =============================================================== g) revenue trend
def revenue_trend(df: pd.DataFrame, weeks: int = 12) -> pd.DataFrame:
    return conversion_trend(df, weeks=weeks)


# =============================================================== h) category
def category_performance(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("Product Category", observed=True)
        .agg(
            Enquiries=("Order ID", "size"),
            Delivered=("Converted", "sum"),
            Revenue=("Order Value Filled", lambda s: s[df.loc[s.index, "Converted"]].sum()),
            Enquiry_Value=("Order Value Filled", "sum"),
        )
        .reset_index()
    )
    g["Conversion %"] = (100 * g["Delivered"] / g["Enquiries"]).round(1)
    g["Revenue Share %"] = (100 * g["Revenue"] / g["Revenue"].sum()).round(1)
    return g.sort_values("Revenue", ascending=False).reset_index(drop=True)


def business_unit_performance(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("Business Unit", observed=True)
        .agg(
            Enquiries=("Order ID", "size"),
            Orders=("Order ID", "nunique"),
            Customers=("Customer ID", "nunique"),
            Delivered=("Converted", "sum"),
            Revenue=("Order Value Filled", lambda s: s[df.loc[s.index, "Converted"]].sum()),
            Mean_Delivery_Days=("Delivery Days", "mean"),
        )
        .reset_index()
    )
    g["Conversion %"] = (100 * g["Delivered"] / g["Enquiries"]).round(1)
    g["Mean_Delivery_Days"] = g["Mean_Delivery_Days"].round(2)
    g["Revenue Share %"] = (100 * g["Revenue"] / g["Revenue"].sum()).round(1)
    return g.sort_values("Revenue", ascending=False).reset_index(drop=True)


# =============================================================== i) channel
def channel_split(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("Channel", observed=True)
        .agg(
            Enquiries=("Order ID", "size"),
            Delivered=("Converted", "sum"),
            Revenue=("Order Value Filled", lambda s: s[df.loc[s.index, "Converted"]].sum()),
        )
        .reset_index()
    )
    g["Conversion %"] = (100 * g["Delivered"] / g["Enquiries"]).round(1)
    g["Share of Enquiries %"] = (100 * g["Enquiries"] / g["Enquiries"].sum()).round(1)
    return g.sort_values("Enquiries", ascending=False).reset_index(drop=True)


def supplier_split(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sourcing channel. NOTE FOR THE AGENT: this is a diagnostic, not a lever.
    "Supplier A" is stamped when sourcing succeeds, so its high conversion is
    largely an effect of delivery, not a cause of it. Reported as "share of
    enquiries we managed to source", never as "route more volume to A".
    """
    g = (
        df.groupby("Supplier", observed=True)
        .agg(Enquiries=("Order ID", "size"), Delivered=("Converted", "sum"))
        .reset_index()
    )
    g["Conversion %"] = (100 * g["Delivered"] / g["Enquiries"]).round(1)
    return g.sort_values("Enquiries", ascending=False).reset_index(drop=True)


# =============================================================== j) daily snapshot
def daily_snapshot(df: pd.DataFrame) -> dict:
    """
    Yesterday's business, benchmarked against the trailing 4-week average for
    the SAME weekday. Comparing a Sunday to a Wednesday would manufacture a
    crisis every Monday morning -- weekday volume swings are large here.
    """
    as_of = df.attrs["as_of"]
    day = df[df["Enquiry Day"] == as_of]
    weekday = as_of.dayofweek

    hist = df[
        (df["Enquiry Day"] < as_of)
        & (df["Enquiry Day"] >= as_of - pd.Timedelta(days=28))
        & (df["Enquiry Date"].dt.dayofweek == weekday)
    ]
    n_hist_days = hist["Enquiry Day"].nunique()

    def _rev(frame):
        return float(frame.loc[frame["Converted"], "Order Value Filled"].sum())

    baseline_enq = _safe_div(len(hist), n_hist_days)
    baseline_rev = _safe_div(_rev(hist), n_hist_days)

    top_bu = (
        day.groupby("Business Unit", observed=True)
        .agg(Enquiries=("Order ID", "size"), Delivered=("Converted", "sum"))
        .reset_index()
    )
    if len(top_bu):
        top_bu["Conversion %"] = (100 * top_bu["Delivered"] / top_bu["Enquiries"]).round(1)
        top_bu = top_bu.sort_values("Enquiries", ascending=False).reset_index(drop=True)

    return {
        "date": as_of,
        "weekday": as_of.strftime("%A"),
        "enquiries": int(len(day)),
        "orders": int(day["Order ID"].nunique()),
        "customers": int(day["Customer ID"].nunique()),
        "delivered": int(day["Converted"].sum()),
        "conversion_pct": round(100 * day["Converted"].mean(), 1) if len(day) else 0.0,
        "revenue": _rev(day),
        "baseline_label": f"average {as_of.strftime('%A')} over the last 4 weeks",
        "baseline_enquiries": round(baseline_enq, 1),
        "baseline_revenue": baseline_rev,
        "baseline_conversion_pct": round(100 * hist["Converted"].mean(), 1) if len(hist) else 0.0,
        "enquiries_vs_baseline_pct": _pct_change(len(day), baseline_enq),
        "revenue_vs_baseline_pct": _pct_change(_rev(day), baseline_rev),
        "by_business_unit": top_bu,
        "caveat": (
            f"Enquiries raised in the last {C.MATURITY_DAYS} days have not had "
            "time to convert, so today's conversion figure will rise."
        ),
    }


# =============================================================== k) the "why"
def conversion_drivers(df: pd.DataFrame, dimension: str = "Business Unit") -> pd.DataFrame:
    """
    Decompose the change in overall conversion between the last 30 days and
    the 30 days before, into:

        RATE effect  -- the same segment converting better or worse
        MIX  effect  -- volume moving toward or away from strong segments

    This is what turns "conversion fell 2 points" into "conversion fell
    2 points because Noida got worse, not because the mix changed". It is the
    single most useful thing the agent can say.
    """
    as_of = df.attrs["as_of"]
    w0 = as_of - pd.Timedelta(days=30)
    w1 = as_of - pd.Timedelta(days=60)

    cur = df[df["Enquiry Date"] > w0]
    prv = df[(df["Enquiry Date"] > w1) & (df["Enquiry Date"] <= w0)]
    if not len(cur) or not len(prv):
        return pd.DataFrame()

    c = cur.groupby(dimension, observed=True).agg(n=("Order ID", "size"), r=("Converted", "mean"))
    p = prv.groupby(dimension, observed=True).agg(n=("Order ID", "size"), r=("Converted", "mean"))
    j = c.join(p, how="outer", lsuffix="_cur", rsuffix="_prv").fillna(0.0)

    j["w_cur"] = j["n_cur"] / j["n_cur"].sum()
    j["w_prv"] = j["n_prv"] / j["n_prv"].sum()

    # Exact shift-share decomposition, in conversion-percentage points.
    #   rate = w_cur * (r_cur - r_prv)      mix = (w_cur - w_prv) * r_prv
    # Chosen over the textbook w_prv-weighted form because this pair
    # telescopes to the true total change with ZERO residual:
    #   SUM(rate + mix) == 100 * (SUM w_cur*r_cur - SUM w_prv*r_prv)
    # An "explanation" whose parts do not add up to the headline number is
    # worse than no explanation -- the BU head would stop trusting the tool.
    j["Rate Effect (pts)"] = 100 * j["w_cur"] * (j["r_cur"] - j["r_prv"])
    j["Mix Effect (pts)"] = 100 * (j["w_cur"] - j["w_prv"]) * j["r_prv"]
    j["Total Effect (pts)"] = j["Rate Effect (pts)"] + j["Mix Effect (pts)"]

    actual = 100 * ((j["w_cur"] * j["r_cur"]).sum() - (j["w_prv"] * j["r_prv"]).sum())
    assert abs(j["Total Effect (pts)"].sum() - actual) < 1e-6, (
        "shift-share decomposition does not reconcile to the actual change"
    )
    for col in ("Rate Effect (pts)", "Mix Effect (pts)", "Total Effect (pts)"):
        j[col] = j[col].round(2)

    out = j.reset_index()[
        [dimension, "n_prv", "n_cur", "r_prv", "r_cur",
         "Rate Effect (pts)", "Mix Effect (pts)", "Total Effect (pts)"]
    ]
    out.columns = [
        dimension, "Enquiries Prev 30d", "Enquiries Last 30d",
        "Conversion Prev", "Conversion Last",
        "Rate Effect (pts)", "Mix Effect (pts)", "Total Effect (pts)",
    ]
    out["Conversion Prev"] = (100 * out["Conversion Prev"]).round(1)
    out["Conversion Last"] = (100 * out["Conversion Last"]).round(1)
    return out.sort_values("Total Effect (pts)").reset_index(drop=True)


def period_comparison(df: pd.DataFrame) -> dict:
    """Headline last-30d vs prev-30d movement, the spine of the daily brief."""
    as_of = df.attrs["as_of"]
    w0, w1 = as_of - pd.Timedelta(days=30), as_of - pd.Timedelta(days=60)
    cur = df[df["Enquiry Date"] > w0]
    prv = df[(df["Enquiry Date"] > w1) & (df["Enquiry Date"] <= w0)]

    def _b(f):
        return {
            "enquiries": int(len(f)),
            "orders": int(f["Order ID"].nunique()),
            "customers": int(f["Customer ID"].nunique()),
            "conversion_pct": round(100 * f["Converted"].mean(), 1) if len(f) else 0.0,
            "revenue": float(f.loc[f["Converted"], "Order Value Filled"].sum()),
        }

    a, b = _b(cur), _b(prv)
    return {
        "current_window": f"{(w0 + pd.Timedelta(days=1)):%d %b} to {as_of:%d %b}",
        "previous_window": f"{(w1 + pd.Timedelta(days=1)):%d %b} to {w0:%d %b}",
        "current": a,
        "previous": b,
        "delta": {
            "enquiries_pct": _pct_change(a["enquiries"], b["enquiries"]),
            "revenue_pct": _pct_change(a["revenue"], b["revenue"]),
            "conversion_pts": round(a["conversion_pct"] - b["conversion_pct"], 1),
            "customers_pct": _pct_change(a["customers"], b["customers"]),
        },
    }


# =============================================================== orchestrator
def build_all(df: pd.DataFrame = None) -> dict:
    """Compute everything once and hand back one dictionary."""
    if df is None:
        df = load_clean()
    win = df[df["In Analysis Window"]].copy()
    win.attrs["as_of"] = df.attrs["as_of"]

    life = customer_lifecycle(win)
    churn = churn_risk(win)
    rets = return_behaviour(win)

    # one customer-level table that priority_flag.py consumes directly
    customers = (
        life.merge(churn, on="Customer ID", how="left")
        .merge(rets, on="Customer ID", how="left")
    )
    rev_all = (
        win[win["Converted"]].groupby("Customer ID", observed=True)["Order Value Filled"].sum()
    )
    customers["Total Revenue"] = customers["Customer ID"].map(rev_all).fillna(0.0)
    customers["Conversion %"] = (
        100 * customers["Customer ID"].map(
            win.groupby("Customer ID", observed=True)["Converted"].mean()
        )
    ).round(1)

    return {
        "as_of": df.attrs["as_of"],
        "window_start": pd.Timestamp(C.DATA_START_CUTOFF),
        "row_count": int(len(win)),
        "frequent_customers": frequent_customers(win),
        "conversion": conversion(win),
        "conversion_trend": conversion_trend(win),
        "delivery_speed": delivery_speed(win),
        "lifecycle": life,
        "lifecycle_counts": life["Lifecycle"].value_counts().to_dict(),
        "churn_risk": churn,
        "returns": rets,
        "revenue_trend": revenue_trend(win),
        "category_performance": category_performance(win),
        "business_unit_performance": business_unit_performance(win),
        "channel_split": channel_split(win),
        "supplier_split": supplier_split(win),
        "daily_snapshot": daily_snapshot(win),
        "period_comparison": period_comparison(win),
        "drivers_by_bu": conversion_drivers(win, "Business Unit"),
        "drivers_by_category": conversion_drivers(win, "Product Category"),
        "customers": customers,
    }


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    I = build_all()

    print("=" * 74)
    print(f" INSIGHTS  |  as of {I['as_of']:%d-%b-%Y}  |  {I['row_count']:,} enquiry lines")
    print("=" * 74)

    cv = I["conversion"]
    print(f"\n[b] CONVERSION  overall {cv['overall']['conversion_pct']}%  "
          f"({cv['overall']['delivered']:,} of {cv['overall']['enquiries']:,})")
    print(f"    mature-only  {cv['overall_mature_only']['conversion_pct']}%")
    print("\n    by business unit:")
    print(cv["by_business_unit"].to_string(index=False))
    print("\n    where the other 61% goes:")
    for k, v in cv["loss_breakdown"].items():
        print(f"      {k:28s} {v:,}")

    print("\n[c] DELIVERY SPEED  overall mean "
          f"{I['delivery_speed']['overall_mean_days']}d  |  p95 {I['delivery_speed']['p95_days']}d")
    print(I["delivery_speed"]["by_business_unit"].to_string(index=False))

    print("\n[d] LIFECYCLE:", I["lifecycle_counts"])

    print("\n[e] CHURN RISK:", I["churn_risk"]["Churn Risk"].value_counts().to_dict())

    print("\n[g] WEEKLY TREND (last 12):")
    print(I["revenue_trend"].to_string(index=False))

    print("\n[h] CATEGORY:")
    print(I["category_performance"].to_string(index=False))

    print("\n[i] CHANNEL:")
    print(I["channel_split"].to_string(index=False))

    pc = I["period_comparison"]
    print(f"\n[j] LAST 30D ({pc['current_window']}) vs PREV 30D ({pc['previous_window']}):")
    print(f"    enquiries {pc['current']['enquiries']:,} vs {pc['previous']['enquiries']:,} "
          f"({pc['delta']['enquiries_pct']:+.1f}%)")
    print(f"    revenue   {pc['current']['revenue']:,.0f} vs {pc['previous']['revenue']:,.0f} "
          f"({pc['delta']['revenue_pct']:+.1f}%)")
    print(f"    conversion {pc['current']['conversion_pct']}% vs "
          f"{pc['previous']['conversion_pct']}% ({pc['delta']['conversion_pts']:+.1f} pts)")

    print("\n[k] WHY -- conversion drivers by business unit (pts of overall change):")
    print(I["drivers_by_bu"].to_string(index=False))
    print("=" * 74)
