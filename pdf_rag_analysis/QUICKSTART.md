# Quick Start Guide

Get up and running with the PDF Analysis System in 5 minutes!

## 1. Installation

### One-time Setup
```bash
# Clone/navigate to the project directory
cd pdf_rag_analysis

# Run setup script
python setup.py
```

This will:
- Create necessary directories
- Install all dependencies
- Create `.env` file from template

### Manual Setup (Alternative)
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
```

## 2. Configuration

Edit `.env` file and add your API key:
```
OPENAI_API_KEY=sk-your-key-here
```

Optional: Add Groq API key for faster inference
```
GROQ_API_KEY=your-groq-key-here
```

## 3. Add PDF Files

Place your PDF documents in the `data/` directory:
```
pdf_rag_analysis/
├── data/
│   ├── Purchase_Order_2025-12-12.pdf
│   ├── Proforma_Invoice_2025-12-12.pdf
│   └── (add your PDFs here)
```

## 4. Run the System

### Option A: Complete Pipeline (Recommended)
```bash
python main.py --mode pipeline
```

This will:
1. ✓ Extract data from PDFs
2. ✓ Compare PO with Invoice
3. ✓ Generate reports (JSON, CSV, Excel, HTML)
4. ✓ Initialize RAG system with ChromaDB
5. ✓ Start interactive chatbot

### Option B: Just Chat
```bash
python main.py --mode chat
```

### Option C: Run Examples
```bash
# Run all examples
python examples.py

# Run specific example
python examples.py extraction  # extraction, comparison, reports, rag, agent, chatbot, pipeline
```

## 5. Interactive Usage

Once the pipeline completes, you'll see a prompt:
```
Query> 
```

Ask natural language questions:
```
Query> What items are missing from the invoice?
Query> What are the main discrepancies?
Query> What is the total difference?
Query> What would you recommend?
```

Special commands:
- `compare` - Show detailed comparison
- `discrepancies` - List top discrepancies
- `summary` - Show system summary
- `help` - Show available commands
- `exit` - Exit the program

## 6. Generated Reports

Reports are automatically saved to `reports/` directory:

- **comparison_report.json** - Structured data format
- **comparison_report.csv** - Spreadsheet format
- **comparison_report.xlsx** - Excel with multiple sheets
- **comparison_report.html** - Visual HTML report

## Common Workflows

### Analyze Specific Item
```
Query> What are the details for Widget A?
Query> Show me the pricing history for item 123
```

### Find Discrepancies
```
Query> Which items have quantity mismatches?
Query> What are the price differences?
Query> Show me all missing items
```

### Get Recommendations
```
Query> What should I do about these discrepancies?
Query> Which issues are critical?
Query> How should I contact the vendor?
```

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "OPENAI_API_KEY not found"
Make sure you:
1. Create `.env` file
2. Add your OpenAI API key
3. Keys should look like: `sk-...`

### PDFs not being extracted
- Check PDFs are in `data/` directory
- Ensure PDFs are text-based (not scanned images)
- Try opening PDFs manually to verify they're valid

### Slow performance
- First run downloads embeddings (~200MB) - this is normal
- Subsequent runs will be faster
- RAG search typically takes 2-3 seconds

### CUDA/GPU not detected
The system works fine on CPU. To use GPU:
1. Install CUDA-compatible PyTorch
2. Set `EMBEDDING_DEVICE=cuda` in `.env`

## File Structure

```
pdf_rag_analysis/
├── data/                    # Input PDFs go here
├── reports/                 # Generated reports
├── chroma_db/               # Vector database storage
├── src/
│   ├── config.py           # Configuration
│   ├── pdf_extractor.py    # PDF parsing
│   ├── comparator.py       # PO vs Invoice comparison
│   ├── report_generator.py # Report generation
│   ├── rag_system.py       # RAG + ChromaDB
│   ├── agent_rag.py        # LangChain agent
│   ├── chatbot.py          # Interactive chatbot
│   └── orchestrator.py     # Main orchestrator
├── main.py                  # CLI entry point
├── examples.py              # Example usage
├── setup.py                 # Setup script
├── requirements.txt         # Dependencies
├── .env                     # Configuration (create from .env.example)
└── README.md                # Full documentation
```

## Next Steps

1. **Explore Reports**: Check the generated reports in `reports/`
2. **Run Examples**: `python examples.py` to see all capabilities
3. **Read Full Docs**: See `README.md` for detailed documentation
4. **Customize**: Adjust settings in `src/config.py`

## API Limits & Costs

OpenAI Pricing (approximate):
- GPT-4 Turbo: $0.01 per 1K input tokens, $0.03 per 1K output tokens
- Embeddings: ~$0.02 per 1M tokens

For free/low-cost usage:
- Use smaller models (gpt-3.5-turbo)
- Reduce chunk size
- Limit result retrieval
- Use Groq API (alternative, free tier available)

## Getting Help

- Check troubleshooting section above
- Review `README.md` for detailed docs
- Check `.env` configuration
- Verify PDFs are in correct format
- Run `python setup.py` again to verify installation

## Tips & Tricks

### Speed Up Processing
```python
# Reduce chunk size in .env
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### Better Accuracy
```python
# Use higher temperature for more creative responses
LLM_TEMPERATURE=0.9

# Use larger model
LLM_MODEL=gpt-4-turbo-preview
```

### Multi-Language Support
Query in any language - the system will handle translation automatically!

```
Query> ¿Cuáles son las discrepancias principales?  (Spanish)
Query> Quelles sont les principales divergences?   (French)
```

## Performance Tips

1. **First Run**: Takes longer (downloads embeddings model)
2. **Batch Processing**: Process multiple PDFs at once
3. **Memory**: Each document adds ~1-2MB to vector database
4. **Chunk Size**: Larger chunks = faster but less precise

## Advanced Usage

See `README.md` for:
- Programmatic API usage
- Custom configuration
- Advanced RAG features
- Integration options
