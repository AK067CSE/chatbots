# src/sql/templates.py

MONTH_MAP = {
    "JANUARY": "JAN", "FEBRUARY": "FEB", "MARCH": "MAR", "APRIL": "APR",
    "MAY": "MAY", "JUNE": "JUN", "JULY": "JUL", "AUGUST": "AUG",
    "SEPTEMBER": "SEP", "OCTOBER": "OCT", "NOVEMBER": "NOV", "DECEMBER": "DEC",
    "JAN": "JAN", "FEB": "FEB", "MAR": "MAR", "APR": "APR", "JUN": "JUN",
    "JUL": "JUL", "AUG": "AUG", "SEP": "SEP", "OCT": "OCT", "NOV": "NOV", "DEC": "DEC",
}

# GROUP_BY_ALLOWED = {
#     "brand": "Brand",
#     "category": "Category",
#     "segment": "Segment",
#     "country": "Country",
#     "city": "City",
#     "area": "Area",
#     "channel": "Channel",
#     "sub channel": "Sub Channel",
#     "supplier": "Supplier",
#     "item": "Item",
#     "month": "Month",
#     "year": "Year",
# }

# def norm_month(m: str | None) -> str | None:
#     if not m:
#         return None
#     k = str(m).strip().upper()
#     return MONTH_MAP.get(k, k[:3])

# def norm_group_by(g: str | None) -> str | None:
#     if not g:
#         return None
#     k = str(g).strip().lower()
#     return GROUP_BY_ALLOWED.get(k, None)

# # -------------------------
# # SALES templates
# # -------------------------

# def sql_sales_total(*, brand=None, month=None, year=None):
#     wh = []
#     if brand:
#         wh.append(f"Brand = '{brand}'")
#     if month:
#         wh.append(f"Month = '{norm_month(month)}'")
#     if year:
#         wh.append(f"Year = {int(year)}")

#     where = ("WHERE " + " AND ".join(wh)) if wh else ""
#     return f"""
# SELECT SUM(Value) AS total_sales
# FROM sales
# {where}
# """.strip()

# def sql_sales_yoy(*, brand=None, month=None, year_1=None, year_2=None):
#     if year_1 is None or year_2 is None:
#         raise ValueError("sales_yoy requires year_1 and year_2")

#     wh = [f"Year IN ({int(year_1)}, {int(year_2)})"]
#     if brand:
#         wh.append(f"Brand = '{brand}'")
#     if month:
#         wh.append(f"Month = '{norm_month(month)}'")

#     where = "WHERE " + " AND ".join(wh)
#     return f"""
# SELECT Year, SUM(Value) AS total_sales
# FROM sales
# {where}
# GROUP BY Year
# ORDER BY Year
# """.strip()

# def sql_sales_summary(*, group_by, brand=None, month=None, year=None, top_n=None):
#     gb = norm_group_by(group_by)
#     if not gb:
#         raise ValueError(f"Unsupported group_by: {group_by}")

#     wh = []
#     if brand:
#         wh.append(f"Brand = '{brand}'")
#     if month:
#         wh.append(f"Month = '{norm_month(month)}'")
#     if year:
#         wh.append(f"Year = {int(year)}")

#     where = ("WHERE " + " AND ".join(wh)) if wh else ""
#     limit = f"LIMIT {int(top_n)}" if top_n else ""

#     return f"""
# SELECT {gb} AS group_key, SUM(Value) AS total_sales
# FROM sales
# {where}
# GROUP BY {gb}
# ORDER BY total_sales DESC
# {limit}
# """.strip()

# # -------------------------
# # ACTIVE STORE templates
# # Active store = unique stores invoiced (distinct customer account)
# # -------------------------

# ACTIVE_STORE_COL = '"Customer Account Number"'  # quoted because of spaces

# def sql_active_store_total(*, brand=None, month=None, year=None):
#     wh = []
#     if brand:
#         wh.append(f"Brand = '{brand}'")
#     if month:
#         wh.append(f"Month = '{norm_month(month)}'")
#     if year:
#         wh.append(f"Year = {int(year)}")
#     where = ("WHERE " + " AND ".join(wh)) if wh else ""

#     return f"""
# SELECT COUNT(DISTINCT {ACTIVE_STORE_COL}) AS active_stores
# FROM sales
# {where}
# """.strip()

# def sql_active_store_yoy(*, brand=None, month=None, year_1=None, year_2=None):
#     if year_1 is None or year_2 is None:
#         raise ValueError("active_store_yoy requires year_1 and year_2")

#     wh = [f"Year IN ({int(year_1)}, {int(year_2)})"]
#     if brand:
#         wh.append(f"Brand = '{brand}'")
#     if month:
#         wh.append(f"Month = '{norm_month(month)}'")

#     where = "WHERE " + " AND ".join(wh)
#     return f"""
# SELECT Year, COUNT(DISTINCT {ACTIVE_STORE_COL}) AS active_stores
# FROM sales
# {where}
# GROUP BY Year
# ORDER BY Year
# """.strip()

# def sql_active_store_summary(*, group_by, brand=None, month=None, year=None, top_n=None):
#     gb = norm_group_by(group_by)
#     if not gb:
#         raise ValueError(f"Unsupported group_by: {group_by}")

#     wh = []
#     if brand:
#         wh.append(f"Brand = '{brand}'")
#     if month:
#         wh.append(f"Month = '{norm_month(month)}'")
#     if year:
#         wh.append(f"Year = {int(year)}")

#     where = ("WHERE " + " AND ".join(wh)) if wh else ""
#     limit = f"LIMIT {int(top_n)}" if top_n else ""

#     return f"""
# SELECT {gb} AS group_key, COUNT(DISTINCT {ACTIVE_STORE_COL}) AS active_stores
# FROM sales
# {where}
# GROUP BY {gb}
# ORDER BY active_stores DESC
# {limit}
# """.strip()
# src/sql/templates.py

# -------------------------
# Month normalization
# -------------------------

MONTH_MAP = {
    "JANUARY": "JAN", "FEBRUARY": "FEB", "MARCH": "MAR", "APRIL": "APR",
    "MAY": "MAY", "JUNE": "JUN", "JULY": "JUL", "AUGUST": "AUG",
    "SEPTEMBER": "SEP", "OCTOBER": "OCT", "NOVEMBER": "NOV", "DECEMBER": "DEC",

    # already-normalized
    "JAN": "JAN", "FEB": "FEB", "MAR": "MAR", "APR": "APR",
    "MAY": "MAY", "JUN": "JUN", "JUL": "JUL", "AUG": "AUG",
    "SEP": "SEP", "OCT": "OCT", "NOV": "NOV", "DEC": "DEC",
}

# -------------------------
# GROUP BY support (CRITICAL FIX HERE)
# -------------------------

# GROUP_BY_ALLOWED = {
#     "brand": "Brand",
#     "category": "Category",
#     "segment": "Segment",

#     # ✅ FIX: region support
#     "region": "Region",

#     "country": "Country",
#     "city": "City",
#     "area": "Area",
#     "channel": "Channel",
#     "sub channel": "Sub Channel",
#     "supplier": "Supplier",
#     "item": "Item",
#     "month": "Month",
#     "year": "Year",
# }
# GROUP_BY_ALLOWED = {
#     "brand": "Brand",
#     "category": "Category",
#     "segment": "Segment",

#     # ✅ Correct region mapping (CRITICAL FIX)
#     "region": "Retailer Group",

#     "country": "Country",
#     "city": "City",
#     "area": "Area",
#     "channel": "Agency",
#     "sub channel": "Retailer Sub Group",
#     "supplier": "Supplier",
#     "item": "Item",
#     "month": "Month",
#     "year": "Year",
# }
GROUP_BY_ALLOWED = {
    "brand": "Brand",
    "category": "Category",
    "segment": "Segment",

    # ✅ FIXED: quoted columns with spaces
    "region": '"Retailer Group"',
    "channel": "Agency",
    "sub channel": '"Retailer Sub Group"',
    "active": '"Customer Account Number"',  # For active stores

    "supplier": "Supplier",
    "item": "Item",
    "month": "Month",
    "year": "Year",
}


# -------------------------
# Normalizers
# -------------------------

def norm_month(m: str | None) -> str | None:
    if not m:
        return None
    k = str(m).strip().upper()
    return MONTH_MAP.get(k, k[:3])


def norm_group_by(g: str | None) -> str | None:
    if not g:
        return None
    k = str(g).strip().lower()
    return GROUP_BY_ALLOWED.get(k)

# =========================================================
# SALES SQL TEMPLATES
# =========================================================

def sql_sales_total(*, brand=None, month=None, year=None):
    wh = []

    if brand:
        wh.append(f"Brand = '{brand}'")
    if month:
        wh.append(f"Month = '{norm_month(month)}'")
    if year:
        wh.append(f"Year = {int(year)}")

    where = "WHERE " + " AND ".join(wh) if wh else ""

    return f"""
SELECT SUM(Value) AS total_sales
FROM sales
{where}
""".strip()


def sql_sales_yoy(*, brand=None, month=None, year_1=None, year_2=None):
    if year_1 is None or year_2 is None:
        raise ValueError("sales_yoy requires year_1 and year_2")

    wh = [f"Year IN ({int(year_1)}, {int(year_2)})"]

    if brand:
        wh.append(f"Brand = '{brand}'")
    if month:
        wh.append(f"Month = '{norm_month(month)}'")

    where = "WHERE " + " AND ".join(wh)

    return f"""
SELECT Year, SUM(Value) AS total_sales
FROM sales
{where}
GROUP BY Year
ORDER BY Year
""".strip()


def sql_sales_summary(*, group_by, brand=None, month=None, year=None, top_n=None):
    gb = norm_group_by(group_by)
    if not gb:
        raise ValueError(f"Unsupported group_by: {group_by}")

    wh = []

    if brand:
        wh.append(f"Brand = '{brand}'")
    if month:
        wh.append(f"Month = '{norm_month(month)}'")
    if year:
        wh.append(f"Year = {int(year)}")

    where = "WHERE " + " AND ".join(wh) if wh else ""
    limit = f"LIMIT {int(top_n)}" if top_n else ""

    return f"""
SELECT {gb} AS group_key, SUM(Value) AS total_sales
FROM sales
{where}
GROUP BY {gb}
ORDER BY total_sales DESC
{limit}
""".strip()

# =========================================================
# ACTIVE STORE SQL TEMPLATES
# Active Store = Unique invoiced stores
# =========================================================

ACTIVE_STORE_COL = '"Customer Account Number"'


def sql_active_store_total(*, brand=None, month=None, year=None):
    wh = []

    if brand:
        wh.append(f"Brand = '{brand}'")
    if month:
        wh.append(f"Month = '{norm_month(month)}'")
    if year:
        wh.append(f"Year = {int(year)}")

    where = "WHERE " + " AND ".join(wh) if wh else ""

    return f"""
SELECT COUNT(DISTINCT {ACTIVE_STORE_COL}) AS active_stores
FROM sales
{where}
""".strip()


def sql_active_store_yoy(*, brand=None, month=None, year_1=None, year_2=None):
    if year_1 is None or year_2 is None:
        raise ValueError("active_store_yoy requires year_1 and year_2")

    wh = [f"Year IN ({int(year_1)}, {int(year_2)})"]

    if brand:
        wh.append(f"Brand = '{brand}'")
    if month:
        wh.append(f"Month = '{norm_month(month)}'")

    where = "WHERE " + " AND ".join(wh)

    return f"""
SELECT Year, COUNT(DISTINCT {ACTIVE_STORE_COL}) AS active_stores
FROM sales
{where}
GROUP BY Year
ORDER BY Year
""".strip()


def sql_active_store_summary(*, group_by, brand=None, month=None, year=None, top_n=None):
    gb = norm_group_by(group_by)
    if not gb:
        raise ValueError(f"Unsupported group_by: {group_by}")

    wh = []

    if brand:
        wh.append(f"Brand = '{brand}'")
    if month:
        wh.append(f"Month = '{norm_month(month)}'")
    if year:
        wh.append(f"Year = {int(year)}")

    where = "WHERE " + " AND ".join(wh) if wh else ""
    limit = f"LIMIT {int(top_n)}" if top_n else ""

    return f"""
SELECT {gb} AS group_key, COUNT(DISTINCT {ACTIVE_STORE_COL}) AS active_stores
FROM sales
{where}
GROUP BY {gb}
ORDER BY active_stores DESC
{limit}
""".strip()

# --------------------------------------------------
# Mapping of template keys to callables for use by agents
# --------------------------------------------------
SQL_TEMPLATES = {
    "total_sales": sql_sales_total,
    "sales_yoy": sql_sales_yoy,
    "sales_summary": sql_sales_summary,
    "active_store_total": sql_active_store_total,
    "active_store_yoy": sql_active_store_yoy,
    "active_store_summary": sql_active_store_summary,
}
