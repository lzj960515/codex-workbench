COLUMNS = ("date", "provider", "amount_usd")

def visible_rows(state):
    return state["rows"]

# state 由页面加载器产生，包含 rows 和 load_error；导出尚未实现。
