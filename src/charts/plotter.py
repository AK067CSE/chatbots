import plotly.express as px
import pandas as pd


class ChartAgent:
    """
    Auto chart generator based on SQL result shape
    """

    def generate(self, df: pd.DataFrame, question: str):
        if df.empty:
            return None

        # If exactly 2 columns → bar chart
        if df.shape[1] == 2:
            x, y = df.columns
            fig = px.bar(
                df,
                x=x,
                y=y,
                title=question,
                text_auto=True
            )
            return fig

        # Time series (Month / Year)
        if "Month" in df.columns or "Year" in df.columns:
            time_col = "Month" if "Month" in df.columns else "Year"
            value_col = df.select_dtypes("number").columns[0]

            fig = px.line(
                df,
                x=time_col,
                y=value_col,
                title=question,
                markers=True
            )
            return fig

        # Fallback → no chart
        return None
