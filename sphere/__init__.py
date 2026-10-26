# Key convenience: if ANTHROPIC_API_KEY is not exported in this window, read it from the private file ~/.sphere_key (one line, chmod 600).
import os as _os
if not _os.environ.get("ANTHROPIC_API_KEY"):
    try:
        _p = _os.path.expanduser("~/.sphere_key")
        if _os.path.exists(_p):
            _k = open(_p).read().strip()
            if _k: _os.environ["ANTHROPIC_API_KEY"] = _k
    except Exception:
        pass
