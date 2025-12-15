# PDF Document Analysis with RAG and Intelligent Chatbot

A comprehensive system for analyzing Purchase Orders and Proforma Invoices using advanced RAG (Retrieval-Augmented Generation), ChromaDB, and intelligent chatbot capabilities.

## Features

### 1. **Advanced PDF Extraction**
- Intelligent parsing of PDF documents
- Extraction of metadata, line items, and totals
- Support for multiple document types (PO, Invoices)
- Structured data output (JSON, dataclass format)

### 2. **Document Comparison & Analysis**
- Automated PO vs Invoice comparison
- Discrepancy detection (quantity, price, missing items)
- Variance calculation and severity assessment
- Detailed item-level analysis

### 3. **Multi-Format Report Generation**
- **JSON**: Structured data format for programmatic access
- **CSV**: Spreadsheet-compatible format
- **Excel**: Rich formatting with multiple sheets (Summary, Discrepancies)
- **HTML**: Visual presentation with color-coded severity levels

### 4. **RAG System with Advanced Retrieval**
- **ChromaDB**: Persistent vector database for document chunks
- **BGE Embeddings**: High-quality semantic embeddings (BAAI/bge-base-en-v1.5)
- **RAG Fusion**: Multi-query retrieval for improved accuracy
- **Intelligent Chunking**: Semantic-aware text segmentation
- **Metadata Indexing**: Rich metadata for filtered retrieval

### 5. **Agentic RAG with LangChain**
- Document search and retrieval tools
- Discrepancy analysis tools
- Comparison summary tools
- Automatic tool selection based on queries
- Error handling and context awareness

### 6. **Intelligent Chatbot**
- **Multi-turn conversations**: Full conversation memory
- **Context-aware responses**: Retrieves relevant document chunks
- **Specialized queries**: Dedicated methods for common questions
- **Conversation history**: Maintains and uses chat history
- **RAG-enhanced**: Generates answers based on indexed documents

## Project Structure

```
pdf_rag_analysis/
├── src/
│   ├── __init__.py              # Package exports
│   ├── config.py                # Configuration management
│   ├── pdf_extractor.py         # PDF parsing and extraction
│   ├── comparator.py            # PO vs Invoice comparison
│   ├── report_generator.py      # Multi-format report generation
│   ├── rag_system.py            # ChromaDB + RAG Fusion implementation
│   ├── agent_rag.py             # LangChain agent and analysis chains
│   ├── chatbot.py               # Interactive chatbot interface
│   └── orchestrator.py          # Complete pipeline orchestration
├── data/                         # Input PDF files
├── reports/                      # Generated reports
├── chroma_db/                    # ChromaDB storage
├── main.py                       # CLI entry point
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
└── README.md                      # This file
```

## Installation

### 1. Clone or Navigate to Project Directory
```bash
cd pdf_rag_analysis
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt

# Download spacy model for text processing
python -m spacy download en_core_web_sm
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `EMBEDDING_MODEL`: BGE model name (default: BAAI/bge-base-en-v1.5)
- `LLM_MODEL`: OpenAI model (default: gpt-4-turbo-preview)

## Usage

### Option 1: Complete Pipeline (Recommended)
```bash
python main.py --mode pipeline
```
This will:
1. Extract all PDFs from the data directory
2. Compare Purchase Orders with Invoices
3. Generate reports in multiple formats
4. Initialize RAG system with ChromaDB
5. Set up analysis agent
6. Launch interactive chatbot

### Option 2: Interactive Chat Only
```bash
python main.py --mode chat
```

### Option 3: Agent Analysis
```bash
python main.py --mode agent --query "What are the main discrepancies?"
```

### Option 4: Programmatic Usage

```python
from src.orchestrator import PDFAnalysisOrchestrator

orchestrator = PDFAnalysisOrchestrator()
orchestrator.run_complete_pipeline()

# Chat with the chatbot
response = orchestrator.chat("What items are missing from the invoice?")
print(response['response'])

# Use the analysis agent
analysis = orchestrator.analyze_with_agent("Summarize the discrepancies")
print(analysis)
```

## Components Overview

### PDF Extractor
Extracts structured data from PDFs:
```python
from src.pdf_extractor import extract_all_pdfs

documents = extract_all_pdfs(Path("data"))
for name, doc in documents.items():
    print(f"{name}: {len(doc.items)} items, Total: ${doc.total:.2f}")
```

### Comparator
Compares Purchase Orders with Invoices:
```python
from src.comparator import compare_po_with_invoice

comparison = compare_po_with_invoice(po_document, invoice_document)
print(f"Discrepancies: {len(comparison.discrepancies)}")
for disc in comparison.discrepancies:
    print(f"  - {disc.description}: {disc.status}")
```

### Report Generator
Generates multi-format reports:
```python
from src.report_generator import generate_all_reports

reports = generate_all_reports(comparison, Path("reports"))
print(f"JSON: {reports['json']}")
print(f"Excel: {reports['excel']}")
```

### RAG System
Searches indexed documents:
```python
from src.rag_system import initialize_rag_system

rag = initialize_rag_system()
results = rag.search("What items have quantity mismatches?", n_results=5)

# RAG Fusion for better retrieval
from src.rag_system import RAGFusionRetriever
retriever = RAGFusionRetriever(rag)
fusion_results = retriever.retrieve_with_fusion("quantity discrepancies")
```

### Chatbot
Interactive chat interface:
```python
from src.chatbot import initialize_chatbot

chatbot = initialize_chatbot(rag_system)

# Single query
response = chatbot.chat("What's the total difference?")
print(response['response'])

# Get conversation summary
summary = chatbot.get_conversation_summary()
print(summary)
```

## API Keys & Configuration

### OpenAI API
1. Get your API key from https://platform.openai.com/api-keys
2. Add to `.env`: `OPENAI_API_KEY=sk-...`

### BGE Embeddings
- Automatically downloaded from Hugging Face
- Uses: `BAAI/bge-base-en-v1.5` (768-dim, high quality)
- Free to use, no API key needed

### Optional: Groq API
For faster inference (alternative to OpenAI):
1. Get API key from https://console.groq.com
2. Add to `.env`: `GROQ_API_KEY=...`

## RAG System Details

### ChromaDB
- **Location**: `chroma_db/` directory
- **Storage Type**: Persistent SQLite backend
- **Collection**: `pdf_documents`
- **Retrieval**: Cosine similarity search

### Embeddings
- **Model**: BAAI/bge-base-en-v1.5
- **Dimension**: 768
- **Type**: Semantic embeddings
- **Device**: CPU (configurable to GPU)

### RAG Fusion Strategy
1. Generate query variations (word removal, synonyms)
2. Retrieve top-k results for each variation
3. Reciprocal rank fusion scoring
4. Return top merged results

### Chunking Strategy
- **Size**: 1000 tokens (configurable)
- **Overlap**: 200 tokens
- **Method**: Recursive splitting (preserves sentence boundaries)
- **Metadata**: Chunk type, index, size tracking

## Output Examples

### Comparison Report (JSON)
```json
{
  "metadata": {
    "po_id": "PO123",
    "invoice_id": "INV456"
  },
  "summary_statistics": {
    "total_items_in_po": 5,
    "total_items_in_invoice": 4,
    "items_with_discrepancies": 3,
    "value_difference": -250.50
  },
  "discrepancies": [
    {
      "item_number": "1",
      "description": "Widget A",
      "quantity": {
        "po": 100,
        "invoice": 90,
        "variance_percent": -10.0
      },
      "discrepancy_type": "QUANTITY_MISMATCH",
      "severity": "HIGH"
    }
  ]
}
```

### Discrepancy Types
- `QUANTITY_MISMATCH`: Quantity differs
- `PRICE_MISMATCH`: Unit price differs
- `QUANTITY_AND_PRICE_MISMATCH`: Both differ
- `MISSING_FROM_INVOICE`: Item in PO but not invoice
- `EXTRA_IN_INVOICE`: Item in invoice but not PO
- `VERIFIED`: Item matches perfectly

### Severity Levels
- `CRITICAL`: >50% variance or missing items
- `HIGH`: 10-50% variance
- `MEDIUM`: Minor discrepancies
- `LOW`: Negligible differences

## Advanced Features

### Query Expansion in RAG Fusion
```python
retriever = RAGFusionRetriever(rag_system)
results = retriever.retrieve_with_fusion(
    "items with price discrepancies",
    n_results=5
)
```

### Document Summaries
```python
summary = rag.get_document_summary("PO123")
# Returns: doc_type, vendor, customer, total, items_count, chunks_stored
```

### Conversation Management
```python
# Get full conversation history
summary = chatbot.get_conversation_summary()

# Clear memory for new session
chatbot.reset_memory()
```

## Troubleshooting

### PDF Extraction Issues
- Ensure PDFs are text-based (not scanned images)
- Check PDF format compatibility
- Verify file permissions

### RAG/Embeddings Issues
- First run downloads BGE model (~200MB)
- Requires internet connection for model download
- Ensure sufficient disk space for ChromaDB

### LangChain/LLM Issues
- Verify API key is correct and active
- Check OpenAI API rate limits
- Ensure stable internet connection

### Performance Issues
- Increase `CHUNK_OVERLAP` for better context
- Reduce `CHUNK_SIZE` for faster processing
- Use GPU for embeddings (set `EMBEDDING_DEVICE=cuda`)

## Best Practices

1. **Data Quality**: Ensure PDFs have clean, structured layouts
2. **Chunk Size**: Adjust based on document complexity
3. **Query Formulation**: Be specific in natural language queries
4. **Memory Management**: Reset chatbot memory for new sessions
5. **Report Review**: Always review generated reports for accuracy

## Performance Metrics

- **PDF Extraction**: ~1-2 seconds per document
- **Embedding Generation**: ~0.5 seconds per 1000 tokens
- **RAG Fusion Search**: ~2-3 seconds for 5 results
- **Chatbot Response**: ~3-5 seconds (includes RAG + LLM)

## Dependencies Overview

| Library | Purpose | Version |
|---------|---------|---------|
| pypdf | PDF extraction | 4.0.1 |
| chromadb | Vector database | 0.4.22 |
| sentence-transformers | BGE embeddings | 2.2.2 |
| langchain | LLM framework | 0.1.11 |
| openai | GPT API | 1.3.9 |
| pandas | Data processing | 2.1.3 |
| openpyxl | Excel generation | 3.10.10 |

## Future Enhancements

- [ ] Web UI dashboard
- [ ] Real-time PDF upload
- [ ] Multi-language support
- [ ] Advanced visualizations
- [ ] Email notifications
- [ ] Database integration
- [ ] Batch processing
- [ ] API endpoints

## Support & Contact

For issues or questions:
1. Check the troubleshooting section
2. Review configuration in `src/config.py`
3. Check ChromaDB status in `chroma_db/`
4. Review generated reports for insights

## License

This project is provided as-is for educational and business use.

## Changelog

### Version 1.0.0
- Initial release
- PDF extraction and comparison
- Multi-format reporting
- ChromaDB + RAG Fusion
- LangChain agent
- Interactive chatbot
