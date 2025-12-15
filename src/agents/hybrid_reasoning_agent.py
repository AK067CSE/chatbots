from langchain_openai import ChatOpenAI
from src.rag.rag_agent import RagAgent


class HybridReasoningAgent:
    """
    Combines SQL results + RAG business memory
    to produce analyst-style reasoning.
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        self.rag = RagAgent()

    def reason(self, question: str, sql_result_df):
        # 1️⃣ Get RAG context
        docs = self.rag.search(question, k=5)
        rag_context = "\n".join(d.page_content for d in docs)

        # 2️⃣ Prepare SQL summary (truncate for safety)
        if sql_result_df is not None and not sql_result_df.empty:
            sql_summary = sql_result_df.head(20).to_string(index=False)
        else:
            sql_summary = "No numerical result available."

        # 3️⃣ Reasoning prompt
        prompt = f"""
You are a senior business analyst.

You are given:
1) Numerical results from a database query
2) Historical business insights (context)

Your task:
- Explain WHAT happened
- Explain WHY it happened
- Give ACTIONABLE recommendations

Business Context (RAG Memory):
{rag_context}

Numerical Result (SQL):
{sql_summary}

User Question:
{question}

Answer clearly in bullet points.
Focus on business reasoning and strategy.
"""

        return self.llm.invoke(prompt).content
