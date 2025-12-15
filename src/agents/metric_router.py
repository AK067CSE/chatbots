# src/agents/metric_router.py
from src.sql import templates as T
from src.agents.intent_classifier import detect_intent
from src.agents.entity_extractor import extract_entities

def build_sql_from_question(question: str) -> tuple[str, dict]:
    intent = detect_intent(question)
    e = extract_entities(question)

    # Default compare years if missing (common in your file: 2024/2025)
    year_1 = e.year
    year_2 = e.year_2

    meta = {"intent": intent, "entities": e.__dict__}

    if intent == "sales_total":
        return T.sql_sales_total(brand=e.brand, month=e.month, year=year_1), meta

    if intent == "sales_yoy":
        if year_1 is None and year_2 is None:
            year_1, year_2 = 2024, 2025
        elif year_2 is None:
            year_2 = year_1 - 1
        return T.sql_sales_yoy(brand=e.brand, month=e.month, year_1=year_1, year_2=year_2), meta

    if intent == "sales_summary":
        gb = e.group_by or "brand"
        return T.sql_sales_summary(group_by=gb, brand=e.brand, month=e.month, year=year_1, top_n=e.top_n), meta

    if intent == "active_store_total":
        return T.sql_active_store_total(brand=e.brand, month=e.month, year=year_1), meta

    if intent == "active_store_yoy":
        if year_1 is None and year_2 is None:
            year_1, year_2 = 2024, 2025
        elif year_2 is None:
            year_2 = year_1 - 1
        return T.sql_active_store_yoy(brand=e.brand, month=e.month, year_1=year_1, year_2=year_2), meta

    if intent == "active_store_summary":
        gb = e.group_by or "brand"
        return T.sql_active_store_summary(group_by=gb, brand=e.brand, month=e.month, year=year_1, top_n=e.top_n), meta

    return "", meta
