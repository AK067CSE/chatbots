# src/insights/insight_builder.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd

from src.db.duckdb_client import DuckDBClient


MONTH_ORDER = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]


@dataclass
class Insight:
    text: str
    meta: Dict[str, Any]


class InsightBuilder:
    """
    Builds *derived business insights* from DuckDB tables.
    These insights are perfect for RAG (not raw rows).
    """

    def __init__(self, db: Optional[DuckDBClient] = None):
        self.db = db or DuckDBClient()

    # -------------------------
    # Helpers
    # -------------------------
    def _years_in_sales(self) -> List[int]:
        df = self.db.fetchdf("SELECT DISTINCT Year FROM sales ORDER BY Year")
        return [int(x) for x in df["Year"].dropna().tolist()]

    def _normalize_month(self, s: pd.Series) -> pd.Categorical:
        s2 = s.astype(str).str.upper().str.strip()
        return pd.Categorical(s2, categories=MONTH_ORDER, ordered=True)

    # -------------------------
    # Insight generators
    # -------------------------
    def top_brands_by_year(self, top_n: int = 5) -> List[Insight]:
        years = self._years_in_sales()
        out: List[Insight] = []

        for y in years:
            q = f"""
            SELECT Brand, SUM(Value) AS total_sales
            FROM sales
            WHERE Year = {y} AND Brand IS NOT NULL
            GROUP BY Brand
            ORDER BY total_sales DESC
            LIMIT {top_n}
            """
            df = self.db.fetchdf(q)
            if df.empty:
                continue

            lines = [f"{i+1}. {row.Brand}: {float(row.total_sales):,.2f}"
                     for i, row in df.iterrows()]

            out.append(Insight(
                text=(
                    f"Top {top_n} brands by total sales in {y}:\n" +
                    "\n".join(lines)
                ),
                meta={"type": "top_brands_by_year", "year": y}
            ))
        return out

    def top_categories_by_year(self, top_n: int = 5) -> List[Insight]:
        years = self._years_in_sales()
        out: List[Insight] = []

        for y in years:
            q = f"""
            SELECT Category, SUM(Value) AS total_sales
            FROM sales
            WHERE Year = {y} AND Category IS NOT NULL
            GROUP BY Category
            ORDER BY total_sales DESC
            LIMIT {top_n}
            """
            df = self.db.fetchdf(q)
            if df.empty:
                continue

            lines = [f"{i+1}. {row.Category}: {float(row.total_sales):,.2f}"
                     for i, row in df.iterrows()]

            out.append(Insight(
                text=(
                    f"Top {top_n} categories by total sales in {y}:\n" +
                    "\n".join(lines)
                ),
                meta={"type": "top_categories_by_year", "year": y}
            ))
        return out

    def best_month_per_year(self) -> List[Insight]:
        years = self._years_in_sales()
        out: List[Insight] = []

        for y in years:
            q = f"""
            SELECT Month, SUM(Value) AS total_sales
            FROM sales
            WHERE Year = {y} AND Month IS NOT NULL
            GROUP BY Month
            """
            df = self.db.fetchdf(q)
            if df.empty:
                continue

            df["Month"] = self._normalize_month(df["Month"])
            df = df.sort_values("Month")
            best = df.loc[df["total_sales"].astype(float).idxmax()]

            out.append(Insight(
                text=(
                    f"In {y}, the best sales month was {str(best['Month'])} "
                    f"with total sales {float(best['total_sales']):,.2f}."
                ),
                meta={"type": "best_month_per_year", "year": y, "month": str(best["Month"])}
            ))
        return out

    def yoy_sales_summary(self) -> List[Insight]:
        years = self._years_in_sales()
        out: List[Insight] = []
        if len(years) < 2:
            return out

        for i in range(len(years) - 1):
            y1, y2 = years[i], years[i + 1]
            q = f"""
            SELECT
              (SELECT SUM(Value) FROM sales WHERE Year = {y1}) AS s1,
              (SELECT SUM(Value) FROM sales WHERE Year = {y2}) AS s2
            """
            df = self.db.fetchdf(q)
            s1 = float(df["s1"].iloc[0] or 0)
            s2 = float(df["s2"].iloc[0] or 0)
            diff = s2 - s1
            growth = None if s1 == 0 else round((diff / s1) * 100, 2)

            out.append(Insight(
                text=(
                    f"Year-over-year total sales change from {y1} to {y2}: "
                    f"{s1:,.2f} → {s2:,.2f} (Δ {diff:,.2f}, growth {growth}%)."
                ),
                meta={"type": "yoy_total_sales", "year1": y1, "year2": y2}
            ))
        return out

    # -------------------------
    # Public build
    # -------------------------
    def build_all(self) -> List[Insight]:
        insights: List[Insight] = []
        insights += self.top_brands_by_year(top_n=5)
        insights += self.top_categories_by_year(top_n=5)
        insights += self.best_month_per_year()
        insights += self.yoy_sales_summary()
        return insights


if __name__ == "__main__":
    builder = InsightBuilder()
    all_insights = builder.build_all()
    print(f"Generated insights: {len(all_insights)}\n")
    for ins in all_insights[:10]:
        print("----")
        print(ins.text)
        print(ins.meta)
