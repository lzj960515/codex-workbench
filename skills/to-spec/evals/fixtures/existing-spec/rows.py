def visible_rows(state):
    if state.get("error"):
        raise RuntimeError(state["error"])
    return state["page"]
