"""
Fine-tune Gemma-2B for Text-to-SQL task
"""

import json
import os
from pathlib import Path
from typing import Dict, List

import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)
from peft import get_peft_model, LoraConfig, TaskType
from huggingface_hub import login

# Authenticate with HuggingFace if token available
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    try:
        login(token=hf_token, add_to_git_credential=False)
        print("[OK] HuggingFace authentication successful")
    except Exception as e:
        print(f"[WARNING] HuggingFace authentication failed: {e}")



class GemmaFineTuner:
    """Fine-tune Gemma-2B for SQL generation"""
    
    def __init__(
        self,
        model_name: str = "google/gemma-2b",
        output_dir: str = "models/gemma-2b-text2sql",
        training_data: str = "data/training_data.jsonl"
    ):
        self.model_name = model_name
        self.output_dir = output_dir
        self.training_data = training_data
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"[INFO] Using device: {self.device}")
        print(f"[INFO] Model: {model_name}")
    
    def load_training_data(self) -> List[Dict]:
        """Load training examples from JSONL"""
        examples = []
        
        if not Path(self.training_data).exists():
            raise FileNotFoundError(f"Training data not found: {self.training_data}")
        
        with open(self.training_data, "r") as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))
        
        print(f"[OK] Loaded {len(examples)} training examples")
        return examples
    
    def prepare_dataset(self, examples: List[Dict]) -> Dataset:
        """Prepare dataset for training"""
        texts = [ex["prompt"] for ex in examples]
        
        dataset = Dataset.from_dict({
            "text": texts
        })
        
        return dataset
    
    def load_model_and_tokenizer(self):
        """Load model and tokenizer"""
        print(f"[*] Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print(f"[*] Loading model...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
        )
        
        print(f"[OK] Model loaded")
    
    def setup_lora(self):
        """Setup LoRA for efficient fine-tuning"""
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,
            lora_alpha=16,
            lora_dropout=0.1,
            bias="none",
            target_modules=["q_proj", "v_proj"],
        )
        
        self.model = get_peft_model(self.model, lora_config)
        print(f"[OK] LoRA configured")
    
    def tokenize_function(self, examples):
        """Tokenize training examples"""
        return self.tokenizer(
            examples["text"],
            max_length=512,
            truncation=True,
            padding="max_length",
        )
    
    def fine_tune(self, num_epochs: int = 3, batch_size: int = 4):
        """Fine-tune the model"""
        print("\n[*] Preparing fine-tuning...")
        
        examples = self.load_training_data()
        dataset = self.prepare_dataset(examples)
        
        self.load_model_and_tokenizer()
        self.setup_lora()
        
        print(f"[*] Tokenizing dataset...")
        tokenized_dataset = dataset.map(
            self.tokenize_function,
            batched=True,
            remove_columns=["text"]
        )
        
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            save_steps=10,
            save_total_limit=2,
            logging_steps=5,
            learning_rate=2e-4,
            warmup_steps=5,
            weight_decay=0.01,
            fp16=self.device == "cuda",
            max_steps=-1,
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )
        
        print(f"[*] Starting fine-tuning...")
        trainer.train()
        
        print(f"\n[OK] Fine-tuning complete!")
        self.save_model()
    
    def save_model(self):
        """Save fine-tuned model"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"[*] Saving model to {self.output_dir}...")
        
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        
        merged_model_path = self.output_dir + "-merged"
        print(f"[*] Merging LoRA weights into base model...")
        merged_model = self.model.merge_and_unload()
        merged_model.save_pretrained(merged_model_path)
        self.tokenizer.save_pretrained(merged_model_path)
        
        print(f"[OK] LoRA model saved to: {self.output_dir}")
        print(f"[OK] Merged model saved to: {merged_model_path}")


def main():
    """Main fine-tuning pipeline"""
    print("\n" + "="*70)
    print("Gemma-2B Fine-Tuning for Text-to-SQL")
    print("="*70)
    
    finetuner = GemmaFineTuner(
        model_name="google/gemma-2b",
        output_dir="models/gemma-2b-text2sql",
        training_data="data/training_data.jsonl"
    )
    
    finetuner.fine_tune(
        num_epochs=3,
        batch_size=4
    )
    
    print("\n" + "="*70)
    print("Fine-tuning complete!")
    print("="*70)


if __name__ == "__main__":
    main()
