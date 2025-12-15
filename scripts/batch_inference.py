"""
Batch inference script for the SalesBot Text-to-SQL system.

Usage examples:

# Run on default training queries (extracted from data/training_data_train.jsonl):
.venv\Scripts\python.exe scripts\batch_inference.py --use-rag --limit 100

# Run with a custom queries file (one query per line):
.venv\Scripts\python.exe scripts\batch_inference.py --input data/queries.txt --output-jsonl data/inference_results.jsonl --output-csv data/inference_results.csv

The script will process each natural-language query via the multi-agent orchestrator,
generate SQL, execute it against DuckDB, and save results.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional

# Ensure project is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.langgraph_multi_agent import MultiAgentOrchestrator
from src.rag.enhanced_rag_builder import EnhancedRAGBuilder


def load_queries_from_jsonl(jsonl_path: Path, limit: Optional[int] = None) -> List[str]:
    queries = []
    if not jsonl_path.exists():
        return queries
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            try:
                data = json.loads(line)
            except Exception:
                continue
            # Accept both `{ "text": "<start_of_turn>user\n..." }` and `{ "input": "..." }`
            text = data.get("text") or data.get("input") or data.get("query")
            if not text:
                continue
            # If text is formatted in Gemma instruction format, extract user portion
            if "<start_of_turn>user" in text and "<end_of_turn>" in text:
                user_part = text.split("<start_of_turn>user")[-1].split("<end_of_turn>")[0].strip()
                queries.append(user_part)
            else:
                queries.append(text.strip())
    return queries


def load_queries_from_txt(txt_path: Path, limit: Optional[int] = None) -> List[str]:
    queries = []
    if not txt_path.exists():
        return queries
    with open(txt_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            q = line.strip()
            if q:
                queries.append(q)
    return queries


def save_jsonl(path: Path, records: List[Dict[str, Any]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def save_csv(path: Path, records: List[Dict[str, Any]]):
    import csv
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        return
    keys = list(records[0].keys())
    with open(path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in records:
            # Flatten preview to string
            r_flat = dict(r)
            if isinstance(r_flat.get("preview"), list):
                r_flat["preview"] = json.dumps(r_flat["preview"], ensure_ascii=False)
            writer.writerow(r_flat)


def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser("Batch inference for SalesBot Text-to-SQL")
    parser.add_argument("--input", type=str, default=None, help="Path to input queries (txt or jsonl). If omitted, uses data/training_data_train.jsonl")
    parser.add_argument("--use-rag", action="store_true", help="Enable RAG context during generation")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of queries to process")
    parser.add_argument("--output-jsonl", type=str, default="data/inference_results.jsonl", help="Output JSONL file")
    parser.add_argument("--output-csv", type=str, default="data/inference_results.csv", help="Output CSV file")
    parser.add_argument("--dry-run", action="store_true", help="Run without executing SQL (only generate SQL)")

    args = parser.parse_args(argv)

    # Locate default training JSONL if input not provided
    if args.input:
        input_path = Path(args.input)
        if input_path.suffix.lower() in {".txt"}:
            queries = load_queries_from_txt(input_path, args.limit)
        else:
            queries = load_queries_from_jsonl(input_path, args.limit)
    else:
        default_jsonl = Path("data/training_data_train.jsonl")
        queries = load_queries_from_jsonl(default_jsonl, args.limit)

    if not queries:
        print("No queries found. Provide --input or generate training data first.")
        return

    print(f"Processing {len(queries)} queries (use_rag={args.use_rag}, dry_run={args.dry_run})")

    # Initialize orchestrator and RAG enhancer (if requested)
    orchestrator = MultiAgentOrchestrator()
    rag_enhancer = None
    if args.use_rag:
        try:
            rag_enhancer = EnhancedRAGBuilder()
            rag_enhancer.load_vector_store()
        except Exception as e:
            print(f"Warning: could not initialize RAG builder: {e}")
            rag_enhancer = None

    results = []

    for i, q in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Query: {q[:80]}{'...' if len(q) > 80 else ''}")
        try:
            state = orchestrator.process(q, use_rag=bool(rag_enhancer))
            sql = state.sql
            error = state.error
            preview = None
            row_count = None
            if not args.dry_run and state.results_df is not None:
                try:
                    row_count = len(state.results_df)
                    preview = state.results_df.head(5).to_dict(orient="records")
                except Exception:
                    preview = None
            record = {
                "query": q,
                "sql": sql,
                "error": error,
                "row_count": row_count,
                "preview": preview,
                "rag_used": bool(rag_enhancer) and (state.rag_context is not None),
            }
        except Exception as e:
            record = {"query": q, "sql": None, "error": str(e), "row_count": None, "preview": None, "rag_used": False}

        results.append(record)

    # Save outputs
    output_jsonl = Path(args.output_jsonl)
    output_csv = Path(args.output_csv)
    save_jsonl(output_jsonl, results)
    save_csv(output_csv, results)

    print(f"Saved {len(results)} records to {output_jsonl} and {output_csv}")


if __name__ == "__main__":
    main()
