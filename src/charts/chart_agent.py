# src/charts/chart_agent.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class ChartAgent:
    """
    Automatically generates interactive Plotly charts from query results + question.
    """

    def generate(self, df: pd.DataFrame, question: str):
        if df is None or df.empty:
            return None

        q = question.lower()

        # ---------------------------
        # TOP N (Bar Chart)
        # ---------------------------
        if "top" in q:
            # Look for numeric and categorical columns
            num_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
            cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
            
            if num_cols and cat_cols:
                # Use first numeric and categorical column
                cat_col = cat_cols[0]
                num_col = num_cols[0]
                
                # Sort and limit to top values
                plot_data = df.nlargest(5, num_col) if len(df) > 5 else df
                
                fig = px.bar(
                    plot_data,
                    x=cat_col,
                    y=num_col,
                    title=f"Top Results by {num_col}",
                    labels={cat_col: "Category", num_col: "Value"},
                    color=num_col,
                    color_continuous_scale="Viridis"
                )
                return fig

        # ---------------------------
        # YEAR COMPARISON (Bar Chart)
        # ---------------------------
        if any(x in q for x in ["compare", "vs", "versus", "yoy"]):
            if "Year" in df.columns:
                num_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
                if num_cols:
                    num_col = num_cols[0]
                    fig = px.bar(
                        df,
                        x="Year",
                        y=num_col,
                        title=f"Year-over-Year Comparison ({num_col})",
                        labels={"Year": "Year", num_col: "Value"},
                        color="Year",
                        text=num_col
                    )
                    fig.update_traces(textposition='auto')
                    return fig

        # ---------------------------
        # GROUP BY (Bar Chart - Horizontal)
        # ---------------------------
        if any(x in q for x in ["by region", "by brand", "by category", "summarize", "breakdown"]):
            # Find categorical and numeric columns
            cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
            num_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
            
            if cat_cols and num_cols:
                cat_col = cat_cols[0] if cat_cols[0] != "group_key" else (cat_cols[1] if len(cat_cols) > 1 else cat_cols[0])
                num_col = num_cols[0]
                
                # Sort and limit
                plot_data = df.sort_values(num_col, ascending=True).tail(10)
                
                fig = px.bar(
                    plot_data,
                    x=num_col,
                    y=cat_col if cat_col != "group_key" else "group_key",
                    title=f"Summary by {cat_col}",
                    labels={cat_col: "Category", num_col: "Value"},
                    color=num_col,
                    color_continuous_scale="Blues",
                    orientation="h"
                )
                return fig

        # ---------------------------
        # MONTH TREND (Line Chart)
        # ---------------------------
        if any(x in q for x in ["trend", "over time", "monthly", "month"]):
            if "Month" in df.columns:
                num_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
                if num_cols:
                    num_col = num_cols[0]
                    fig = px.line(
                        df,
                        x="Month",
                        y=num_col,
                        title=f"{num_col} Trend by Month",
                        labels={"Month": "Month", num_col: "Value"},
                        markers=True
                    )
                    return fig

        # ---------------------------
        # DEFAULT: Generic Bar Chart
        # ---------------------------
        try:
            num_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
            cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
            
            if num_cols and cat_cols:
                cat_col = cat_cols[0]
                num_col = num_cols[0]
                
                fig = px.bar(
                    df.head(10),
                    x=cat_col,
                    y=num_col,
                    title=f"{num_col} by {cat_col}",
                    color=num_col,
                    color_continuous_scale="Plasma"
                )
                return fig
        except Exception:
            pass

        return None
