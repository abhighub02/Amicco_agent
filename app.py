"""
app.py
------
Streamlit interface for the Business Insights Agent.

The landing view is the morning brief, because that is the product: the BU
head opens this with their coffee and reads what happened yesterday. Chat is
the follow-up mechanism, not the main event.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

SRC = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC))

# Streamlit Community Cloud supplies secrets through st.secrets, not a .env
# file. Copy them into the environment BEFORE importing agent.py, so the same
# os.getenv lookups work identically locally and when deployed -- and so
# agent.py stays importable from the CLI without Streamlit installed.
for _k in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_WORKSPACE_ID"):
    try:
        if _k in st.secrets and not os.getenv(_k):
            os.environ[_k] = str(st.secrets[_k])
    except Exception:
        pass        # no secrets.toml locally -- .env handles it

# Streamlit Cloud sets HOSTNAME, and there is no .env there to point people at.
_ON_CLOUD = bool(os.getenv("HOSTNAME", "").startswith("streamlit")
                 or os.getenv("STREAMLIT_RUNTIME_ENV")
                 or not (Path(__file__).resolve().parent / ".env").exists())

import config as C
from preprocess import run as run_preprocess
from insights import build_all
from priority_flag import assign_priority, priority_summary
from build_prompt import (
    build_system_prompt, build_morning_brief_request, rupees, signed, word_count,
)
from agent import BusinessInsightsAgent

st.set_page_config(page_title="Business Insights Agent", page_icon="*", layout="wide")

PRIORITY_COLOUR = {"P1": "#c0392b", "P2": "#d68910", "P3": "#1e8449"}


# --------------------------------------------------------------- pipeline
@st.cache_resource(show_spinner=False)
def load_pipeline(_bust: int = 0):
    insights = build_all()
    flags = assign_priority(insights)
    prompt = build_system_prompt(insights, flags)
    return insights, flags, prompt, priority_summary(flags)


def refresh():
    run_preprocess()
    st.cache_resource.clear()
    st.session_state.pop("agent", None)
    st.session_state["messages"] = []
    st.session_state["brief"] = None


# --------------------------------------------------------------- helpers
def mentioned_customers(text: str, flags: pd.DataFrame) -> pd.DataFrame:
    """Find every customer the answer names, so the UI can tag them."""
    hits = [n for n in flags["Customer Name"].unique() if n and n in text]
    if not hits:
        return pd.DataFrame()
    return flags[flags["Customer Name"].isin(hits)]


def render_tags(sub: pd.DataFrame):
    if not len(sub):
        return
    st.caption("Customers referenced in this answer")
    for _, r in sub.iterrows():
        colour = PRIORITY_COLOUR.get(r["Priority"], "#555")
        st.markdown(
            f"<span style='background:{colour};color:#fff;padding:2px 8px;"
            f"border-radius:10px;font-size:0.78rem;font-weight:600'>{r['Priority']}</span>"
            f"&nbsp; <b>{r['Customer Name']}</b> &nbsp;"
            f"<span style='opacity:.7;font-size:0.85rem'>{r['Business Unit']} &middot; "
            f"{rupees(r['Total Revenue'])} &middot; last order "
            f"{int(r['Days Since Last Order'])}d ago &middot; "
            f"{int(r['Consecutive NDs'])} undelivered in a row</span>",
            unsafe_allow_html=True,
        )


# --------------------------------------------------------------- boot
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "brief" not in st.session_state:
    st.session_state["brief"] = None

insights, flags, system_prompt, psum = load_pipeline()

if "agent" not in st.session_state:
    st.session_state["agent"] = BusinessInsightsAgent(system_prompt, insights=insights, flags=flags)
agent = st.session_state["agent"]

as_of = insights["as_of"]
pc = insights["period_comparison"]
snap = insights["daily_snapshot"]


# --------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Business Insights Agent")
    st.caption(f"Data as of **{as_of:%d %b %Y}**")

    if agent.mode == "live":
        st.success(agent.status)
    else:
        st.warning(agent.status)
        # The remedy differs by environment, and naming the wrong one sends
        # people to a file that does not exist on the deployed app.
        if _ON_CLOUD:
            st.caption(
                "Add it under **Manage app -> Settings -> Secrets** as "
                "`GEMINI_API_KEY = \"...\"` (TOML, quotes required). "
                "All figures below are live either way."
            )
        else:
            st.caption("Add an API key to `.env` for written answers. "
                       "All figures below are live either way.")

    st.divider()
    st.metric("Conversion", f"{insights['conversion']['overall']['conversion_pct']}%",
              signed(pc["delta"]["conversion_pts"], " pts vs prev 30d"))
    st.metric("Revenue, last 30 days", rupees(pc["current"]["revenue"]),
              signed(pc["delta"]["revenue_pct"]))
    st.metric("Active customers", pc["current"]["customers"],
              signed(pc["delta"]["customers_pct"]))

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("P1", psum["counts"]["P1"])
    c2.metric("P2", psum["counts"]["P2"])
    c3.metric("P3", psum["counts"]["P3"])
    st.caption(f"Call list capped at {psum['call_list_size']}; "
               f"{psum['p1_overflow']} more P1s queued.")

    st.divider()
    if st.button("Run pipeline / refresh data", width='stretch'):
        with st.spinner("Rebuilding from Raw_Data.xlsx..."):
            refresh()
        st.rerun()
    if st.button("Clear conversation", width='stretch'):
        agent.reset()
        st.session_state["messages"] = []
        st.rerun()
    st.caption(f"System prompt: {word_count(system_prompt):,} words")
    if agent.mode == "live":
        st.caption(agent.usage_summary())


# --------------------------------------------------------------- tabs
tab_brief, tab_chat, tab_priority, tab_numbers = st.tabs(
    ["Morning brief", "Ask a question", "Priority list", "The numbers"]
)


# ---------------------------------------------------------- morning brief
with tab_brief:
    st.subheader(f"Morning brief - {as_of:%A %d %B %Y}")

    k = st.columns(4)
    k[0].metric("Enquiries yesterday", f"{snap['enquiries']:,}",
                signed(snap["enquiries_vs_baseline_pct"]))
    k[1].metric("Orders", f"{snap['orders']:,}")
    k[2].metric("Delivered", f"{snap['delivered']:,}", f"{snap['conversion_pct']}% converted")
    k[3].metric("Revenue", rupees(snap["revenue"]), signed(snap["revenue_vs_baseline_pct"]))
    st.caption(f"Compared against the {snap['baseline_label']}. {snap['caveat']}")

    st.divider()
    if st.session_state["brief"] is None:
        if st.button("Generate today's brief", type="primary"):
            with st.spinner("Writing..."):
                st.session_state["brief"] = agent.brief(build_morning_brief_request(insights))
            st.rerun()
    else:
        st.markdown(st.session_state["brief"])
        render_tags(mentioned_customers(st.session_state["brief"], flags))
        if st.button("Regenerate"):
            st.session_state["brief"] = None
            st.rerun()

    st.divider()
    streak = flags["Consecutive NDs"] >= C.CHURN_STREAK_WATCH
    gave_up = flags[streak & flags["Is Silent"]]
    ops = flags[streak & ~flags["Is Silent"]]

    lane1, lane2 = st.columns(2)
    with lane1:
        st.markdown("##### Sales calls — they gave up on us")
        st.caption(
            f"{len(gave_up)} customers · {rupees(gave_up['Total Revenue'].sum())}. "
            "Undelivered orders, then silence. They are buying elsewhere."
        )
        st.dataframe(
            gave_up.head(8)[["Customer Name", "Business Unit", "Total Revenue",
                             "Consecutive NDs", "Days Since Last Order"]]
            .rename(columns={"Total Revenue": "Revenue",
                             "Consecutive NDs": "Failed orders",
                             "Days Since Last Order": "Silent (days)"}),
            hide_index=True, width='stretch',
        )
    with lane2:
        st.markdown("##### Operations fix — still with us")
        st.caption(
            f"{len(ops)} customers · {rupees(ops['Total Revenue'].sum())}. "
            "We keep failing them but they keep calling. Fix sourcing, "
            "not a sales visit."
        )
        st.dataframe(
            ops.sort_values("Consecutive NDs", ascending=False)
            .head(8)[["Customer Name", "Business Unit", "Total Revenue",
                      "Consecutive NDs", "Days Since Last Order"]]
            .rename(columns={"Total Revenue": "Revenue",
                             "Consecutive NDs": "Failed orders",
                             "Days Since Last Order": "Last order (days)"}),
            hide_index=True, width='stretch',
        )

    st.divider()
    st.markdown("**Full call list**")
    call = flags[flags["On Call List"]].head(8)
    st.dataframe(
        call[["Customer Name", "Business Unit", "Issue Owner", "Total Revenue",
              "Days Since Last Order", "Consecutive NDs", "Reason"]]
        .rename(columns={"Total Revenue": "Revenue",
                         "Days Since Last Order": "Days quiet",
                         "Consecutive NDs": "Undelivered streak"}),
        hide_index=True, width='stretch',
    )


# ---------------------------------------------------------------- chat
with tab_chat:
    st.subheader("Ask about the business")

    if not st.session_state["messages"]:
        st.caption("Try one of these:")
        starters = [
            "How has conversion changed over the last month, and why?",
            "Which customers are slipping away?",
            "How is Noida doing versus Gurgaon?",
            "What happened to Battery conversion?",
            "Who should my team call today?",
        ]
        cols = st.columns(len(starters))
        for col, s in zip(cols, starters):
            if col.button(s, width='stretch'):
                st.session_state["pending"] = s
                st.rerun()

    for m in st.session_state["messages"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m["role"] == "assistant":
                render_tags(mentioned_customers(m["content"], flags))

    question = st.chat_input("e.g. why did conversion drop in Insurance & Fleet?")
    if "pending" in st.session_state:
        question = st.session_state.pop("pending")

    if question:
        st.session_state["messages"].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = agent.ask(question)
            st.markdown(answer)
            render_tags(mentioned_customers(answer, flags))
        st.session_state["messages"].append({"role": "assistant", "content": answer})


# ------------------------------------------------------------ priority
with tab_priority:
    st.subheader("Sales priority")
    st.caption(
        f"P1 customers hold {psum['p1_revenue_share_pct']}% of delivered revenue. "
        "A run of undelivered orders is an **operations** problem while the "
        "customer keeps enquiring (P2, owned by Amicco). It becomes a **sales** "
        "emergency the moment they go silent (P1) - that is the customer giving "
        "up on us. Silence is judged against each customer's own ordering rhythm."
    )
    pick = st.radio("Show", ["P1", "P2", "P3"], horizontal=True, label_visibility="collapsed")
    sub = flags[flags["Priority"] == pick]
    st.caption(f"{len(sub)} customers - {rupees(sub['Total Revenue'].sum())} of revenue")
    st.dataframe(
        sub[["Customer Name", "Business Unit", "Issue Owner", "Value Tier",
             "Lifecycle", "Total Revenue", "Days Since Last Order",
             "Median Order Gap", "Consecutive NDs", "Priority Score", "Reason"]]
        .rename(columns={"Total Revenue": "Revenue",
                         "Days Since Last Order": "Days quiet",
                         "Consecutive NDs": "Undelivered streak"}),
        hide_index=True, width='stretch', height=520,
    )
    st.download_button("Download this list (CSV)", sub.to_csv(index=False),
                       f"priority_{pick}.csv", "text/csv")


# ------------------------------------------------------------- numbers
with tab_numbers:
    st.subheader("The numbers behind every answer")
    st.caption("The agent reads only these. It never calculates anything itself.")

    left, right = st.columns(2)
    with left:
        st.markdown("**Conversion by business unit**")
        st.dataframe(insights["conversion"]["by_business_unit"],
                     hide_index=True, width='stretch')
        st.markdown("**Why conversion moved (last 30d vs previous 30d)**")
        st.caption("Rate = same segment converting differently. "
                   "Mix = volume shifting between segments. They sum to the total.")
        st.dataframe(insights["drivers_by_bu"], hide_index=True, width='stretch')
    with right:
        st.markdown("**Product category**")
        st.dataframe(insights["category_performance"],
                     hide_index=True, width='stretch')
        st.markdown("**Category drivers**")
        st.dataframe(insights["drivers_by_category"],
                     hide_index=True, width='stretch')

    st.markdown("**Weekly trend**")
    tr = insights["revenue_trend"].copy()
    tr["Week Of"] = tr["Enquiry Week"].dt.strftime("%d %b")
    st.line_chart(tr.set_index("Week Of")[["Enquiries", "Delivered"]])
    st.dataframe(tr[["Week Of", "Enquiries", "Delivered", "Conversion %",
                     "Revenue", "Complete"]],
                 hide_index=True, width='stretch')

    lb = insights["conversion"]["loss_breakdown"]
    st.markdown("**Where the lost enquiries go**")
    st.caption("Never quoted means we never even gave a price - a response failure, "
               "and the most fixable part of the loss.")
    st.dataframe(pd.DataFrame([
        {"Outcome": "Never quoted", "Lines": lb["never_quoted"],
         "% of all enquiries": lb["never_quoted_pct_of_all"]},
        {"Outcome": "Quoted but lost", "Lines": lb["quoted_but_lost"],
         "% of all enquiries": lb["quoted_but_lost_pct_of_all"]},
        {"Outcome": "Returned", "Lines": lb["returned"], "% of all enquiries": None},
        {"Outcome": "Still in progress", "Lines": lb["in_progress"], "% of all enquiries": None},
    ]), hide_index=True, width='stretch')

    with st.expander("View the exact system prompt sent to Claude"):
        st.code(system_prompt, language="text")
