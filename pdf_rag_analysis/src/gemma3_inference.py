import torch
from typing import Optional, List
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import os

class Gemma3Inference:
    def __init__(self, model_path: str = r"C:\Users\abhik\Downloads\sales\salesbot\gemma3-text2sql-merged", 
                 device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.tokenizer = None
        self.loaded = False
        
    def load_model(self):
        if self.loaded:
            return
            
        print(f"Loading Gemma3 model from {self.model_path}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map="auto",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            self.loaded = True
            print(f"Model loaded successfully on device: {self.device}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def generate(self, prompt: str, max_length: int = 512, temperature: float = 0.7, top_p: float = 0.9) -> str:
        if not self.loaded:
            self.load_model()
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
    
    def analyze_discrepancies(self, po_items: List[dict], invoice_items: List[dict]) -> str:
        prompt = f"""You are an expert financial auditor analyzing discrepancies between Purchase Orders and Proforma Invoices.

PO Items:
{json.dumps(po_items, indent=2)}

Invoice Items:
{json.dumps(invoice_items, indent=2)}

Provide a clear analysis of:
1. Key discrepancies found
2. Financial impact
3. Recommended actions

Analysis:"""
        
        return self.generate(prompt)
    
    def answer_question(self, context: str, question: str) -> str:
        prompt = f"""Based on the following document content:

{context}

Answer this question: {question}

Answer:"""
        
        return self.generate(prompt)
    
    def extract_summary(self, document_text: str) -> str:
        prompt = f"""Summarize the key information from this document:

{document_text}

Summary:"""
        
        return self.generate(prompt)
    
    def unload_model(self):
        if self.loaded:
            del self.model
            del self.tokenizer
            torch.cuda.empty_cache()
            self.loaded = False
            print("Model unloaded from memory")
