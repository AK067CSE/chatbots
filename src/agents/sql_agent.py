# # from langchain_openai import ChatOpenAI
# # from langchain_core.prompts import PromptTemplate
# # from src.db.duckdb_client import DuckDBClient


# # class SQLAgent:
# #     def __init__(self):
# #         self.llm = ChatOpenAI(
# #             model="gpt-4o-mini",
# #             temperature=0
# #         )
# #         self.db = DuckDBClient()

# #     # --------------------------------------------------
# #     # FETCH DB SCHEMA (LLM SAFETY)
# #     # --------------------------------------------------
# #     def get_schema(self) -> str:
# #         schema = self.db.fetchdf("""
# #             SELECT table_name, column_name, data_type
# #             FROM information_schema.columns
# #             WHERE table_name IN ('sales', 'active_store')
# #             ORDER BY table_name, column_name
# #         """)
# #         return schema.to_string(index=False)

# #     # --------------------------------------------------
# #     # TEXT → SQL (SANITIZED)
# #     # --------------------------------------------------
# #     def generate_sql(self, question: str) -> str:
# #         prompt = PromptTemplate(
# #             input_variables=["schema", "question"],
# #             template="""
# # You are an expert data analyst.

# # STRICT RULES:
# # - Use ONLY the schema provided
# # - Output ONLY raw DuckDB SQL
# # - NO markdown
# # - NO ```sql
# # - NO explanations
# # - NO comments
# # - NO semicolon at the end

# # Schema:
# # {schema}

# # Question:
# # {question}
# # """
# #         )

# #         response = self.llm.invoke(
# #             prompt.format(
# #                 schema=self.get_schema(),
# #                 question=question
# #             )
# #         )

# #         sql = response.content.strip()

# #         # 🔥 CRITICAL SQL SANITIZATION (DO NOT REMOVE)
# #         sql = sql.replace("```sql", "")
# #         sql = sql.replace("```", "")
# #         sql = sql.strip()

# #         if sql.endswith(";"):
# #             sql = sql[:-1]

# #         return sql

# #     # --------------------------------------------------
# #     # EXECUTE SQL
# #     # --------------------------------------------------
# #     def execute(self, sql: str):
# #         return self.db.fetchdf(sql)

# #     # --------------------------------------------------
# #     # FULL PIPELINE
# #     # --------------------------------------------------
# #     def answer(self, question: str):
# #         sql = self.generate_sql(question)
# #         df = self.execute(sql)
# #         return sql, df
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import PromptTemplate
# from src.db.duckdb_client import DuckDBClient


# class SQLAgent:
#     def __init__(self):
#         self.llm = ChatOpenAI(
#             model="gpt-4o-mini",
#             temperature=0
#         )
#         self.db = DuckDBClient()

#     # --------------------------------------------------
#     # FETCH DB SCHEMA (LLM SAFETY)
#     # --------------------------------------------------
#     def get_schema(self) -> str:
#         schema = self.db.fetchdf("""
#             SELECT table_name, column_name, data_type
#             FROM information_schema.columns
#             WHERE table_name IN ('sales', 'active_store')
#             ORDER BY table_name, column_name
#         """)
#         return schema.to_string(index=False)

#     # --------------------------------------------------
#     # TEXT → SQL (WITH DOMAIN RULES)
#     # --------------------------------------------------
#     def generate_sql(self, question: str) -> str:
#         prompt = PromptTemplate(
#             input_variables=["schema", "question"],
#             template="""
# You are an expert data analyst generating DuckDB SQL.

# DOMAIN RULES (VERY IMPORTANT):
# - The Month column stores values as:
#   JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC
# - If the user says:
#   January → 'JAN'
#   February → 'FEB'
#   March → 'MAR'
#   April → 'APR'
#   May → 'MAY'
#   June → 'JUN'
#   July → 'JUL'
#   August → 'AUG'
#   September → 'SEP'
#   October → 'OCT'
#   November → 'NOV'
#   December → 'DEC'
# - Always match Month exactly as stored in the database

# STRICT RULES:
# - Use ONLY the schema provided
# - Use ONLY valid DuckDB SQL
# - Output ONLY raw SQL
# - NO markdown
# - NO ```sql
# - NO explanations
# - NO comments
# - NO semicolon at the end

# Schema:
# {schema}

# Question:
# {question}
# """
#         )

#         response = self.llm.invoke(
#             prompt.format(
#                 schema=self.get_schema(),
#                 question=question
#             )
#         )

#         sql = response.content.strip()

#         # --------------------------------------------------
#         # SQL SANITIZATION (CRITICAL)
#         # --------------------------------------------------
#         sql = sql.replace("```sql", "")
#         sql = sql.replace("```", "")
#         sql = sql.strip()

#         if sql.endswith(";"):
#             sql = sql[:-1]

#         return sql

#     # --------------------------------------------------
#     # EXECUTE SQL
#     # --------------------------------------------------
#     def execute(self, sql: str):
#         return self.db.fetchdf(sql)

#     # --------------------------------------------------
#     # FULL PIPELINE
#     # --------------------------------------------------
#     def answer(self, question: str):
#         sql = self.generate_sql(question)
#         df = self.execute(sql)
#         return sql, df
# src/agents/sql_agent.py

from src.db.duckdb_client import DuckDBClient
from src.agents.metric_router import build_sql_from_question


class SQLAgent:
    """
    SQLAgent
    --------
    Responsible ONLY for:
    - Understanding user intent (via metric_router)
    - Building SAFE SQL from templates
    - Executing SQL on DuckDB

    ❌ No LLM-generated SQL
    ✅ Deterministic, debuggable, production-safe
    """

    def __init__(self):
        self.db = DuckDBClient()

    # --------------------------------------------------
    # EXECUTE SQL
    # --------------------------------------------------
    def execute(self, sql: str):
        return self.db.fetchdf(sql)

    # --------------------------------------------------
    # FULL PIPELINE
    # --------------------------------------------------
    def answer(self, question: str):
        """
        Returns:
        - sql: generated SQL string
        - df: pandas DataFrame result
        - meta: intent + extracted entities (for debugging/UI)
        """
        sql, meta = build_sql_from_question(question)

        if not sql:
            return "", None, meta

        df = self.execute(sql)
        return sql, df, meta
