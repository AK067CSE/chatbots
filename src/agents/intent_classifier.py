# src/agents/intent_classifier.py

def detect_intent(q: str) -> str:
    t = q.lower()

    # charts/tables
    if any(x in t for x in ["chart", "plot", "graph", "trend", "line chart", "bar chart"]):
        return "chart"
    if any(x in t for x in ["table", "show rows", "list "]):
        return "table"

    # active stores
    if any(x in t for x in ["active store", "active stores", "unique stores", "stores invoiced"]):
        if any(x in t for x in ["compare", "vs", "versus", "yoy", "last year"]):
            return "active_store_yoy"
        if "by " in t:
            return "active_store_summary"
        return "active_store_total"

    # sales
    if any(x in t for x in ["sales", "revenue", "value"]):
        if any(x in t for x in ["compare", "vs", "versus", "yoy", "last year"]):
            return "sales_yoy"
        if "by " in t or any(x in t for x in ["summarize", "breakdown"]):
            return "sales_summary"
        return "sales_total"

    # “strategy” style goes to hybrid later
    if any(x in t for x in ["why", "how", "improve", "strategy", "recommend", "suggest"]):
        return "hybrid"

    return "unknown"
