# # from langchain_openai import ChatOpenAI


# # class ExplainAgent:
# #     def __init__(self):
# #         self.llm = ChatOpenAI(
# #             model="gpt-4o-mini",
# #             temperature=0
# #         )

# #     def explain(self, question: str, sql: str, df):
# #         prompt = f"""
# # You are a business analyst.

# # Question:
# # {question}

# # SQL Used:
# # {sql}

# # Result:
# # {df.to_string(index=False)}

# # Explain the result clearly for a business user.
# # """
# #         return self.llm.invoke(prompt).content
# from langchain_openai import ChatOpenAI
# from src.rag.rag_agent import RAGAgent

# class ExplainAgent:
#     def __init__(self):
#         self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
#         self.rag = RAGAgent()

#     def explain(self, question, sql, df):
#         context = self.rag.get_context(question)

#         prompt = f"""
# Business context:
# {context}

# User question:
# {question}

# SQL used:
# {sql}

# Result:
# {df.head(10)}

# Explain clearly for a business user.
# """

#         # return self.llm.invoke(prompt).content
# from langchain_openai import ChatOpenAI


# class ExplainAgent:
#     def __init__(self):
#         self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

#     def explain_sql(self, question: str, sql: str, df):
#         return self.llm.invoke(
#             f"""
# You are a business analyst.

# Question:
# {question}

# SQL Used:
# {sql}

# Result:
# {df.to_string(index=False)}

# Explain this clearly in business terms.
# """
#         ).content

#     def explain_rag(self, question: str, docs):
#         context = "\n\n".join(d.page_content for d in docs)
#         return self.llm.invoke(
#             f"""
# Answer the question using the context below.

# Context:
# {context}

# Question:
# {question}
# """
#         ).content

from langchain_openai import ChatOpenAI


class ExplainAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def explain_sql(self, question: str, sql: str, df):
        return self.llm.invoke(
            f"""
You are a business analyst.

Question:
{question}

SQL Used:
{sql}

Result:
{df.to_string(index=False)}

Explain this clearly in business terms.
"""
        ).content

    def explain_rag(self, question: str, docs):
        context = "\n\n".join(d.page_content for d in docs)
        return self.llm.invoke(
            f"""
Answer the question using the context below.

Context:
{context}

Question:
{question}
"""
        ).content
