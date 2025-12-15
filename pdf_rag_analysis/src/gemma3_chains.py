import json
from typing import List, Dict, Optional
from src.gemma3_inference import Gemma3Inference

class Gemma3DocumentAnalysisChain:
    def __init__(self, model_path: str = r"C:\Users\abhik\Downloads\sales\salesbot\gemma3-text2sql-merged"):
        self.inference = Gemma3Inference(model_path)
    
    def analyze_discrepancies(self, po_items: List[Dict], invoice_items: List[Dict]) -> str:
        return self.inference.analyze_discrepancies(po_items, invoice_items)
    
    def extract_financial_summary(self, document_data: Dict) -> Dict:
        prompt = f"""Extract and summarize the financial information from this document:

{json.dumps(document_data, indent=2)}

Provide a JSON response with:
- total_amount
- currency
- line_items_count
- key_financial_metrics
- summary

Response as JSON:"""
        
        response = self.inference.generate(prompt)
        try:
            return json.loads(response)
        except:
            return {"raw_response": response}

class Gemma3MultiTurnChatChain:
    def __init__(self, model_path: str = r"C:\Users\abhik\Downloads\sales\salesbot\gemma3-text2sql-merged"):
        self.inference = Gemma3Inference(model_path)
        self.conversation_history = []
    
    def add_message(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
    
    def get_response(self, user_message: str, context: str = "") -> str:
        self.add_message("user", user_message)
        
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in self.conversation_history[-4:]])
        
        prompt = f"""Document Context:
{context}

Conversation History:
{history_text}

Provide a helpful response to the user's question based on the document context and conversation history.
Response:"""
        
        response = self.inference.generate(prompt, max_length=512)
        self.add_message("assistant", response)
        return response
    
    def clear_history(self):
        self.conversation_history = []

class Gemma3ComparisonAnalysisChain:
    def __init__(self, model_path: str = r"C:\Users\abhik\Downloads\sales\salesbot\gemma3-text2sql-merged"):
        self.inference = Gemma3Inference(model_path)
    
    def generate_analysis(self, comparison_data: Dict) -> str:
        prompt = f"""As a procurement analyst, generate a professional comparison analysis report:

{json.dumps(comparison_data, indent=2)}

Provide:
1. Executive Summary
2. Key Differences
3. Risk Assessment
4. Recommendations

Analysis Report:"""
        
        return self.inference.generate(prompt, max_length=1024)
    
    def identify_issues(self, po_data: Dict, invoice_data: Dict) -> List[str]:
        prompt = f"""Identify potential issues and discrepancies between these documents:

PO Data: {json.dumps(po_data, indent=2)}
Invoice Data: {json.dumps(invoice_data, indent=2)}

List each issue as a separate item:"""
        
        response = self.inference.generate(prompt)
        issues = [line.strip() for line in response.split('\n') if line.strip() and not line.startswith('List')]
        return issues

class Gemma3IntelligentQueryProcessor:
    def __init__(self, model_path: str = r"C:\Users\abhik\Downloads\sales\salesbot\gemma3-text2sql-merged"):
        self.inference = Gemma3Inference(model_path)
    
    def classify_query(self, query: str) -> str:
        prompt = f"""Classify this query into one category:

Query: {query}

Categories: [document_comparison, financial_analysis, discrepancy_detection, data_extraction, general_question]

Classification:"""
        
        response = self.inference.generate(prompt, max_length=50).strip().lower()
        
        valid_categories = ['document_comparison', 'financial_analysis', 'discrepancy_detection', 'data_extraction', 'general_question']
        for cat in valid_categories:
            if cat in response:
                return cat
        return 'general_question'
    
    def generate_follow_up_questions(self, query: str, document_summary: str) -> List[str]:
        prompt = f"""Based on this query and document context, generate 3 relevant follow-up questions:

Query: {query}
Document Summary: {document_summary}

Follow-up questions:"""
        
        response = self.inference.generate(prompt, max_length=300)
        questions = [q.strip() for q in response.split('\n') if q.strip() and not q.startswith('Follow')]
        return questions[:3]
    
    def summarize_document(self, document_text: str) -> str:
        prompt = f"""Create a concise summary of this document:

{document_text[:2000]}

Summary:"""
        
        return self.inference.generate(prompt, max_length=300)
