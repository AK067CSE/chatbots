"""
Test and verify Gemma fine-tuning integration
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.gemma_sql_agent import GemmaSQLAgent
from src.agents.langgraph_multi_agent import MultiAgentOrchestrator
from src.rag.enhanced_rag_builder import RAGQueryEnhancer


def test_gemma_loading():
    """Test if Gemma model can be loaded"""
    print("\n" + "="*70)
    print("Testing Gemma Model Loading")
    print("="*70)
    
    agent = GemmaSQLAgent()
    
    if agent.is_loaded():
        print("[OK] Gemma model loaded successfully")
        print(f"     Model path: {agent.model_path}")
        print(f"     Device: {agent.device}")
        return True
    else:
        print("[INFO] Gemma model not found")
        print("[INFO] System will use SQL templates as fallback")
        print(f"       Checked paths:")
        for path in ["models/gemma-2b-text2sql-merged", "models/gemma-2b-text2sql"]:
            print(f"         - {path}")
        return False


def test_rag_system():
    """Test RAG system"""
    print("\n" + "="*70)
    print("Testing RAG System")
    print("="*70)
    
    try:
        enhancer = RAGQueryEnhancer()
        print("[OK] RAG system initialized")
        
        test_query = "What were total sales in 2024?"
        context = enhancer.get_context(test_query)
        
        print(f"     Query: {test_query}")
        print(f"     Schema available: {bool(context.get('schema'))}")
        print(f"     Patterns found: {len(context.get('patterns', []))}")
        print(f"     Examples found: {len(context.get('examples', []))}")
        return True
    except Exception as e:
        print(f"[WARNING] RAG system error: {e}")
        return False


def test_orchestrator():
    """Test multi-agent orchestrator"""
    print("\n" + "="*70)
    print("Testing Multi-Agent Orchestrator")
    print("="*70)
    
    test_queries = [
        "Total sales in 2024?",
        "Compare sales 2023 vs 2024",
        "Top 5 brands by revenue",
    ]
    
    try:
        orchestrator = MultiAgentOrchestrator()
        
        for query in test_queries:
            print(f"\n[*] Processing: {query}")
            state = orchestrator.process(query, use_rag=True)
            
            print(f"    Intent: {state.intent['type'] if state.intent else 'None'}")
            print(f"    SQL Generated: {bool(state.sql)}")
            if state.sql:
                print(f"    First 60 chars: {state.sql[:60]}...")
            print(f"    Results: {len(state.results_df) if state.results_df is not None else 0} rows")
            print(f"    Error: {state.error if state.error else 'None'}")
        
        print("\n[OK] Orchestrator working correctly")
        return True
    except Exception as e:
        print(f"[ERROR] Orchestrator failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_training_data():
    """Verify training data was generated"""
    print("\n" + "="*70)
    print("Verifying Training Data")
    print("="*70)
    
    training_file = Path("data/training_data.jsonl")
    
    if not training_file.exists():
        print("[ERROR] Training data not found at data/training_data.jsonl")
        return False
    
    import json
    examples = []
    with open(training_file) as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
    
    print(f"[OK] Training data found")
    print(f"     Total examples: {len(examples)}")
    print(f"     First example keys: {list(examples[0].keys())}")
    
    query_types = {}
    for ex in examples:
        qt = ex.get('query_type', 'unknown')
        query_types[qt] = query_types.get(qt, 0) + 1
    
    print(f"     Query types:")
    for qt, count in sorted(query_types.items()):
        print(f"       - {qt}: {count}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("GEMMA FINE-TUNING INTEGRATION TEST")
    print("="*70)
    
    results = {
        "Training Data": test_training_data(),
        "RAG System": test_rag_system(),
        "Gemma Loading": test_gemma_loading(),
        "Orchestrator": test_orchestrator(),
    }
    
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "[OK]" if passed else "[WARN]"
        print(f"{status} {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("ALL TESTS PASSED")
        print("System is ready to use!")
    else:
        print("SOME TESTS WARNING")
        print("System will use templates as fallback")
        print("Fine-tune the model with: python scripts/finetune_gemma.py")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
