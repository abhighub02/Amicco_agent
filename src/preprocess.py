"""
preprocess.py
-------------
Loads the raw Excel extract and produces one clean, trustworthy fact table
that every downstream module reads from.

Design notes for the reviewer:

*  We NEVER recompute Order Value as Quantity x Unit Price. In the raw file
   those two disagree on ~45% of priced lines (ratios cluster at 1.00, 0.92,
   0.90 ... down to 0.48) -- i.e. a discount is already baked into Order
   Value. Recomputing would silently overstate revenue. We keep the supplied
   Order Value as truth and expose the implied discount as its own column.

*  "Not Delivered" rows split into two very different business problems:
   never quoted (no Unit Price at all -- a response failure) versus quoted
   and lost (a price / availability failure). We separate them here so the
   agent can talk about them separately.

*  AS_OF is the newest enquiry date in the file, not today's system clock.
   Anchoring to the clock would make every customer drift into "Gone Quiet"
   as the extract ages on disk.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C


# --------------------------------------------------------------------------- load
def load_raw(path=C.RAW_FILE) -> pd.DataFrame:
    """Read the Excel extract exactly as supplied."""
    df = pd.read_excel(path, engine="openpyxl")
    df.columns = [c.strip() for c in df.columns]
    return df


# --------------------------------------------------------------------------- clean
def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ---- dates -----------------------------------------------------------
    for col in ("Enquiry Date", "Delivery Date"):
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # ---- text hygiene ----------------------------------------------------
    text_cols = [
        "Order ID", "Customer ID", "Customer Name", "Business Unit",
        "Product Category", "Product Name", "Delivery Status",
        "Is Virtual Order", "Supplier",
    ]
    for col in text_cols:
        df[col] = df[col].astype("string").str.strip()

    # ---- numerics --------------------------------------------------------
    for col in ("Quantity", "Unit Price", "Order Value", "Items in Order"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Missing-value policy, stated explicitly rather than blanket-filled:
    #   Unit Price missing  -> the enquiry was never quoted. Genuine signal.
    #                          Kept as NaN, flagged in `Was Quoted`.
    #   Quantity missing    -> assume a single unit (the modal value is 1.0).
    #   Order Value missing -> revenue is unknown, NOT zero. Kept NaN for
    #                          averages; a separate _filled column is used
    #                          only where a sum needs to be well-defined.
    df["Was Quoted"] = df["Unit Price"].notna()
    df["Quantity"] = df["Quantity"].fillna(1.0)
    df["Order Value Filled"] = df["Order Value"].fillna(0.0)

    # ---- delivery timing -------------------------------------------------
    df["Delivery Days"] = (df["Delivery Date"] - df["Enquiry Date"]).dt.days
    df.loc[df["Delivery Days"] < 0, "Delivery Days"] = np.nan  # guard; none today

    # ---- outcome flags ---------------------------------------------------
    st = df["Delivery Status"]
    df["Is Delivered"] = st.isin(C.DELIVERED_STATUSES)
    df["Is Partial"] = st.isin(C.PARTIAL_STATUSES)
    df["Is Returned"] = st.isin(C.RETURN_STATUSES)
    df["Is In Progress"] = st.isin(C.IN_PROGRESS_STATUSES)
    df["Is Not Delivered"] = st.isin(C.NOT_DELIVERED_STATUSES)

    # Headline conversion = Delivered only, per the brief's definition.
    df["Converted"] = df["Is Delivered"]

    # Enquiries that died before anyone even priced them.
    df["Lost Unquoted"] = df["Is Not Delivered"] & ~df["Was Quoted"]
    df["Lost Quoted"] = df["Is Not Delivered"] & df["Was Quoted"]

    # ---- implied discount (surfaced, not silently corrected) -------------
    gross = df["Quantity"] * df["Unit Price"]
    with np.errstate(invalid="ignore", divide="ignore"):
        df["Discount Pct"] = np.where(
            (gross > 0) & df["Order Value"].notna(),
            (1.0 - df["Order Value"] / gross) * 100.0,
            np.nan,
        )
    df.loc[df["Discount Pct"].abs() < 0.01, "Discount Pct"] = 0.0

    # ---- calendar helpers ------------------------------------------------
    df["Enquiry Month"] = df["Enquiry Date"].dt.to_period("M").astype("string")
    df["Enquiry Week"] = df["Enquiry Date"].dt.to_period("W").dt.start_time
    df["Enquiry Day"] = df["Enquiry Date"].dt.normalize()

    df["Is Virtual"] = df["Is Virtual Order"].str.lower().eq("yes")
    df["Channel"] = np.where(df["Is Virtual"], "Virtual", "Physical")

    # ---- window flags ----------------------------------------------------
    as_of = df["Enquiry Date"].max()
    # Cohorts younger than MATURITY_DAYS have not had time to convert.
    df["Is Mature"] = df["Enquiry Date"] <= (as_of - pd.Timedelta(days=C.MATURITY_DAYS))
    # Rows before the real data start are a partial extract, not a slow month.
    df["In Analysis Window"] = df["Enquiry Date"] >= pd.Timestamp(C.DATA_START_CUTOFF)

    df = df.sort_values(["Enquiry Date", "Order ID"]).reset_index(drop=True)
    df.attrs["as_of"] = as_of
    return df


# --------------------------------------------------------------------------- report
def quality_report(raw: pd.DataFrame, df: pd.DataFrame) -> dict:
    as_of = df.attrs["as_of"]
    win = df[df["In Analysis Window"]]
    return {
        "rows_in": int(len(raw)),
        "rows_out": int(len(df)),
        "as_of": as_of,
        "date_min": df["Enquiry Date"].min(),
        "date_max": as_of,
        "analysis_window_start": pd.Timestamp(C.DATA_START_CUTOFF),
        "rows_dropped_pre_window": int((~df["In Analysis Window"]).sum()),
        "orders": int(df["Order ID"].nunique()),
        "customers": int(df["Customer ID"].nunique()),
        "business_units": int(df["Business Unit"].nunique()),
        "missing_unit_price": int(df["Unit Price"].isna().sum()),
        "missing_order_value": int(df["Order Value"].isna().sum()),
        "missing_quantity_filled": int(raw["Quantity"].isna().sum()),
        "immature_rows": int((~df["Is Mature"]).sum()),
        "conversion_all": float(df["Converted"].mean()),
        "conversion_window_mature": float(
            win.loc[win["Is Mature"], "Converted"].mean()
        ),
        "lines_with_discount": int((df["Discount Pct"] > 0.01).sum()),
        "median_discount_pct": float(
            df.loc[df["Discount Pct"] > 0.01, "Discount Pct"].median()
        ),
    }


# --------------------------------------------------------------------------- main
def run(save: bool = True):
    raw = load_raw()
    df = clean(raw)
    report = quality_report(raw, df)
    if save:
        # attrs carries a Timestamp, which parquet cannot JSON-serialise --
        # write from a copy with attrs cleared and re-derive as_of on load.
        out = df.copy()
        out.attrs = {}
        try:
            out.to_parquet(C.CLEAN_FILE, index=False)
            C.CLEAN_CSV.unlink(missing_ok=True)
        except Exception:                       # pyarrow not installed
            out.to_csv(C.CLEAN_CSV, index=False)
    return df, report


def load_clean() -> pd.DataFrame:
    """Downstream modules call this. Rebuilds from Excel if no cache exists."""
    if C.CLEAN_FILE.exists():
        df = pd.read_parquet(C.CLEAN_FILE)
    elif C.CLEAN_CSV.exists():
        df = pd.read_csv(
            C.CLEAN_CSV,
            parse_dates=["Enquiry Date", "Delivery Date", "Enquiry Week", "Enquiry Day"],
        )
    else:
        df, _ = run()
        return df
    df.attrs["as_of"] = df["Enquiry Date"].max()
    return df


if __name__ == "__main__":
    df, rep = run()
    print("=" * 68)
    print(" PREPROCESS COMPLETE")
    print("=" * 68)
    print(f"  Rows in / out            : {rep['rows_in']:,} / {rep['rows_out']:,}")
    print(f"  Orders / Customers / BUs : {rep['orders']:,} / {rep['customers']} / {rep['business_units']}")
    print(f"  Enquiry dates            : {rep['date_min']:%d-%b-%Y}  ->  {rep['date_max']:%d-%b-%Y}")
    print(f"  AS OF (anchor date)      : {rep['as_of']:%d-%b-%Y}")
    print(f"  Analysis window starts   : {rep['analysis_window_start']:%d-%b-%Y}"
          f"  ({rep['rows_dropped_pre_window']} sparse rows before it)")
    print("-" * 68)
    print(f"  Never quoted (no price)  : {rep['missing_unit_price']:,} lines")
    print(f"  Order Value missing      : {rep['missing_order_value']:,} lines")
    print(f"  Quantity imputed to 1    : {rep['missing_quantity_filled']:,} lines")
    print(f"  Immature (< {C.MATURITY_DAYS}d old)       : {rep['immature_rows']:,} lines")
    print("-" * 68)
    print(f"  Conversion, raw          : {rep['conversion_all']:.1%}")
    print(f"  Conversion, clean+mature : {rep['conversion_window_mature']:.1%}")
    print(f"  Lines carrying a discount: {rep['lines_with_discount']:,} "
          f"(median {rep['median_discount_pct']:.1f}%)")
    print("=" * 68)
