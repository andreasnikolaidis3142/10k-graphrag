"""OpenRouter client restricted to FREE models, with auto-discovery, fallback chain and robust JSON parsing."""
import json, logging, re, time, os
import requests
from . import config

log = logging.getLogger("tenk_graphrag.llm")
DEFAULT_MAX_TOKENS = int(os.getenv("TENK_MAX_TOKENS", "6000"))   # reasoning ("thinking") tokens count as OUTPUT tokens
MAX_TOKENS_CAP = int(os.getenv("TENK_MAX_TOKENS_CAP", "16000"))  # a truncated reply is retried with double the budget, up to this
REASONING_EFFORT = os.getenv("TENK_REASONING_EFFORT", "low")     # OpenRouter reasoning.effort; "" = do not send it

_FREE_CACHE = {}

def list_free_models(refresh=False):
    """GET /models and keep those whose prompt+completion price is 0, ranked by MODEL_PREFERENCE + context length."""
    if _FREE_CACHE and not refresh:
        return _FREE_CACHE["m"]
    models = []
    try:
        r = requests.get(f"{config.OPENROUTER_BASE}/models", timeout=20)
        for m in r.json().get("data", []):
            p = m.get("pricing", {})
            if str(p.get("prompt", "1")) in ("0", "0.0") and str(p.get("completion", "1")) in ("0", "0.0") \
                    and set((m.get("architecture") or {}).get("output_modalities") or ["text"]) == {"text"}:   # no music/image generators
                models.append(m)
    except Exception:
        pass
    def score(m):
        mid = m["id"].lower()
        pref = sum(1 for i, k in enumerate(config.MODEL_PREFERENCE) if k in mid) * 10
        return -(pref + min(m.get("context_length", 0), 128000) / 20000)
    ids = [m["id"] for m in sorted(models, key=score) if ":free" in m["id"] or True]
    # user-supplied / fallback list always first-class citizens
    ordered = [m for m in config.FALLBACK_FREE_MODELS if (not ids or m in ids)] + [m for m in ids if m not in config.FALLBACK_FREE_MODELS]
    _FREE_CACHE["m"] = ordered or config.FALLBACK_FREE_MODELS
    return _FREE_CACHE["m"]

def extract_json(text):
    """Pull the first JSON object out of a model reply (handles ```json fences and chatter)."""
    if not text: return None
    t = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try: return json.loads(t)
    except Exception: pass
    start = t.find("{")
    while start != -1:
        depth, end = 0, None
        for i in range(start, len(t)):
            depth += (t[i] == "{") - (t[i] == "}")
            if depth == 0:
                end = i; break
        if end is None:
            return None                      # truncated outer object: never salvage one of its nested items as "the answer"
        try: return json.loads(t[start:end + 1])
        except Exception: start = t.find("{", end + 1)      # skip PAST the broken object, not into it
    return None

def chat(messages, json_mode=False, temperature=0.1, max_tokens=None, models=None, retries_per_model=3, verbose=False):
    """Try each free model in order. Returns (text, model_id). Raises RuntimeError if all fail.
    - asks for JSON mode and LOW reasoning effort (extras are dropped for a model that rejects them)
    - a reply cut off by the token limit (finish_reason == "length") that is not valid JSON is retried on the SAME model
      with double the budget (up to MAX_TOKENS_CAP) instead of wasting a call on another model."""
    if not config.OPENROUTER_API_KEY:
        raise RuntimeError("Set OPENROUTER_API_KEY (free key from openrouter.ai) to use the LLM layer.")
    headers = {"Authorization": f"Bearer {config.OPENROUTER_API_KEY}", "Content-Type": "application/json",
               "HTTP-Referer": os.getenv("OPENROUTER_REFERER", "https://localhost"), "X-Title": "tenk-graphrag"}
    base_budget = max_tokens or DEFAULT_MAX_TOKENS
    last = None
    for model in (models or list_free_models()):
        budget, use_extras = base_budget, True
        for attempt in range(retries_per_model):
            body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": budget}
            if use_extras:
                if json_mode:
                    body["response_format"] = {"type": "json_object"}              # some free models reject it
                if REASONING_EFFORT:
                    body["reasoning"] = {"effort": REASONING_EFFORT, "exclude": True}   # thinking tokens eat the output budget
            try:
                r = requests.post(f"{config.OPENROUTER_BASE}/chat/completions", headers=headers, json=body, timeout=120)
                if r.status_code == 429:
                    time.sleep(2 + attempt * 3); last = "429 rate limited"; continue
                if r.status_code >= 400:
                    last = f"{r.status_code} {r.text[:200]}"
                    if r.status_code in (400, 422) and use_extras:
                        use_extras = False; continue                                 # retry without the optional parameters
                    break
                choice = (r.json().get("choices") or [{}])[0]
                content = choice.get("message", {}).get("content") or ""
                if choice.get("finish_reason") == "length":
                    log.warning("%s hit max_tokens=%d, so the answer may be cut off.", model, budget)
                    if json_mode and extract_json(content) is None and budget < MAX_TOKENS_CAP:
                        budget = min(budget * 2, MAX_TOKENS_CAP); last = "truncated"; continue     # same model, bigger budget
                if content.strip():
                    if verbose: print(f"[llm] {model}")
                    return content, model
                last = "empty completion"
            except requests.RequestException as e:
                last = str(e)
    raise RuntimeError(f"All free models failed. Last error: {last}")

def chat_json(messages, **kw):
    text, model = chat(messages, json_mode=True, **kw)
    obj = extract_json(text)
    if obj is None:                                             # one repair attempt
        text, model = chat(messages + [{"role": "assistant", "content": text},
                                       {"role": "user", "content": "Return ONLY the JSON object, no prose, no markdown fences."}], **kw)
        obj = extract_json(text)
    return obj, model
