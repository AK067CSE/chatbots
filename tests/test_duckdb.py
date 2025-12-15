from src.db.duckdb_client import DuckDBClient

db = DuckDBClient()
print(db.fetchdf("SELECT COUNT(*) AS rows FROM sales"))
print(db.fetchdf("SELECT Year, SUM(Value) FROM sales GROUP BY Year"))
print(db.fetchdf("SELECT COUNT(*) FROM active_store"))
