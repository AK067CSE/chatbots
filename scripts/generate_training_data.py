"""
Training Data Extraction Pipeline
Extracts query-to-SQL mappings from DuckDB for fine-tuning Gemma-2b
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.duckdb_client import DuckDBClient
from src.sql import templates as T
from src.agents.entity_extractor import extract_entities
from src.agents.intent_classifier import detect_intent

class TrainingDataGenerator:
    """
    Generates training data for Gemma-2b Text-to-SQL fine-tuning.
    Converts natural language queries + SQL context into structured training examples.
    """
    
    def __init__(self, db_path: str = "data/sales.duckdb"):
        self.db = DuckDBClient(db_path)
        self.training_examples = []
    
    def get_schema_info(self) -> str:
        """Fetch database schema for context."""
        schema_query = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_name IN ('sales', 'active_store')
        ORDER BY table_name, column_name
        """
        schema_df = self.db.fetchdf(schema_query)
        
        # Format schema
        schema_text = "Database Schema:\n"
        current_table = None
        for _, row in schema_df.iterrows():
            if row['table_name'] != current_table:
                schema_text += f"\nTable: {row['table_name']}\n"
                current_table = row['table_name']
            schema_text += f"  - {row['column_name']}: {row['data_type']}\n"
        
        return schema_text
    
    def generate_sales_examples(self) -> list:
        """Generate training examples for sales queries."""
        examples = []
        
        # 1. Total sales examples
        years = [2024, 2025]
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN"]
        brands = ["Delmond", "Titz", "Rasbury", "Delphy"]
        
        for brand in brands:
            for year in years:
                for month in months:
                    question = f"Total sales for {brand} in {month} {year}"
                    sql = T.sql_sales_total(brand=brand, month=month, year=year)
                    
                    examples.append({
                        "instruction": "Convert the following natural language query to SQL:",
                        "input": f"Question: {question}\n\nDatabase: Sales database with sales table",
                        "output": sql,
                        "query_type": "sales_total",
                        "brand": brand,
                        "month": month,
                        "year": year
                    })
        
        # 2. Year-over-year comparison examples
        for brand in brands:
            question = f"Compare {brand} sales 2024 vs 2025"
            sql = T.sql_sales_yoy(brand=brand, year_1=2024, year_2=2025)
            
            examples.append({
                "instruction": "Convert the following natural language query to SQL:",
                "input": f"Question: {question}\n\nDatabase: Sales database",
                "output": sql,
                "query_type": "sales_yoy",
                "brand": brand
            })
        
        # 3. Summarization examples
        dimensions = [("region", "Retailer Group"), ("brand", "Brand")]
        
        for dim, col in dimensions:
            question = f"Summarize sales by {dim}"
            sql = T.sql_sales_summary(group_by=dim, year=2025)
            
            examples.append({
                "instruction": "Convert natural language to SQL for sales summary:",
                "input": f"Question: {question}\n\nDatabase: Sales database with dimensions",
                "output": sql,
                "query_type": "sales_summary",
                "dimension": dim
            })
        
        # 4. Top N examples
        for n in [3, 5, 10]:
            question = f"Top {n} brands by sales in 2025"
            sql = T.sql_sales_summary(group_by="brand", year=2025, top_n=n)
            
            examples.append({
                "instruction": "Generate SQL for top N query:",
                "input": f"Question: {question}\n\nDatabase: Sales data",
                "output": sql,
                "query_type": "sales_top_n",
                "top_n": n
            })
        
        return examples
    
    def generate_active_store_examples(self) -> list:
        """Generate training examples for active store queries."""
        examples = []
        
        # 1. Total active stores
        brands = ["Delmond", "Titz", "Rasbury"]
        for brand in brands:
            for year in [2024, 2025]:
                question = f"Total active stores for {brand} in {year}"
                sql = T.sql_active_store_total(brand=brand, year=year)
                
                examples.append({
                    "instruction": "Convert natural language to SQL for active stores:",
                    "input": f"Question: {question}\n\nDatabase: Store transactions database",
                    "output": sql,
                    "query_type": "active_store_total",
                    "brand": brand,
                    "year": year
                })
        
        # 2. Active store YoY
        for brand in brands:
            question = f"Compare active stores {brand} 2024 vs 2025"
            sql = T.sql_active_store_yoy(brand=brand, year_1=2024, year_2=2025)
            
            examples.append({
                "instruction": "Generate SQL for year-over-year store comparison:",
                "input": f"Question: {question}\n\nDatabase: Store data",
                "output": sql,
                "query_type": "active_store_yoy",
                "brand": brand
            })
        
        # 3. Active store by dimension
        for dim in ["region", "brand"]:
            question = f"Active stores by {dim}"
            sql = T.sql_active_store_summary(group_by=dim, year=2025)
            
            examples.append({
                "instruction": "Generate SQL for store summary by dimension:",
                "input": f"Question: {question}\n\nDatabase: Store data",
                "output": sql,
                "query_type": "active_store_summary",
                "dimension": dim
            })
        
        return examples
    
    def generate_gemma_format(self, example: dict) -> str:
        """
        Format example in Gemma-2b instruction format.
        Uses <start_of_turn>user / <start_of_turn>model tags.
        """
        instruction = example.get("instruction", "Convert to SQL")
        input_text = example.get("input", "")
        output_text = example.get("output", "")
        
        prompt = f"""<start_of_turn>user
{instruction}

{input_text}
<end_of_turn>
<start_of_turn>model
{output_text}
<end_of_turn>"""
        
        return prompt
    
    def generate_all_examples(self) -> list:
        """Generate all training examples."""
        print("[*] Generating training data...")
        
        examples = []
        examples.extend(self.generate_sales_examples())
        examples.extend(self.generate_active_store_examples())
        
        print(f"[OK] Generated {len(examples)} training examples")
        return examples
    
    def save_to_jsonl(self, output_path: str = "data/training_data.jsonl"):
        """Save training examples to JSONL format."""
        examples = self.generate_all_examples()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            for example in examples:
                # Add Gemma format prompt to example
                example['prompt'] = self.generate_gemma_format(example)
                f.write(json.dumps(example) + '\n')
        
        print(f"[OK] Saved {len(examples)} examples to {output_path}")
        return output_path
    
    def save_by_type(self, output_dir: str = "data/training_splits"):
        """Save training examples split by query type."""
        examples = self.generate_all_examples()
        
        # Group by query type
        by_type = {}
        for ex in examples:
            query_type = ex.get('query_type', 'unknown')
            if query_type not in by_type:
                by_type[query_type] = []
            by_type[query_type].append(ex)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each type
        for query_type, exs in by_type.items():
            output_path = os.path.join(output_dir, f"{query_type}.jsonl")
            with open(output_path, 'w') as f:
                for ex in exs:
                    ex['prompt'] = self.generate_gemma_format(ex)
                    f.write(json.dumps(ex) + '\n')
            print(f"[OK] Saved {len(exs)} {query_type} examples to {output_path}")

if __name__ == "__main__":
    generator = TrainingDataGenerator()
    
    # Generate and save all training data
    generator.save_to_jsonl("data/training_data.jsonl")
    
    # Also save by type for analysis
    generator.save_by_type("data/training_splits")
    
    print("\n[DONE] Training data generation complete!")
    print("Files created:")
    print("  - data/training_data.jsonl (Complete dataset)")
    print("  - data/training_splits/*.jsonl (Split by query type)")
