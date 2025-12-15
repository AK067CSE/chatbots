# # # # from src.agents.sql_agent import SQLAgent
# # # from src.rag.rag_agent import RagAgent
# # # from src.agents.explain_agent import ExplainAgent


# # # class SQLRAGRouter:
# # #     def __init__(self):
# # #         self.sql_agent = SQLAgent()
# # #         self.rag_agent = RagAgent()
# # #         self.explainer = ExplainAgent()

# # #     def route(self, question: str):
# # #         q = question.lower()

# # #         # ----------------------------
# # #         # RAG-only (definitions, meaning)
# # #         # ----------------------------
# # #         if any(x in q for x in ["what is", "define", "meaning", "explain column"]):
# # #             docs = self.rag_agent.search(question)
# # #             answer = self.explainer.explain_rag(question, docs)
# # #             return {
# # #                 "engine": "RAG",
# # #                 "answer": answer
# # #             }

# # #         # ----------------------------
# # #         # SQL (metrics, comparisons)
# # #         # ----------------------------
# # #         sql, df = self.sql_agent.answer(question)
# # #         explanation = self.explainer.explain_sql(question, sql, df)

# # #         return {
# # #             "engine": "SQL",
# # #             "sql": sql,
# # #             "data": df,
# # #             "explanation": explanation
# # #         }
# # from src.agents.sql_agent import SQLAgent   # ✅ UNCOMMENT / ADD THIS
# # from src.rag.rag_agent import RagAgent
# # from src.agents.explain_agent import ExplainAgent


# # class SQLRAGRouter:
# #     def __init__(self):
# #         self.sql_agent = SQLAgent()
# #         self.rag_agent = RagAgent()
# #         self.explainer = ExplainAgent()

# #     def route(self, question: str):
# #         q = question.lower()

# #         # ----------------------------
# #         # RAG-only (definitions, meaning)
# #         # ----------------------------
# #         if any(x in q for x in ["what is", "define", "meaning", "explain column"]):
# #             docs = self.rag_agent.search(question)
# #             answer = self.explainer.explain_rag(question, docs)
# #             return {
# #                 "engine": "RAG",
# #                 "answer": answer
# #             }

# #         # ----------------------------
# #         # SQL (metrics, comparisons)
# #         # ----------------------------
# #         sql, df = self.sql_agent.answer(question)
# #         explanation = self.explainer.explain_sql(question, sql, df)

# #         return {
# #             "engine": "SQL",
# #             "sql": sql,
# #             "data": df,
# #             "explanation": explanation
# #         }
# from src.charts.chart_agent import ChartAgent

# from src.agents.sql_agent import SQLAgent
# from src.rag.rag_agent import RagAgent
# from src.agents.explain_agent import ExplainAgent
# from src.agents.hybrid_reasoning_agent import HybridReasoningAgent


# class SQLRAGRouter:
#     def __init__(self):
#         self.sql_agent = SQLAgent()
#         self.rag_agent = RagAgent()
#         self.explainer = ExplainAgent()
#         self.hybrid = HybridReasoningAgent()

#     def route(self, question: str):
#         q = question.lower()

#         # ----------------------------
#         # RAG-only (definitions, meanings)
#         # ----------------------------
#         if any(x in q for x in ["what is", "define", "meaning", "explain column"]):
#             docs = self.rag_agent.search(question)
#             answer = self.explainer.explain_rag(question, docs)
#             return {
#                 "engine": "RAG",
#                 "answer": answer
#             }

#         # ----------------------------
#         # SQL + RAG reasoning (strategy / why / how)
#         # ----------------------------
#         if any(x in q for x in ["why", "how", "improve", "strategy", "recommend"]):
#             sql, df = self.sql_agent.answer(question)
#             reasoning = self.hybrid.reason(question, df)
#             return {
#                 "engine": "HYBRID",
#                 "sql": sql,
#                 "data": df,
#                 "analysis": reasoning
#             }

#         # ----------------------------
#         # SQL-only (metrics, comparisons)
#         # ----------------------------
#         sql, df = self.sql_agent.answer(question)
#         explanation = self.explainer.explain_sql(question, sql, df)

#         return {
#             "engine": "SQL",
#             "sql": sql,
#             "data": df,
#             "explanation": explanation
#         }
from src.agents.sql_agent import SQLAgent
from src.rag.rag_agent import RagAgent
from src.agents.explain_agent import ExplainAgent
from src.agents.hybrid_reasoning_agent import HybridReasoningAgent
from src.charts.chart_agent import ChartAgent


class SQLRAGRouter:
    """
    Central brain:
    - SQL → facts & metrics
    - RAG → definitions & metadata
    - HYBRID → reasoning & strategy
    - Charts → auto visualization
    """

    def __init__(self):
        self.sql_agent = SQLAgent()
        self.rag_agent = RagAgent()
        self.explainer = ExplainAgent()
        self.hybrid = HybridReasoningAgent()
        self.charts = ChartAgent()

    def route(self, question: str):
        q = question.lower()

        # --------------------------------------------------
        # 1️⃣ RAG ONLY (definitions / column meaning)
        # --------------------------------------------------
        if any(x in q for x in ["what is", "define", "meaning", "explain column"]):
            docs = self.rag_agent.search(question)
            answer = self.explainer.explain_rag(question, docs)

            return {
                "engine": "RAG",
                "answer": answer
            }

        # --------------------------------------------------
        # 2️⃣ HYBRID (WHY / HOW / STRATEGY)
        # --------------------------------------------------
        if any(x in q for x in ["why", "how", "improve", "strategy", "recommend"]):
            sql, df, meta = self.sql_agent.answer(question)
            analysis = self.hybrid.reason(question, df)
            chart = self.charts.generate(df, question)

            return {
                "engine": "HYBRID",
                "sql": sql,
                "data": df,
                "analysis": analysis,
                "chart": chart
            }

        # --------------------------------------------------
        # 3️⃣ SQL ONLY (FACTS / METRICS)
        # --------------------------------------------------
        sql, df, meta = self.sql_agent.answer(question)
        explanation = self.explainer.explain_sql(question, sql, df)
        chart = self.charts.generate(df, question)

        return {
            "engine": "SQL",
            "sql": sql,
            "data": df,
            "explanation": explanation,
            "chart": chart
        }
