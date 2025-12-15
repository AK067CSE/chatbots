import duckdb
from typing import Optional
import pandas as pd


class DuckDBClient:
    def __init__(self, db_path: str = "data/sales.duckdb"):
        self.db_path = db_path
        self.conn: Optional[duckdb.DuckDBPyConnection] = None

    def connect(self):
        if self.conn is None:
            self.conn = duckdb.connect(self.db_path)
        return self.conn

    def execute(self, query: str):
        conn = self.connect()
        return conn.execute(query)

    def fetchdf(self, query: str):
        conn = self.connect()
        return conn.execute(query).fetchdf()

    def load_dataframe(self, table_name: str, df: pd.DataFrame):
        """Load a pandas DataFrame into DuckDB as a table."""
        conn = self.connect()
        conn.register(table_name, df)
        return conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {table_name}")

    def query(self, sql: str):
        """Execute SQL and return a pandas DataFrame."""
        return self.fetchdf(sql)

    def get_tables(self) -> list:
        """Return a list of table names in the database."""
        df = self.fetchdf("SHOW TABLES")
        # DuckDB may return different column names depending on version
        if 'name' in df.columns:
            return df['name'].tolist()
        if 'table_name' in df.columns:
            return df['table_name'].tolist()
        # Fallback: return stringified rows
        return [str(v) for v in df.iloc[:, 0].tolist()]

    def get_columns(self, table_name: str) -> list:
        """Return list of (column_name, data_type) for a table."""
        try:
            df = self.fetchdf(f"PRAGMA table_info('{table_name}')")
        except Exception:
            # Fallback to information_schema
            df = self.fetchdf(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'")

        cols = []
        if 'name' in df.columns and 'type' in df.columns:
            for _, r in df.iterrows():
                cols.append((r['name'], r['type']))
        elif 'column_name' in df.columns and 'data_type' in df.columns:
            for _, r in df.iterrows():
                cols.append((r['column_name'], r['data_type']))
        else:
            for c in df.columns:
                cols.append((c, 'unknown'))

        return cols

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None