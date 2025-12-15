#!/usr/bin/env python3
# tests/comprehensive_test.py
"""
Comprehensive test of all query types supported by the chatbot.
Tests:
1. Sales Queries (total, compare, summarize)
2. Active Store Queries (total, compare, summarize)
3. Advanced/Bonus Queries (top N, rankings)
4. Chart generation
"""

import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.sql_rag_router import SQLRAGRouter

router = SQLRAGRouter()

# ==============================================================================
# SALES QUERIES
# ==============================================================================
SALES_QUERIES = [
    # 1. Total sales for specific brand in specific month
    {
        "question": "Total sales for Delmond in Jan 2024",
        "type": "sales_total",
        "expected": "Single row with total_sales"
    },
    {
        "question": "What are the sales for Titz in March 2025?",
        "type": "sales_total",
        "expected": "Single row with total_sales"
    },
    
    # 2. Compare sales year-over-year
    {
        "question": "Compare Delmond sales 2024 vs 2025",
        "type": "sales_yoy",
        "expected": "Two rows (2024 and 2025)"
    },
    {
        "question": "How did Titz sales change from 2024 to 2025?",
        "type": "sales_yoy",
        "expected": "Year comparison"
    },
    
    # 3. Summarize sales by dimension
    {
        "question": "Summarize sales by region",
        "type": "sales_summary",
        "expected": "Multiple regions with sales totals"
    },
    {
        "question": "Break down sales by brand",
        "type": "sales_summary",
        "expected": "Top brands"
    },
    {
        "question": "Top 5 brands by sales in 2025",
        "type": "sales_summary_top_n",
        "expected": "Top 5 brands sorted by sales"
    },
]

# ==============================================================================
# ACTIVE STORE QUERIES
# ==============================================================================
ACTIVE_STORE_QUERIES = [
    # 1. Total active stores for specific brand/month
    {
        "question": "Total active stores for Delmond in Feb 2024",
        "type": "active_store_total",
        "expected": "Single row with active_stores count"
    },
    {
        "question": "How many stores were invoiced for Titz in Jan 2025?",
        "type": "active_store_total",
        "expected": "Store count"
    },
    
    # 2. Compare active stores year-over-year
    {
        "question": "Compare active stores 2024 vs 2025",
        "type": "active_store_yoy",
        "expected": "Two rows with year comparison"
    },
    {
        "question": "How did store count change from 2024 to 2025?",
        "type": "active_store_yoy",
        "expected": "Year comparison"
    },
    
    # 3. Summarize active stores by dimension
    {
        "question": "Active stores by region",
        "type": "active_store_summary",
        "expected": "Stores breakdown by region"
    },
    {
        "question": "Summarize active stores by brand in 2025",
        "type": "active_store_summary",
        "expected": "Brands with store counts"
    },
    {
        "question": "Top 5 brands by active stores in 2025",
        "type": "active_store_summary_top_n",
        "expected": "Top 5 brands by store count"
    },
]

# ==============================================================================
# ADVANCED/BONUS QUERIES
# ==============================================================================
ADVANCED_QUERIES = [
    {
        "question": "Top 5 products by sales in 2024",
        "type": "advanced_top_n",
        "expected": "Top 5 products/items"
    },
    {
        "question": "Top 10 brands by sales last quarter vs same quarter last year",
        "type": "advanced_quarterly",
        "expected": "Advanced comparison"
    },
]

# ==============================================================================
# TEST EXECUTION
# ==============================================================================

def test_query(question, query_type, expected):
    """Test a single query and report results."""
    try:
        result = router.route(question)
        
        success = {
            "✅": True,
            "question": question,
            "engine": result.get("engine"),
            "data_rows": len(result.get("data", [])) if result.get("data") is not None else 0,
            "has_sql": bool(result.get("sql")),
            "has_chart": result.get("chart") is not None,
            "has_explanation": bool(result.get("explanation") or result.get("analysis")),
        }
        
        return success
        
    except Exception as e:
        return {
            "❌": True,
            "question": question,
            "error": str(e)[:100]
        }

def run_all_tests():
    """Run all test categories."""
    
    all_queries = (
        [("SALES", SALES_QUERIES)] +
        [("ACTIVE_STORE", ACTIVE_STORE_QUERIES)] +
        [("ADVANCED", ADVANCED_QUERIES)]
    )
    
    total_pass = 0
    total_fail = 0
    
    for category, queries in all_queries:
        print(f"\n{'='*80}")
        print(f"  {category} QUERIES")
        print(f"{'='*80}")
        
        for q_dict in queries:
            result = test_query(q_dict["question"], q_dict["type"], q_dict["expected"])
            
            if "✅" in result:
                total_pass += 1
                status = "✅ PASS"
                print(f"{status} | {result['question'][:50]}")
                print(f"     Engine: {result['engine']:8} | Rows: {result['data_rows']:3} | Chart: {result['has_chart']} | Explanation: {result['has_explanation']}")
            else:
                total_fail += 1
                status = "❌ FAIL"
                print(f"{status} | {result['question'][:50]}")
                print(f"     Error: {result['error']}")
        
    print(f"\n{'='*80}")
    print(f"  SUMMARY: {total_pass} PASSED | {total_fail} FAILED")
    print(f"{'='*80}\n")
    
    return total_pass, total_fail

if __name__ == "__main__":
    passed, failed = run_all_tests()
    exit(0 if failed == 0 else 1)
