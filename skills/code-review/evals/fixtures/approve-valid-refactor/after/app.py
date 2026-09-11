def parse_settings(raw):
    mode = raw.get("mode", "normal")
    if not isinstance(mode, str) or mode not in {"normal", "fast"}:
        raise ValueError("unsupported mode")
    return mode


def _retry_limit(mode):
    return {"normal": 3, "fast": 5}[mode]


def run(raw_settings):
    mode = parse_settings(raw_settings)
    return {"attempt_limit": _retry_limit(mode)}
