# src/agents/entity_extractor.py
import re
from dataclasses import dataclass

MONTH_WORDS = r"(jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)"
YEAR_RE = r"(20\d{2})"

@dataclass
class Entities:
    brand: str | None = None
    month: str | None = None
    year: int | None = None
    year_2: int | None = None
    group_by: str | None = None
    top_n: int | None = None

def extract_entities(q: str) -> Entities:
    text = q.strip()

    # years
    years = [int(y) for y in re.findall(YEAR_RE, text)]
    year = years[0] if len(years) >= 1 else None
    year_2 = years[1] if len(years) >= 2 else None

    # month
    m = re.search(MONTH_WORDS, text, re.IGNORECASE)
    month = m.group(0) if m else None

    # top N
    tn = re.search(r"\btop\s+(\d+)\b", text, re.IGNORECASE)
    top_n = int(tn.group(1)) if tn else None

    # group by - FIXED: Handle "by sales" = group by brand
    # "Top 5 brands by sales" means group_by = brand (default aggregation)
    gb = None
    gb_match = re.search(r"\bby\s+([a-zA-Z]+)", text, re.IGNORECASE)
    if gb_match:
        raw_gb = gb_match.group(1).strip().lower()
        # Map metric words (sales, revenue) to dimension (brand)
        if raw_gb in ("sales", "revenue", "value", "amount"):
            gb = "brand"  # Default grouping when user says "by sales"
        else:
            gb = raw_gb

    # brand heuristic: if user says "brand X" or just a capitalized token we’ll leave it None here.
    # We'll set brand later using DB distinct values (next step).
    brand = None
    b1 = re.search(r"\bbrand\s+([A-Za-z0-9 &\-\_]+)", text, re.IGNORECASE)
    if b1:
        brand = b1.group(1).strip()

    return Entities(
        brand=brand,
        month=month,
        year=year,
        year_2=year_2,
        group_by=gb,
        top_n=top_n,
    )
