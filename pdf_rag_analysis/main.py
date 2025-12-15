#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from src.orchestrator import PDFAnalysisOrchestrator

try:
    from src.chatbot import start_interactive_chat
except Exception:
    from src.chatbot_simple import start_simple_interactive_chat as start_interactive_chat


def main():
    parser = argparse.ArgumentParser(
        description="PDF Document Analysis with RAG and Chatbot"
    )
    
    parser.add_argument(
        '--mode',
        choices=['pipeline', 'chat', 'agent', 'interactive'],
        default='pipeline',
        help='Mode of operation'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        help='Query for agent or chatbot mode'
    )
    
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=Path(__file__).parent / 'data',
        help='Directory containing PDF files'
    )
    
    parser.add_argument(
        '--reports-dir',
        type=Path,
        default=Path(__file__).parent / 'reports',
        help='Directory for generated reports'
    )
    
    args = parser.parse_args()
    
    orchestrator = PDFAnalysisOrchestrator()
    
    if args.mode == 'pipeline':
        print("\n[RUNNING] Complete Pipeline Analysis")
        orchestrator.run_complete_pipeline()
        orchestrator.print_pipeline_summary()
        
        print("\nStarting interactive mode...")
        orchestrator.interactive_analysis()
    
    elif args.mode == 'chat':
        orchestrator.run_complete_pipeline()
        
        if args.query:
            response = orchestrator.chat(args.query)
            print(f"\nResponse:\n{response['response']}")
        else:
            start_interactive_chat(orchestrator.rag_system)
    
    elif args.mode == 'agent':
        orchestrator.run_complete_pipeline()
        
        if args.query:
            response = orchestrator.analyze_with_agent(args.query)
            print(f"\nAgent Analysis:\n{response}")
        else:
            print("Please provide a query with --query flag")
    
    elif args.mode == 'interactive':
        orchestrator.run_complete_pipeline()
        orchestrator.interactive_analysis()


if __name__ == "__main__":
    main()
