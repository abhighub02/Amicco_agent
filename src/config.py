"""
Central configuration. Every tunable business rule lives here so that a
non-technical reviewer can find and change a threshold in one place.
"""
from pathlib import Path

# ---------------------------------------------------------------- paths
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
RAW_FILE = DATA_DIR / "Raw_Data.xlsx"
CLEAN_FILE = OUTPUT_DIR / "clean_data.parquet"
CLEAN_CSV = OUTPUT_DIR / "clean_data.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- LLM
# Model is pinned here and nowhere else. Swap to "claude-opus-5" for the
# current flagship model; the rest of the code is unchanged.
MODEL_ID = "claude-sonnet-4-6"
MAX_TOKENS = 4000

# ---------------------------------------------------------------- status vocab
DELIVERED_STATUSES = {"Delivered"}
PARTIAL_STATUSES = {"Partially Delivered"}
RETURN_STATUSES = {"Returned", "Return Requested", "Return Picked"}
IN_PROGRESS_STATUSES = {"Delivery In-Progress"}
NOT_DELIVERED_STATUSES = {"Not Delivered"}

# ---------------------------------------------------------------- business rules
# Deliveries are effectively same-day (median 0 days, p95 = 3 days). Enquiries
# raised inside this window have not had a fair chance to convert yet, so they
# are reported separately rather than dragging the headline conversion down.
MATURITY_DAYS = 3

# Real data begins 22-Jun-2026. The file technically starts 04-Jun but the
# first three weeks hold 21 rows in total -- a partial extract, not a slow
# month. Comparing against it would invent a fake 600% growth story.
DATA_START_CUTOFF = "2026-06-22"

# Customer lifecycle / churn thresholds
NEW_CUSTOMER_DAYS = 30          # first ever enquiry within this window  -> New
GONE_QUIET_DAYS = 30            # no enquiry for this long               -> Gone Quiet
MID_VALUE_QUIET_DAYS = 20       # softer quiet threshold for P2
CHURN_STREAK_HIGH = 6           # consecutive non-deliveries -> P1
CHURN_STREAK_WATCH = 3          # consecutive non-deliveries -> P2
REVENUE_DROP_P1 = 0.50          # >50% month-on-month revenue fall -> P1
RETURN_RATE_P2 = 0.20           # >20% of this month's lines returned -> P2
GROWTH_BAND = 0.15              # +/-15% month-on-month = "Steady"

# Grain for the consecutive non-delivery streak.
#   "order" -> consecutive ORDERS where nothing at all was delivered.
#   "line"  -> consecutive LINE ITEMS not delivered.
# Order grain is the default: it is what a person means by "six in a row",
# and it does not punish a customer for one large multi-line order that fell
# through. At a threshold of 6, line grain flags 107 of 330 customers versus
# 60 on order grain -- a 32% P1 rate is a report, not a priority list.
STREAK_GRAIN = "order"

# Hard ceiling on the P1 list. If everyone is urgent, nobody is.
MAX_P1_CUSTOMERS = 25

# ---------------------------------------------------------------- silence
# A run of non-deliveries is OUR failure. It only becomes a sales emergency
# when the customer stops calling afterwards -- that is the moment they give
# up on us. So the P1 rule is "undelivered streak AND then silence", not
# "undelivered streak" on its own.
#
# Silence is judged against the customer's OWN ordering rhythm. A workshop
# that orders daily going quiet for 10 days is alarming; one that orders
# monthly, 10 days is nothing. Absolute-day thresholds get this wrong in both
# directions.
SILENCE_GAP_MULTIPLIER = 3.0    # silent if gap > this x their median gap
SILENCE_MIN_DAYS = 10           # ...but never call it silence sooner than this

# ---------------------------------------------------------------- pricing
# claude-sonnet-4-6 list price, USD per million tokens. Used only to show the
# running cost in the UI -- a tool whose cost is invisible is a tool nobody
# trusts to leave switched on.
PRICE_PER_MTOK_IN = 3.00
PRICE_PER_MTOK_OUT = 15.00

# ---------------------------------------------------------------- provider
# Which LLM writes the answers. Both implementations stay live in agent.py
# and are selected here rather than commented out -- commented-out code rots,
# and Anthropic is expected back the moment the account has credits. Flip this
# one string to switch; nothing else changes.
#   "gemini"    -> Google Gemini (currently primary: Anthropic has no credits)
#   "anthropic" -> Claude
LLM_PROVIDER = "gemini"

# gemini-1.5-flash and gemini-2.5-flash are both retired for new users; 3.6 is
# the current Flash generation. Verified against models.list on this key.
GEMINI_MODEL = "gemini-3.6-flash"

# Gemini Flash pricing, USD per million tokens (free tier available).
GEMINI_PRICE_IN = 0.075
GEMINI_PRICE_OUT = 0.30
