"""
agent.py
--------
The conversational layer.

The model's job is narrow and deliberate: read the pre-computed figures in the
system prompt, decide which of them answer the question, and say it in plain
English. It never calculates. Every number it can utter was produced by pandas
in insights.py. This is what makes the answers auditable -- if a figure looks
wrong, it is wrong in the metric layer, not hallucinated in the prose.

PROMPT CACHING
The briefing is identical on every call and is ~3.7k tokens, so it is marked
cacheable. Turns after the first read it from cache at a tenth of the input
price and return noticeably faster. This works only because the prompt is
stable -- the user's question and any timestamp go in `messages`, never into
`system`, or the cached prefix would be invalidated on every request.

OFFLINE MODE
If no ANTHROPIC_API_KEY is present the agent falls back to a deterministic
narrator: keyword-routed, template-written findings over the same computed
metrics. It is NOT an LLM and does not pretend to be -- it cannot handle a
question outside its routes, cannot follow up on a previous answer, and
cannot rephrase. It exists so the pipeline is demonstrable without
credentials, and so an API outage degrades the tool rather than breaking it.
Every answer it gives is labelled as offline.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

try:                                    # Claude
    import anthropic
except ImportError:
    anthropic = None

try:                                    # Gemini
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None
    genai_types = None

try:                                    # optional -- reads a local .env
    from dotenv import load_dotenv
    load_dotenv(C.ROOT / ".env")
except ImportError:
    pass


# =============================================================== offline answerer
class OfflineAnswerer:
    """
    Keyword router over the system prompt's own sections.

    This is not an LLM and does not pretend to be. It finds the section of the
    briefing that matches the question and returns it verbatim, with a short
    lead-in. Honest, fast, and impossible to hallucinate with.
    """

    ROUTES = [
        (r"\bp1\b|call list|urgent|today|priorit|who should|action",
         ["## SALES PRIORITY"], "Here is the priority position."),
        (r"convers|why|driver|rate effect|mix|fell|dropped|improv",
         ["## HEADLINE", "## WHY CONVERSION MOVED"],
         "Here is conversion and what moved it."),
        (r"custom|churn|quiet|lifecycle|new|growing|shrink|slipping|returns?\b",
         ["## CUSTOMER BASE", "## SALES PRIORITY"],
         "Here is how the customer base is moving."),
        (r"region|zone|business unit|gurgaon|noida|tier|insurance|tyre|retail|deliver|speed|slow",
         ["## PERFORMANCE BY SEGMENT"], "Here is performance by segment."),
        (r"categor|batter|paint|oil|spare|product",
         ["## PERFORMANCE BY SEGMENT", "## WHY CONVERSION MOVED"],
         "Here is category performance."),
        (r"virtual|physical|channel",
         ["## PERFORMANCE BY SEGMENT"], "Here is the channel split."),
        (r"trend|week|month|revenue|sales|growth",
         ["## WEEKLY TREND", "## HEADLINE"], "Here is the revenue trend."),
        (r"yesterday|last day|daily|brief|morning",
         ["## MOST RECENT DAY", "## SALES PRIORITY"], "Here is yesterday."),
    ]

    def __init__(self, system_prompt: str, insights: dict = None, flags=None):
        self.sections = self._split(system_prompt)
        self.insights = insights
        self.flags = flags

    @staticmethod
    def _split(prompt: str) -> dict:
        out, name, buf = {}, None, []
        for line in prompt.splitlines():
            if line.startswith("## "):
                if name:
                    out[name] = "\n".join(buf).strip()
                name, buf = line.strip(), [line]
            elif name:
                buf.append(line)
        if name:
            out[name] = "\n".join(buf).strip()
        return out

    def _get(self, prefix: str) -> str:
        for k, v in self.sections.items():
            if k.startswith(prefix):
                return v
        return ""

    NOTE = ("*Offline mode - written by the deterministic narrator, not a "
            "model.*")

    def answer(self, question: str) -> str:
        # Prefer narrated prose; fall back to raw sections only if no
        # finding matches. Tables are a last resort, not the default.
        if self.insights is not None and self.flags is not None:
            try:
                from narrator import answer_offline
                narrated = answer_offline(question, self.insights, self.flags)
                if narrated:
                    return f"{narrated}\n\n{self.NOTE}"
            except Exception:
                pass

        q = question.lower()
        for pattern, keys, lead in self.ROUTES:
            if re.search(pattern, q):
                body = "\n\n".join(filter(None, (self._get(k) for k in keys)))
                return f"**{lead}**  \n{self.NOTE}\n\n{body}"
        return (
            "*(Offline mode.)* I could not match that to a section of the daily "
            "figures. Try asking about conversion, customers at risk, a business "
            "unit, a product category, the weekly trend, or today's call list."
        )


# =============================================================== the agent
class BusinessInsightsAgent:
    def __init__(self, system_prompt: str, api_key: str | None = None,
                 model: str = None, insights: dict = None, flags=None,
                 provider: str = None):
        self.system_prompt = system_prompt
        self.model = model or C.MODEL_ID
        self.history: list[dict] = []
        self.insights = insights
        self.flags = flags
        self._offline = OfflineAnswerer(system_prompt, insights, flags)
        self.last_usage: dict = {}
        self.calls = 0
        self.total_cost = 0.0
        self.total_cached = 0

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.mode = "offline"
        self.status = "No ANTHROPIC_API_KEY found - running in offline mode."

        self.provider = provider or C.LLM_PROVIDER
        if self.provider == "gemini":
            self._init_gemini()
        else:
            self._init_anthropic()

    # ------------------------------------------------------------- providers
    def _init_gemini(self) -> None:
        self.model = C.GEMINI_MODEL
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            self.status = "No GEMINI_API_KEY found - running in offline mode."
            return
        if genai is None:
            self.status = ("GEMINI_API_KEY is set but `google-genai` is not "
                           "installed. Run: pip install google-genai")
            return
        try:
            self.client = genai.Client(api_key=key)
            self.mode = "live"
            self.status = f"Connected to {self.model} (Gemini)."
        except Exception as e:
            self.status = f"Could not initialise the Gemini client: {e}"

    def _init_anthropic(self) -> None:
        self.model = C.MODEL_ID
        # Identity-linked API keys (issued to a user rather than a service)
        # must name the workspace they act in on every request. A plain
        # organisation key does not, so the header is only attached when set.
        self.workspace_id = os.getenv("ANTHROPIC_WORKSPACE_ID")
        if not self.api_key:
            self.status = "No ANTHROPIC_API_KEY found - running in offline mode."
            return
        if anthropic is None:
            self.status = ("ANTHROPIC_API_KEY is set but the `anthropic` "
                           "package is not installed.")
            return
        try:
            headers = ({"anthropic-workspace-id": self.workspace_id}
                       if self.workspace_id else None)
            self.client = anthropic.Anthropic(
                api_key=self.api_key, default_headers=headers
            )
            self.mode = "live"
            self.status = f"Connected to {self.model} (Claude)."
            if self.workspace_id:
                self.status += f" (workspace {self.workspace_id[:14]}...)"
        except Exception as e:
            self.status = f"Could not initialise the Claude client: {e}"

    # ------------------------------------------------------------------ usage
    def _record_usage(self, resp) -> None:
        """
        Track tokens and cost so the running spend is visible in the UI.
        A tool nobody can see the cost of is a tool nobody trusts to leave on.
        """
        u = resp.usage
        read = getattr(u, "cache_read_input_tokens", 0) or 0
        write = getattr(u, "cache_creation_input_tokens", 0) or 0
        fresh = u.input_tokens

        rate_in, rate_out = C.PRICE_PER_MTOK_IN, C.PRICE_PER_MTOK_OUT
        cost = (
            fresh * rate_in                      # uncached input
            + write * rate_in * 1.25             # cache write costs 25% extra
            + read * rate_in * 0.10              # cache read costs 10%
            + u.output_tokens * rate_out
        ) / 1_000_000

        self.last_usage = {
            "input": fresh, "output": u.output_tokens,
            "cache_read": read, "cache_write": write, "cost_usd": cost,
        }
        self.calls += 1
        self.total_cost += cost
        self.total_cached += read

    def usage_summary(self) -> str:
        if not self.calls:
            return "No API calls yet this session."
        saved = self.total_cached * C.PRICE_PER_MTOK_IN * 0.9 / 1_000_000
        return (f"{self.calls} call(s) · ${self.total_cost:.4f} spent · "
                f"{self.total_cached:,} tokens served from cache "
                f"(~${saved:.4f} saved)")

    # ------------------------------------------------------------------ chat
    def ask(self, question: str) -> str:
        self.history.append({"role": "user", "content": question})
        if self.mode != "live":
            answer = self._offline.answer(question)
        elif self.provider == "gemini":
            answer = self._live_gemini(question)
        else:
            answer = self._live_anthropic(question)
        self.history.append({"role": "assistant", "content": answer})
        return answer

    def _live_gemini(self, question: str) -> str:
        """
        Gemini path. Same contract as the Claude path: the briefing goes in
        as system_instruction, the conversation goes in as contents, and the
        model writes prose over numbers it was given rather than computing
        any of its own.

        Caching: Gemini applies implicit context caching automatically on
        repeated prefixes, so the stable briefing is discounted without an
        explicit cache handle. There is no equivalent of Anthropic's
        cache_control to set here.
        """
        try:
            contents = [
                genai_types.Content(
                    role=("model" if m["role"] == "assistant" else "user"),
                    parts=[genai_types.Part(text=m["content"])],
                )
                for m in self.history
            ]
            resp = self.client.models.generate_content(
                model=self.model,
                config=genai_types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    max_output_tokens=C.MAX_TOKENS,
                ),
                contents=contents,
            )
            self._record_usage_gemini(resp)
            text = (resp.text or "").strip()
            if not text:
                return ("The model returned an empty response. Here are the "
                        "figures instead.\n\n" + self._offline.answer(question))
            return text
        except Exception as e:
            name = type(e).__name__
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                return ("Gemini rate limit hit (free tier). Wait a moment and "
                        "ask again.\n\n" + self._offline.answer(question))
            if "404" in msg:
                return (f"Model `{self.model}` is not available on this key. "
                        "Check GEMINI_MODEL in config.py.")
            return (f"Gemini call failed ({name}). Here are the figures "
                    f"instead.\n\n{self._offline.answer(question)}")

    def _record_usage_gemini(self, resp) -> None:
        u = getattr(resp, "usage_metadata", None)
        if u is None:
            return
        pin = getattr(u, "prompt_token_count", 0) or 0
        out = getattr(u, "candidates_token_count", 0) or 0
        cached = getattr(u, "cached_content_token_count", 0) or 0
        cost = (pin * C.GEMINI_PRICE_IN + out * C.GEMINI_PRICE_OUT) / 1_000_000
        self.last_usage = {"input": pin, "output": out,
                           "cache_read": cached, "cache_write": 0,
                           "cost_usd": cost}
        self.calls += 1
        self.total_cost += cost
        self.total_cached += cached

    def _live_anthropic(self, question: str) -> str:
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=C.MAX_TOKENS,
                # The briefing is byte-identical on every call, which is
                # exactly what prompt caching is for. It is ~3.7k tokens --
                # comfortably over the ~1k minimum cacheable prefix -- so
                # every turn after the first reads it from cache at a tenth
                # of the input price, and returns faster.
                #
                # This only works because the prompt is STABLE. If a
                # timestamp or the user's question were interpolated into
                # it, the prefix would change every call and nothing would
                # ever cache. That is why the question goes in `messages`
                # and never into `system`.
                system=[{
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }],
                messages=self.history,
            )
            self._record_usage(resp)
            return "".join(b.text for b in resp.content if b.type == "text").strip()

        # Most specific first, so retryable and non-retryable stay distinguishable.
        except anthropic.NotFoundError:
            return (f"Model `{self.model}` was not found. Check MODEL_ID in config.py.")
        except anthropic.AuthenticationError:
            return "The API key was rejected. Check ANTHROPIC_API_KEY in your .env file."
        except anthropic.RateLimitError:
            return "Rate limited by the API. Wait a moment and ask again."
        except anthropic.BadRequestError as e:
            msg = str(e).lower()
            if "credit balance" in msg or "too low" in msg:
                return ("The Anthropic account has no credits, so I cannot "
                        "write an answer. Add credits under Plans & Billing "
                        "in the Console. Here are the underlying figures in "
                        "the meantime.\n\n" + self._offline.answer(question))
            if "workspace" in str(e).lower():
                return ("This API key is identity-linked and needs a workspace "
                        "ID. Add `ANTHROPIC_WORKSPACE_ID=wrkspc_...` to your "
                        ".env (find it in the Console URL when you open your "
                        "workspace), or generate a plain organisation key "
                        "instead.")
            return f"The API rejected the request (400): {e}"
        except anthropic.InternalServerError as e:
            # 500 / 529 -- Anthropic side. Retryable; fall back rather than fail.
            return ("The API is overloaded right now. Here are the underlying "
                    "figures instead.\n\n" + self._offline.answer(question))
        except anthropic.APIStatusError as e:
            return f"The API returned {e.status_code}: {e.message}"
        except anthropic.APIConnectionError:
            return ("Could not reach the API. Here are the raw figures instead.\n\n"
                    + self._offline.answer(question))
        except Exception as e:                       # never break the UI
            return f"Unexpected error: {type(e).__name__}: {e}"

    # ------------------------------------------------------------- one-shot
    def brief(self, request: str) -> str:
        """
        Generate the morning brief. Deliberately does NOT touch self.history --
        the brief is a standalone product, not a conversation turn, and mixing
        it into the chat log would skew every later answer toward it.
        """
        if self.mode != "live":
            if self.insights is not None and self.flags is not None:
                from narrator import morning_brief
                return (morning_brief(self.insights, self.flags)
                        + "\n\n" + OfflineAnswerer.NOTE)
            return self._offline.answer("morning brief")
        if self.provider == "gemini":
            try:
                resp = self.client.models.generate_content(
                    model=self.model,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        max_output_tokens=1500),
                    contents=request)
                self._record_usage_gemini(resp)
                return (resp.text or "").strip()
            except Exception as e:
                return (f"Could not generate the brief ({type(e).__name__}).\n\n"
                        + self._offline.answer("morning brief"))
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=1200,
                system=[{
                    "type": "text",
                    "text": self.system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }],
                messages=[{"role": "user", "content": request}],
            )
            self._record_usage(resp)
            return "".join(b.text for b in resp.content if b.type == "text").strip()
        except Exception as e:
            return f"Could not generate the brief ({type(e).__name__}). {e}"

    def reset(self) -> None:
        self.history = []


# =============================================================== cli
if __name__ == "__main__":
    from build_prompt import build_system_prompt, build_morning_brief_request
    from insights import build_all

    from priority_flag import assign_priority
    I = build_all()
    flags = assign_priority(I)
    agent = BusinessInsightsAgent(build_system_prompt(I, flags),
                                  insights=I, flags=flags)

    print("=" * 70)
    print(" BUSINESS INSIGHTS AGENT")
    print(f" {agent.status}")
    print("=" * 70)

    if len(sys.argv) > 1:
        if sys.argv[1] == "--brief":
            print(agent.brief(build_morning_brief_request(I)))
        else:
            print(agent.ask(" ".join(sys.argv[1:])))
        sys.exit()

    print(" Ask a question, or 'quit'.\n")
    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in {"quit", "exit", "q", ""}:
            break
        print(f"\n{agent.ask(q)}\n")
