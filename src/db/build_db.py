from src.data.excel_loader import ExcelDataLoader
from src.db.duckdb_client import DuckDBClient


def build_database(excel_path: str, db_path: str = "data/sales.duckdb"):
    loader = ExcelDataLoader(excel_path)
    data = loader.load_all()

    sales_df = data["sales"]
    active_df = data["active_store"]
    headers_df = data["headers"]

    db = DuckDBClient(db_path)
    conn = db.connect()

    # Drop old tables (idempotent)
    conn.execute("DROP TABLE IF EXISTS sales")
    conn.execute("DROP TABLE IF EXISTS active_store")
    conn.execute("DROP TABLE IF EXISTS dictionary")

    # Create tables
    conn.register("sales_df", sales_df)
    conn.execute("CREATE TABLE sales AS SELECT * FROM sales_df")

    conn.register("active_df", active_df)
    conn.execute("CREATE TABLE active_store AS SELECT * FROM active_df")

    conn.register("headers_df", headers_df)
    conn.execute("CREATE TABLE dictionary AS SELECT * FROM headers_df")

    print("✅ DuckDB built successfully")
    print("Tables:", conn.execute("SHOW TABLES").fetchall())

    db.close()


if __name__ == "__main__":
    build_database("data/Sales & Active Stores Data.xlsb")
