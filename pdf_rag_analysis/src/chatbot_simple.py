from typing import List, Dict, Any
from src.rag_system_simple import SimpleRAGSystem, SimpleRAGFusionRetriever
import json


class SimplePDFChatbot:
    def __init__(self, rag_system: SimpleRAGSystem):
        self.rag = rag_system
        self.retriever = SimpleRAGFusionRetriever(rag_system)
        self.conversation_history = []
    
    def chat(self, user_query: str) -> Dict[str, Any]:
        retrieved_context = self.retriever.retrieve_with_fusion(user_query, n_results=3)
        context_text = self._format_context(retrieved_context)
        
        response = self._generate_response(user_query, context_text)
        
        self.conversation_history.append({
            'user': user_query,
            'assistant': response,
            'retrieved_context': retrieved_context
        })
        
        return {
            'query': user_query,
            'response': response,
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
    
    def _generate_response(self, user_query: str, context: str) -> str:
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['discrepanc', 'mismatch', 'difference', 'variance']):
            return self._respond_to_discrepancy_query(user_query, context)
        elif any(word in query_lower for word in ['total', 'value', 'price', 'amount', 'cost']):
            return self._respond_to_financial_query(user_query, context)
        elif any(word in query_lower for word in ['item', 'product', 'line', 'what']):
            return self._respond_to_item_query(user_query, context)
        elif any(word in query_lower for word in ['recommend', 'suggest', 'action', 'do', 'should']):
            return self._respond_to_recommendation_query(user_query, context)
        else:
            return self._respond_to_general_query(user_query, context)
    
    def _respond_to_discrepancy_query(self, query: str, context: str) -> str:
        return f"""Based on the documents, here's what I found regarding discrepancies:

{context[:500]}...

Key findings from the comparison:
- The system has identified several items with mismatches between the Purchase Order and Proforma Invoice
- These include quantity differences, price variations, and missing items
- I recommend reviewing each discrepancy carefully before proceeding with payment

For a detailed breakdown, please check the generated comparison report in JSON, CSV, or Excel format."""
    
    def _respond_to_financial_query(self, query: str, context: str) -> str:
        return f"""Regarding the financial aspects:

{context[:500]}...

Financial Summary:
- The comparison shows significant differences between PO and Invoice values
- Various items have price and quantity discrepancies contributing to the total difference
- It's important to resolve these before finalizing the transaction

Please review the detailed financial report for line-by-line breakdown."""
    
    def _respond_to_item_query(self, query: str, context: str) -> str:
        return f"""Here are the items from your documents:

{context[:600]}...

The documents contain multiple items with varying quantities and prices. Some key observations:
- Each item has been extracted and organized
- Quantities and unit prices are available for comparison
- Check the comparison report for detailed item-level analysis"""
    
    def _respond_to_recommendation_query(self, query: str, context: str) -> str:
        return f"""Based on the document analysis, here are my recommendations:

{context[:400]}...

Action Items:
1. Review the comparison report for all discrepancies
2. Prioritize items with CRITICAL or HIGH severity ratings
3. Contact the vendor to clarify quantity and price differences
4. Verify that all items match the original purchase requirements
5. Reconcile the total invoice amount with the PO total
6. Request corrected documentation if needed

Critical items requiring immediate attention:
- Items missing from the invoice
- Items with more than 10% price variance
- Quantity mismatches that affect total cost significantly"""
    
    def _respond_to_general_query(self, query: str, context: str) -> str:
        return f"""Thank you for your question. Here's relevant information from the documents:

{context[:500]}...

This analysis system can help you:
- Compare Purchase Orders with Proforma Invoices
- Identify and highlight discrepancies
- Generate detailed reports in multiple formats
- Understand the financial impact of any mismatches

Feel free to ask specific questions about items, totals, discrepancies, or recommendations."""
    
    def ask_about_discrepancies(self) -> str:
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
            'last_response': self.conversation_history[-1]['assistant'][:200],
            'context_used_total': sum(len(turn['retrieved_context']) for turn in self.conversation_history)
        }
    
    def reset_memory(self):
        self.conversation_history = []
        return "Conversation memory cleared."


class InteractiveSimpleChatbot:
    def __init__(self, rag_system: SimpleRAGSystem):
        self.chatbot = SimplePDFChatbot(rag_system)
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
                    print(f"\nConversation Summary:\n{json.dumps(summary, indent=2)}\n")
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


def initialize_simple_chatbot(rag_system: SimpleRAGSystem) -> SimplePDFChatbot:
    return SimplePDFChatbot(rag_system)


def start_simple_interactive_chat(rag_system: SimpleRAGSystem):
    bot = InteractiveSimpleChatbot(rag_system)
    bot.start_interactive_session()
