"""
Fine-tuned Gemma-2B SQL Generation Agent
Integrates fine-tuned Gemma-2B model for Text-to-SQL generation
"""

import os
from pathlib import Path
from typing import Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

# Authenticate with HuggingFace if token available
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    try:
        login(token=hf_token, add_to_git_credential=False)
    except Exception:
        pass  # Silent fail - not fatal if auth fails


class GemmaSQLAgent:
    """Generate SQL using fine-tuned Gemma-2B model"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize Gemma SQL Agent
        
        Args:
            model_path: Path to fine-tuned model. If None, tries default locations.
        """
        self.model_path = model_path or self._find_model()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        
        if self.model_path and Path(self.model_path).exists():
            self._load_model()
    
    def _find_model(self) -> Optional[str]:
        """Find fine-tuned model in default locations"""
        candidates = [
            "models/gemma-2b-text2sql-merged",
            "models/gemma-2b-text2sql",
            "../models/gemma-2b-text2sql-merged",
            "../models/gemma-2b-text2sql",
        ]
        
        for path in candidates:
            if Path(path).exists():
                return path
        
        return None
    
    def _load_model(self):
        """Load model and tokenizer"""
        try:
            print(f"[*] Loading Gemma from {self.model_path}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
            )
            
            print(f"[OK] Gemma model loaded from {self.model_path}")
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            self.model = None
            self.tokenizer = None
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.tokenizer is not None
    
    def generate_sql(self, prompt: str, max_length: int = 256) -> str:
        """
        Generate SQL using the fine-tuned model
        
        Args:
            prompt: Input prompt with schema and query context
            max_length: Maximum tokens to generate
            
        Returns:
            Generated SQL query
        """
        if not self.is_loaded():
            return None
        
        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
            
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            sql = self._extract_sql(generated_text)
            return sql
        except Exception as e:
            print(f"[ERROR] Failed to generate SQL: {e}")
            return None
    
    def _extract_sql(self, text: str) -> str:
        """Extract SQL query from generated text"""
        if "<start_of_turn>model" in text:
            parts = text.split("<start_of_turn>model")
            if len(parts) > 1:
                sql = parts[1].split("<end_of_turn>")[0].strip()
                return sql
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.upper().startswith('SELECT'):
                return '\n'.join(lines[i:]).strip()
        
        return text.strip()
    
    def generate(self, intent: Dict, entities: Dict) -> Dict:
        """
        Generate SQL from intent and entities
        Matches interface of other SQL agents
        
        Args:
            intent: Intent classification result
            entities: Extracted entities
            
        Returns:
            Dict with sql, error, etc.
        """
        if not self.is_loaded():
            return {
                "sql": None,
                "error": "Gemma model not loaded"
            }
        
        prompt = self._build_prompt(intent, entities)
        
        try:
            sql = self.generate_sql(prompt)
            return {
                "sql": sql,
                "error": None
            }
        except Exception as e:
            return {
                "sql": None,
                "error": str(e)
            }
    
    def _build_prompt(self, intent: Dict, entities: Dict) -> str:
        """Build prompt for SQL generation"""
        intent_type = intent.get("type", "unknown")
        
        prompt = f"""<start_of_turn>user
Generate SQL for the following query.

Intent: {intent_type}
Entities: {entities}

Generate the SQL query:
<end_of_turn>
<start_of_turn>model
"""
        return prompt
