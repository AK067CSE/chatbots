try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain.chat_models import ChatOpenAI

try:
    from langchain.memory import ConversationBufferMemory
except ImportError:
    from langchain_community.chat_message_histories import ChatMessageHistory
    ConversationBufferMemory = None

try:
    from langchain.chains import ConversationChain
except ImportError:
    ConversationChain = None

from langchain.prompts import PromptTemplate
from typing import List, Dict, Any
from src.rag_system_simple import SimpleRAGSystem, SimpleRAGFusionRetriever
from src.config import settings
import json


class PDFAnalysisChatbot:
    def __init__(self, rag_system: RAGSystem):
        self.rag = rag_system
        self.retriever = RAGFusionRetriever(rag_system)
        
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
        
        self.memory = ConversationBufferMemory(
            max_token_limit=2048,
            return_messages=True
        )
        
        self._setup_chat_chain()
        
        self.conversation_history = []
    
    def _setup_chat_chain(self):
        system_prompt = """You are an expert procurement and accounting assistant specializing in Purchase Order (PO) 
        and Invoice reconciliation. You have access to detailed document information and can:
        
        1. Answer questions about documents, items, quantities, and prices
        2. Identify and explain discrepancies between POs and Invoices
        3. Provide recommendations for resolving issues
        4. Search and retrieve specific information from documents
        5. Generate summaries and reports
        
        Always be precise with numbers and financial data. When uncertain, ask clarifying questions.
        Format currency values clearly and highlight any significant discrepancies.
        
        Context: {context}
        
        Conversation History:
        {history}
        
        User Question: {input}
        
        Response:"""
        
        prompt_template = PromptTemplate(
            input_variables=["context", "history", "input"],
            template=system_prompt
        )
        
        self.chat_chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=prompt_template,
            verbose=True
        )
    
    def chat(self, user_query: str) -> Dict[str, Any]:
        retrieved_context = self.retriever.retrieve_with_fusion(user_query, n_results=3)
        
        context_text = self._format_context(retrieved_context)
        
        history_text = self._format_history()
        
        input_dict = {
            "input": user_query,
            "context": context_text,
            "history": history_text
        }
        
        response = self.llm.invoke(
            [{"role": "system", "content": f"Context: {context_text}"},
             {"role": "user", "content": user_query}]
        )
        
        assistant_response = response.content
        
        self.conversation_history.append({
            'user': user_query,
            'assistant': assistant_response,
            'retrieved_context': retrieved_context
        })
        
        self.memory.save_context(
            {"input": user_query},
            {"output": assistant_response}
        )
        
        return {
            'query': user_query,
            'response': assistant_response,
            'context_used': len(retrieved_context),
            'context_samples': [r['document'][:200] for r in retrieved_context]
        }
    
    def _format_context(self, retrieved_results: List[Dict]) -> str:
        if not retrieved_results:
            return "No relevant context found."
        
        context_lines = ["RETRIEVED CONTEXT:"]
        
        for i, result in enumerate(retrieved_results, 1):
            context_lines.append(f"\n[Document {i}]")
            context_lines.append(f"Type: {result['metadata'].get('chunk_type', 'Unknown')}")
            context_lines.append(f"Document ID: {result['metadata'].get('document_id', 'Unknown')}")
            context_lines.append(f"Content: {result['document'][:300]}...")
        
        return "\n".join(context_lines)
    
    def _format_history(self) -> str:
        if not self.conversation_history:
            return "No conversation history yet."
        
        history_lines = []
        for turn in self.conversation_history[-3:]:
            history_lines.append(f"User: {turn['user']}")
            history_lines.append(f"Assistant: {turn['assistant'][:200]}...")
        
        return "\n".join(history_lines)
    
    def ask_about_discrepancies(self, item_description: str = None) -> str:
        if item_description:
            query = f"What are the discrepancies for {item_description}?"
        else:
            query = "What are the main discrepancies between the PO and Invoice?"
        
        return self.chat(query)
    
    def ask_about_totals(self) -> str:
        query = "What is the difference in total values between the PO and Invoice?"
        return self.chat(query)
    
    def ask_for_recommendations(self) -> str:
        query = "Based on the discrepancies, what actions would you recommend?"
        return self.chat(query)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        if not self.conversation_history:
            return {'message': 'No conversation history'}
        
        return {
            'total_turns': len(self.conversation_history),
            'queries': [turn['user'] for turn in self.conversation_history],
            'last_response': self.conversation_history[-1]['assistant'],
            'context_used_total': sum(len(turn['retrieved_context']) for turn in self.conversation_history)
        }
    
    def reset_memory(self):
        self.memory.clear()
        self.conversation_history = []
        return "Conversation memory cleared."


class InteractiveChatbot:
    def __init__(self, rag_system: RAGSystem):
        self.chatbot = PDFAnalysisChatbot(rag_system)
        self.running = False
    
    def start_interactive_session(self):
        self.running = True
        print("\n" + "="*60)
        print("PDF ANALYSIS CHATBOT - Interactive Session")
        print("="*60)
        print("Type 'help' for available commands")
        print("Type 'exit' to quit\n")
        
        while self.running:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'exit':
                    self.running = False
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self._print_help()
                    continue
                
                if user_input.lower() == 'summary':
                    summary = self.chatbot.get_conversation_summary()
                    print(f"\nConversation Summary: {json.dumps(summary, indent=2)}\n")
                    continue
                
                if user_input.lower() == 'clear':
                    self.chatbot.reset_memory()
                    print("Memory cleared.\n")
                    continue
                
                response = self.chatbot.chat(user_input)
                print(f"\nAssistant: {response['response']}\n")
                
            except KeyboardInterrupt:
                self.running = False
                print("\n\nSession terminated.")
                break
            except Exception as e:
                print(f"Error: {str(e)}\n")
    
    def _print_help(self):
        help_text = """
AVAILABLE COMMANDS:
- Any natural language question about documents
- 'help' - Show this help message
- 'summary' - Show conversation summary
- 'clear' - Clear conversation memory
- 'exit' - Exit the chatbot

EXAMPLE QUESTIONS:
- "What items are in the purchase order?"
- "What are the discrepancies between PO and Invoice?"
- "What is the total difference in value?"
- "Which items have quantity mismatches?"
- "What are your recommendations for these discrepancies?"
"""
        print(help_text)


def initialize_chatbot(rag_system: RAGSystem) -> PDFAnalysisChatbot:
    return PDFAnalysisChatbot(rag_system)


def start_interactive_chat(rag_system: RAGSystem):
    bot = InteractiveChatbot(rag_system)
    bot.start_interactive_session()
