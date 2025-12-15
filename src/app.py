# # # from dotenv import load_dotenv
# # # from src.agents.sql_agent import SQLAgent
# # # from src.agents.explain_agent import ExplainAgent
# # # from src.charts.plotter import ChartAgent

# # # # Load environment variables (.env → OPENAI_API_KEY)
# # # load_dotenv()

# # # # Initialize agents
# # # sql_agent = SQLAgent()
# # # explain_agent = ExplainAgent()
# # # chart_agent = ChartAgent()


# # # def run_query(question: str):
# # #     # 1️⃣ Text → SQL → Data
# # #     sql, df = sql_agent.answer(question)

# # #     # 2️⃣ Business explanation
# # #     explanation = explain_agent.explain(question, sql, df)

# # #     # 3️⃣ Auto chart (if possible)
# # #     chart = chart_agent.generate(df, question)

# # #     return {
# # #         "sql": sql,
# # #         "data": df,
# # #         "explanation": explanation,
# # #         "chart": chart
# # #     }


# # # if __name__ == "__main__":
# # #     print("\n📊 AI Sales & Active Store Assistant (DuckDB + LLM)")
# # #     print("Type 'exit' to quit\n")

# # #     while True:
# # #         q = input("Ask a business question: ")
# # #         if q.lower() == "exit":
# # #             break

# # #         output = run_query(q)

# # #         print("\n--- SQL GENERATED ---")
# # #         print(output["sql"])

# # #         print("\n--- DATA RESULT ---")
# # #         print(output["data"])

# # #         print("\n--- BUSINESS EXPLANATION ---")
# # #         print(output["explanation"])

# # #         # Show chart if generated
# # #         if output["chart"] is not None:
# # #             output["chart"].show()
# # # # 
# # # from dotenv import load_dotenv
# # # from src.agents.sql_rag_router import SQLRAGRouter

# # # load_dotenv()

# # # router = SQLRAGRouter()

# # # if __name__ == "__main__":
# # #     while True:
# # #         q = input("\nAsk a business question (or 'exit'): ")
# # #         if q.lower() == "exit":
# # #             break

# # #         output = router.route(q)

# # #         print("\nEngine Used:", output["engine"])

# # #         if output["engine"] == "SQL":
# # #             print("\nSQL:\n", output["sql"])
# # #             print("\nResult:\n", output["data"])
# # #             print("\nExplanation:\n", output["explanation"])
# # #         else:
# # #             print("\nAnswer:\n", output["answer"])
# # from dotenv import load_dotenv
# # from src.agents.sql_rag_router import SQLRAGRouter

# # load_dotenv()

# # router = SQLRAGRouter()

# # if __name__ == "__main__":
# #     while True:
# #         q = input("\nAsk a business question (or 'exit'): ")
# #         if q.lower() == "exit":
# #             break

# #         output = router.route(q)

# #         print("\nEngine Used:", output["engine"])

# #         if output["engine"] == "SQL":
# #             print("\nSQL:\n", output["sql"])
# #             print("\nResult:\n", output["data"])
# #             print("\nExplanation:\n", output["explanation"])
# #         else:
# #             print("\nAnswer:\n", output["answer"])
# from dotenv import load_dotenv
# from src.agents.sql_rag_router import SQLRAGRouter

# load_dotenv()

# router = SQLRAGRouter()

# if __name__ == "__main__":
#     while True:
#         q = input("\nAsk a business question (or 'exit'): ")
#         if q.lower() == "exit":
#             break

#         output = router.route(q)

#         print("\nEngine Used:", output["engine"])

#         if output["engine"] == "SQL":
#             print("\n--- SQL GENERATED ---")
#             print(output["sql"])

#             print("\n--- DATA ---")
#             print(output["data"])

#             print("\n--- BUSINESS EXPLANATION ---")
#             print(output["explanation"])

#         elif output["engine"] == "HYBRID":
#             print("\n--- SQL GENERATED ---")
#             print(output["sql"])

#             print("\n--- DATA ---")
#             print(output["data"].head(10))

#             print("\n--- BUSINESS ANALYSIS ---")
#             print(output["analysis"])

#         elif output["engine"] == "RAG":
#             print("\n--- KNOWLEDGE ANSWER ---")
#             print(output["answer"])
from dotenv import load_dotenv
from src.agents.sql_rag_router import SQLRAGRouter

load_dotenv()

router = SQLRAGRouter()

if __name__ == "__main__":
    print("\n📊 AI Sales & Active Store Business Assistant")
    print("Type 'exit' to quit")

    while True:
        q = input("\nAsk a business question: ")
        if q.lower() == "exit":
            break

        output = router.route(q)

        print("\nEngine Used:", output["engine"])

        if output["engine"] == "SQL":
            print("\n--- SQL ---")
            print(output["sql"])

            print("\n--- DATA ---")
            print(output["data"].head(10))

            print("\n--- EXPLANATION ---")
            print(output["explanation"])

        elif output["engine"] == "HYBRID":
            print("\n--- SQL ---")
            print(output["sql"])

            print("\n--- DATA ---")
            print(output["data"].head(10))

            print("\n--- BUSINESS ANALYSIS ---")
            print(output["analysis"])

        elif output["engine"] == "RAG":
            print("\n--- KNOWLEDGE ---")
            print(output["answer"])

        # Auto chart
        if output.get("chart"):
            output["chart"].show()
