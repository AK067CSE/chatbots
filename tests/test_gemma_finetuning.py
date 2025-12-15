"""
Comprehensive test suite for fine-tuned Gemma-2B Text-to-SQL system
Tests include: model loading, inference, RAG retrieval, multi-agent orchestration, and end-to-end flows
"""

import sys
from pathlib import Path
import unittest
from typing import Dict, List, Any
import json

import torch
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.langgraph_multi_agent import (
    MultiAgentOrchestrator,
    IntentClassifierAgent,
    EntityExtractionAgent,
    SQLGenerationAgent,
)
from src.rag.enhanced_rag_builder import EnhancedRAGBuilder, RAGQueryEnhancer
from src.db.duckdb_client import DuckDBClient


class TestGemmaModelLoading(unittest.TestCase):
    """Test fine-tuned Gemma model loading and basic operations"""
    
    @classmethod
    def setUpClass(cls):
        """Load model once for all tests"""
        cls.model_path = "../models/gemma-2b-text2sql-merged"
        cls.skip_gpu_tests = not torch.cuda.is_available()
    
    def test_model_exists(self):
        """Test that model files exist"""
        model_dir = Path(self.model_path)
        self.assertTrue(model_dir.exists(), f"Model directory not found: {self.model_path}")
        
        # Check for required files
        required_files = ["config.json", "generation_config.json"]
        for file in required_files:
            file_path = model_dir / file
            self.assertTrue(file_path.exists(), f"Missing required file: {file}")
    
    def test_load_tokenizer(self):
        """Test tokenizer loading"""
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.assertIsNotNone(tokenizer)
            self.assertGreater(tokenizer.vocab_size, 0)
            self.assertIsNotNone(tokenizer.eos_token)
        except Exception as e:
            self.fail(f"Failed to load tokenizer: {str(e)}")
    
    def test_load_model(self):
        """Test model loading with quantization"""
        try:
            model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map="auto" if torch.cuda.is_available() else None,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
            self.assertIsNotNone(model)
            self.assertTrue(hasattr(model, 'generate'))
        except Exception as e:
            self.fail(f"Failed to load model: {str(e)}")


class TestIntentClassification(unittest.TestCase):
    """Test intent classification agent"""
    
    @classmethod
    def setUpClass(cls):
        cls.agent = IntentClassifierAgent()
    
    def test_sales_intent(self):
        """Test sales query intent classification"""
        result = self.agent.classify("What were total sales in 2023?")
        self.assertIn("type", result)
        self.assertEqual(result["type"].lower(), "total_sales")
    
    def test_comparison_intent(self):
        """Test comparison query intent"""
        result = self.agent.classify("Compare sales between 2023 and 2024")
        self.assertIn("type", result)
        self.assertEqual(result["type"].lower(), "sales_comparison")
    
    def test_active_store_intent(self):
        """Test active store query intent"""
        result = self.agent.classify("How many active stores do we have?")
        self.assertIn("type", result)
        self.assertIn("active_store", result["type"].lower())


class TestEntityExtraction(unittest.TestCase):
    """Test entity extraction agent"""
    
    @classmethod
    def setUpClass(cls):
        cls.agent = EntityExtractionAgent()
    
    def test_metric_extraction(self):
        """Test metric extraction"""
        intent = {"type": "total_sales"}
        result = self.agent.extract("What were total sales in 2023?", intent)
        
        self.assertIn("metrics", result)
        self.assertIsInstance(result["metrics"], list)
    
    def test_time_filter_extraction(self):
        """Test time period filter extraction"""
        intent = {"type": "sales_comparison"}
        result = self.agent.extract("Sales in 2023 vs 2024", intent)
        
        self.assertIn("filters", result)
    
    def test_group_by_extraction(self):
        """Test group by extraction"""
        intent = {"type": "sales_by_brand"}
        result = self.agent.extract("Top 5 brands by sales", intent)
        
        self.assertIn("group_by", result)


class TestSQLGeneration(unittest.TestCase):
    """Test SQL generation agent"""
    
    @classmethod
    def setUpClass(cls):
        cls.agent = SQLGenerationAgent()
    
    def test_sales_sql_generation(self):
        """Test SQL generation for sales query"""
        intent = {"type": "total_sales"}
        entities = {
            "metrics": ["amount"],
            "filters": {"year": 2023},
        }
        
        result = self.agent.generate(intent, entities)
        
        self.assertIn("sql", result)
        if result["sql"]:
            self.assertIn("SELECT", result["sql"].upper())
            self.assertIn("SUM", result["sql"].upper())
    
    def test_sql_execution(self):
        """Test SQL execution"""
        sql = "SELECT COUNT(*) as count FROM sales LIMIT 1"
        result = self.agent.execute(sql)
        
        self.assertIsNotNone(result["results"])
        self.assertEqual(result["row_count"], 1)
    
    def test_invalid_sql_handling(self):
        """Test handling of invalid SQL"""
        result = self.agent.execute("SELECT * FROM nonexistent_table")
        
        self.assertIsNotNone(result["error"])
        self.assertIsNone(result["results"])


class TestRAGSystem(unittest.TestCase):
    """Test RAG retrieval and enhancement"""
    
    @classmethod
    def setUpClass(cls):
        cls.rag = EnhancedRAGBuilder()
        # Load existing vector store if available, else create
        try:
            cls.rag.load_vector_store()
        except:
            print("Building RAG knowledge base...")
            cls.rag.create_knowledge_base()
    
    def test_schema_retrieval(self):
        """Test database schema retrieval"""
        result = self.rag.retrieve("Total sales query")
        
        self.assertIsNotNone(result.schema_info)
        self.assertIn("sales", result.schema_info.lower())
    
    def test_pattern_retrieval(self):
        """Test SQL pattern retrieval"""
        result = self.rag.retrieve("How to query sales?")
        
        self.assertGreater(len(result.relevant_patterns), 0)
    
    def test_context_generation(self):
        """Test full context generation"""
        result = self.rag.retrieve("Sales by brand 2024")
        
        self.assertIsNotNone(result.context)
        self.assertGreater(len(result.context), 0)


class TestRAGEnhancer(unittest.TestCase):
    """Test RAG query enhancement"""
    
    @classmethod
    def setUpClass(cls):
        cls.enhancer = RAGQueryEnhancer()
    
    def test_prompt_enhancement(self):
        """Test prompt enhancement with RAG context"""
        query = "Total sales 2023"
        enhanced = self.enhancer.enhance_prompt(query)
        
        self.assertIsNotNone(enhanced)
        self.assertIn(query, enhanced)
        self.assertIn("Schema", enhanced)
    
    def test_context_retrieval(self):
        """Test full context retrieval"""
        context = self.enhancer.get_context("Sales comparison query")
        
        self.assertIn("query", context)
        self.assertIn("schema", context)
        self.assertIn("patterns", context)
        self.assertIn("examples", context)


class TestMultiAgentOrchestrator(unittest.TestCase):
    """Test multi-agent orchestration"""
    
    @classmethod
    def setUpClass(cls):
        cls.orchestrator = MultiAgentOrchestrator()
    
    def test_simple_query_processing(self):
        """Test processing simple query end-to-end"""
        query = "What were total sales in 2023?"
        state = self.orchestrator.process(query, use_rag=False)
        
        self.assertEqual(state.user_query, query)
        self.assertIsNotNone(state.intent)
    
    def test_query_with_rag(self):
        """Test query processing with RAG enhancement"""
        query = "Top 5 brands by sales"
        state = self.orchestrator.process(query, use_rag=True)
        
        self.assertIsNotNone(state.rag_context)
    
    def test_state_to_dict(self):
        """Test AgentState serialization"""
        query = "Active stores by region"
        state = self.orchestrator.process(query)
        
        state_dict = state.to_dict()
        self.assertIsInstance(state_dict, dict)
        self.assertIn("user_query", state_dict)
        self.assertIn("intent", state_dict)


class TestEndToEndFlow(unittest.TestCase):
    """Test complete end-to-end flows"""
    
    @classmethod
    def setUpClass(cls):
        cls.orchestrator = MultiAgentOrchestrator()
        cls.db = DuckDBClient()
    
    def test_sales_query_flow(self):
        """Test complete flow for sales query"""
        query = "What were total sales in 2023?"
        
        state = self.orchestrator.process(query, use_rag=True)
        
        # Verify complete flow
        self.assertIsNotNone(state.intent)
        self.assertIsNotNone(state.entities)
        self.assertIsNotNone(state.sql)
        self.assertIsNotNone(state.results_df)
        self.assertIsNone(state.error)
    
    def test_comparison_query_flow(self):
        """Test complete flow for comparison query"""
        query = "Compare sales between 2023 and 2024"
        
        state = self.orchestrator.process(query, use_rag=False)
        
        self.assertIsNotNone(state.intent)
        self.assertEqual(len(state.results_df), 2)  # 2 years
    
    def test_error_handling_flow(self):
        """Test error handling in processing"""
        query = "Some random nonsensical query xyz abc 123"
        
        state = self.orchestrator.process(query)
        
        # Should handle gracefully
        self.assertIsNotNone(state.user_query)


class TestPerformance(unittest.TestCase):
    """Test system performance metrics"""
    
    @classmethod
    def setUpClass(cls):
        cls.orchestrator = MultiAgentOrchestrator()
    
    def test_intent_classification_performance(self):
        """Test intent classification speed"""
        import time
        
        query = "Total sales 2023"
        agent = IntentClassifierAgent()
        
        start = time.time()
        agent.classify(query)
        elapsed = time.time() - start
        
        # Should be fast (< 100ms on CPU)
        self.assertLess(elapsed, 1.0, f"Intent classification too slow: {elapsed:.2f}s")
    
    def test_sql_generation_performance(self):
        """Test SQL generation speed"""
        import time
        
        agent = SQLGenerationAgent()
        intent = {"type": "total_sales"}
        entities = {"metrics": ["amount"]}
        
        start = time.time()
        agent.generate(intent, entities)
        elapsed = time.time() - start
        
        # Should be fast
        self.assertLess(elapsed, 0.5)
    
    def test_query_results_count(self):
        """Test that queries return reasonable result counts"""
        agent = SQLGenerationAgent()
        sql = "SELECT * FROM sales LIMIT 100"
        
        result = agent.execute(sql)
        
        self.assertLessEqual(result["row_count"], 100)


class TestDataValidation(unittest.TestCase):
    """Test data validation and consistency"""
    
    @classmethod
    def setUpClass(cls):
        cls.db = DuckDBClient()
    
    def test_database_accessibility(self):
        """Test database connectivity"""
        tables = self.db.get_tables()
        
        self.assertGreater(len(tables), 0)
        self.assertIn("sales", tables)
    
    def test_training_data_availability(self):
        """Test training data files exist"""
        training_file = Path("../data/training_data_formatted.jsonl")
        
        self.assertTrue(training_file.exists())
        
        # Check file is valid JSONL
        with open(training_file, "r") as f:
            for line in f:
                data = json.loads(line)
                self.assertIn("text", data)


def run_test_suite(test_filter: str = None):
    """
    Run test suite with optional filtering
    
    Args:
        test_filter: Run only tests containing this string (e.g., "Intent", "RAG")
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestGemmaModelLoading,
        TestIntentClassification,
        TestEntityExtraction,
        TestSQLGeneration,
        TestRAGSystem,
        TestRAGEnhancer,
        TestMultiAgentOrchestrator,
        TestEndToEndFlow,
        TestPerformance,
        TestDataValidation,
    ]
    
    for test_class in test_classes:
        if test_filter and test_filter.lower() not in test_class.__name__.lower():
            continue
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run test suite for fine-tuned Gemma system")
    parser.add_argument("--filter", help="Filter tests by name")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("="*70)
    print("Fine-Tuned Gemma-2B Text-to-SQL System - Test Suite")
    print("="*70)
    
    result = run_test_suite(test_filter=args.filter)
    
    # Print summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
