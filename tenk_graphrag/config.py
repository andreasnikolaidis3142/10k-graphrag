"""Central configuration. Everything can be overridden with environment variables."""
import os
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_BASE = os.getenv("OPENROUTER_BASE", "https://openrouter.ai/api/v1")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "")

# Free model ids on OpenRouter change often. We (1) try auto-discovery of every model whose
# pricing is 0 via GET /models and (2) fall back to this list. Override with FREE_MODELS="a:free,b:free".
FALLBACK_FREE_MODELS = [m.strip() for m in os.getenv("FREE_MODELS", "").split(",") if m.strip()] or [
    "deepseek/deepseek-chat-v3-0324:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen-2.5-72b-instruct:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
]
# substrings that rank a discovered free model higher (bigger / better at instruction following)
MODEL_PREFERENCE = ["deepseek", "llama-3.3", "70b", "qwen", "gemma-3", "mistral"]

CACHE_DIR = os.getenv("TENK_CACHE", ".tenk_cache")
INFLECTION_THRESHOLD = 0.25      # same idea as the Reddit post: 25% vs local average
NARRATIVE_TOLERANCE_REL = 0.006  # 0.6% relative tolerance when matching text <-> table numbers
