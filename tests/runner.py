"""Tiny test runner so `python3 -m tests.test_retrieval` prints results without needing pytest."""
import inspect, pathlib, sys, tempfile, traceback

class _MonkeyPatch:
    def __init__(self): self._undo = []
    def setattr(self, obj, name, val):
        self._undo.append((obj, name, getattr(obj, name))); setattr(obj, name, val)
    def undo(self):
        for o, n, v in reversed(self._undo): setattr(o, n, v)

def run(module_name):
    mod = sys.modules[module_name]
    passed = failed = 0
    for name, fn in inspect.getmembers(mod, inspect.isfunction):
        if not name.startswith("test_") or fn.__module__ != module_name:
            continue
        params, kw, mp = inspect.signature(fn).parameters, {}, _MonkeyPatch()
        if "tmp_path" in params: kw["tmp_path"] = pathlib.Path(tempfile.mkdtemp())
        if "monkeypatch" in params: kw["monkeypatch"] = mp
        try:
            fn(**kw); print(f"PASS  {name}"); passed += 1
        except Exception:
            print(f"FAIL  {name}"); traceback.print_exc(limit=4); failed += 1
        finally:
            mp.undo()
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
