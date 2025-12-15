import os
import sys

# Ensure project root is on sys.path so `src` can be imported when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.sql_agent import SQLAgent

agent = SQLAgent()

def run_tests():
    queries = [
        "Total sales for Delmond in Jan 2024",
        "Compare Delmond sales 2024 vs 2025",
        "Total active stores for Delmond in Feb 2024",
        "Summarize sales by region",
    ]

    for q in queries:
        print("\nQUESTION:", q)
        sql, df, meta = agent.answer(q)

        print("SQL:", sql)

        if df is None or df.empty:
            print("❌ NO DATA RETURNED")
        else:
            print("✅ RESULT:")
            print(df.head())

if __name__ == "__main__":
    run_tests()
