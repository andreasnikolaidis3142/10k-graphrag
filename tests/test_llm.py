"""LLM client behaviour with a fake HTTP layer (no network): reasoning effort, optional-parameter fallback, truncation retry."""
from tenk_graphrag import llm, config

class Resp:
    def __init__(self, status=200, content="", finish="stop"):
        self.status_code, self.text, self._c, self._f = status, "err", content, finish
    def json(self):
        return {"choices": [{"message": {"content": self._c}, "finish_reason": self._f}]}

def _run(responses, **kw):
    calls = []
    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(json); return responses[min(len(calls) - 1, len(responses) - 1)]
    orig_post, orig_key = llm.requests.post, config.OPENROUTER_API_KEY
    llm.requests.post, config.OPENROUTER_API_KEY = fake_post, "test-key"
    try:
        try: out = llm.chat([{"role": "user", "content": "hi"}], models=["m1"], max_tokens=4000, **kw)
        except RuntimeError as e: out = e
    finally:
        llm.requests.post, config.OPENROUTER_API_KEY = orig_post, orig_key
    return out, calls

def test_requests_json_mode_and_low_reasoning_effort_by_default():
    (text, model), calls = _run([Resp(content='{"a": 1}')], json_mode=True)
    assert calls[0]["response_format"] == {"type": "json_object"} and calls[0]["reasoning"] == {"effort": "low", "exclude": True}
    assert calls[0]["max_tokens"] == 4000 and model == "m1"

def test_a_model_that_rejects_the_optional_parameters_is_retried_without_them():
    (text, _), calls = _run([Resp(status=400), Resp(content='{"a": 1}')], json_mode=True)
    assert len(calls) == 2 and "reasoning" in calls[0] and "reasoning" not in calls[1] and "response_format" not in calls[1]

def test_a_truncated_non_json_reply_is_retried_on_the_same_model_with_a_bigger_budget():
    (text, _), calls = _run([Resp(content='{"summary": "cut o', finish="length"), Resp(content='{"summary": "ok"}')], json_mode=True)
    assert [c["max_tokens"] for c in calls] == [4000, 8000] and llm.extract_json(text) == {"summary": "ok"}
    assert all("reasoning" in c for c in calls)                          # the low-effort setting is kept on the retry

def test_complete_json_is_accepted_even_if_the_model_kept_talking():
    (text, _), calls = _run([Resp(content='{"summary": "ok"} and then some extra thinking', finish="length")], json_mode=True)
    assert len(calls) == 1 and llm.extract_json(text) == {"summary": "ok"}

def test_the_budget_never_exceeds_the_cap_and_the_last_partial_reply_is_still_returned():
    (text, _), calls = _run([Resp(content='{"x": ', finish="length")], json_mode=True)
    assert [c["max_tokens"] for c in calls] == [4000, 8000, 16000] and llm.extract_json(text) is None

TRUNCATED_ANSWER = '{"summary": "ok", "key_numbers": [{"metric": "Total debt", "value": "$37.01B", "fact_id": "F1"}, {"metric": "Net de'

def test_a_truncated_answer_is_not_salvaged_as_its_first_nested_object():
    assert llm.extract_json(TRUNCATED_ANSWER) is None
    assert llm.extract_json('note: {"summary": "ok", "drivers": []}') == {"summary": "ok", "drivers": []}

def test_a_truncated_answer_with_a_complete_nested_item_still_gets_the_bigger_budget():
    (text, _), calls = _run([Resp(content=TRUNCATED_ANSWER, finish="length"), Resp(content='{"summary": "ok"}')], json_mode=True)
    assert [c["max_tokens"] for c in calls] == [4000, 8000] and llm.extract_json(text) == {"summary": "ok"}

def test_free_model_discovery_skips_models_that_do_not_output_text():
    class R:
        def json(self):
            free = {"prompt": "0", "completion": "0"}
            return {"data": [{"id": "a/music:free", "pricing": free, "architecture": {"output_modalities": ["audio"]}},
                             {"id": "b/chat:free", "pricing": free, "architecture": {"output_modalities": ["text"]}},
                             {"id": "d/song-and-lyrics", "pricing": free, "architecture": {"output_modalities": ["text", "audio"]}},
                             {"id": "c/old:free", "pricing": free}]}
    orig_get, orig_fb = llm.requests.get, config.FALLBACK_FREE_MODELS
    llm.requests.get, config.FALLBACK_FREE_MODELS = (lambda *a, **k: R()), []
    llm._FREE_CACHE.clear()
    try: models = llm.list_free_models(refresh=True)
    finally:
        llm.requests.get, config.FALLBACK_FREE_MODELS = orig_get, orig_fb; llm._FREE_CACHE.clear()
    assert "a/music:free" not in models and "d/song-and-lyrics" not in models
    assert "b/chat:free" in models and "c/old:free" in models

def test_reasoning_can_be_switched_off():
    orig = llm.REASONING_EFFORT; llm.REASONING_EFFORT = ""
    try: (_, _), calls = _run([Resp(content='{"a": 1}')], json_mode=True)
    finally: llm.REASONING_EFFORT = orig
    assert "reasoning" not in calls[0]

if __name__ == "__main__":
    from tests.runner import run
    run(__name__)
