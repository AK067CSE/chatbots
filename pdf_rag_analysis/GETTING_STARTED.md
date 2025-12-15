# Getting Started - PDF Analysis & RAG Chatbot

Welcome! This guide will get you up and running in **5 minutes**.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (get it from https://platform.openai.com/api-keys)
- ~500MB disk space for embeddings and database

## 3-Step Quick Setup

### Step 1: Install Dependencies (2 min)
```bash
cd pdf_rag_analysis
python setup.py
```

This will automatically:
- Create required directories
- Install all dependencies
- Create `.env` configuration file

### Step 2: Configure API Key (1 min)
```bash
# Open .env file
notepad .env
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

Get your key from: https://platform.openai.com/api-keys

### Step 3: Run the System (2 min)
```bash
python main.py --mode pipeline
```

This will:
1. ✓ Extract PDFs from the `data/` folder
2. ✓ Compare Purchase Order with Proforma Invoice
3. ✓ Generate reports (JSON, CSV, Excel, HTML)
4. ✓ Initialize RAG system
5. ✓ Start interactive chatbot

## 🎯 What You Can Do

Once running, ask natural language questions:

```
Query> What items are missing from the invoice?
Query> Show me items with quantity mismatches
Query> What's the total value difference?
Query> What would you recommend based on these discrepancies?
Query> Help me understand the price differences
```

Type `help` for more commands.

## 📁 Important Files & Folders

| Location | Purpose |
|----------|---------|
| `data/` | Put your PDF files here |
| `reports/` | Generated comparison reports |
| `src/` | Core Python modules |
| `main.py` | Start the system here |
| `.env` | Your API keys and config |
| `README.md` | Full documentation |
| `examples.py` | Example usage patterns |

## 🚀 Usage Modes

### Mode 1: Complete Pipeline (Recommended)
```bash
python main.py --mode pipeline
```
Everything in one go + interactive chat.

### Mode 2: Chat Only
```bash
python main.py --mode chat
```
Just chat with the system.

### Mode 3: Single Query
```bash
python main.py --mode chat --query "What are the discrepancies?"
```

### Mode 4: See Examples
```bash
python examples.py                    # Run all examples
python examples.py extraction         # Just extraction
python examples.py rag                # Just RAG search
python examples.py pipeline           # Complete pipeline
```

## 📊 What Gets Generated

After running the pipeline, check the `reports/` folder:

| File | Format | Purpose |
|------|--------|---------|
| `comparison_report.json` | JSON | Structured data, programmatic access |
| `comparison_report.csv` | CSV | Excel/Spreadsheet compatible |
| `comparison_report.xlsx` | Excel | Rich formatting, multiple sheets |
| `comparison_report.html` | HTML | Visual presentation with colors |

## 🤖 System Components

```
Your PDFs
    ↓
PDF Extractor → Structured Data
    ↓
Comparator → Find Discrepancies
    ↓
Report Generator → Multiple Formats
    ↓
RAG System (ChromaDB) → Semantic Search
    ↓
LangChain Agent → Intelligent Analysis
    ↓
Chatbot → Natural Language Interface
```

## 🔑 Key Features

### PDF Extraction
- Automatically parses Purchase Orders and Invoices
- Extracts items, quantities, prices, totals
- Handles multiple document types

### Smart Comparison
- Identifies 5 types of discrepancies
- Calculates variance percentages
- Rates severity (Critical, High, Medium)

### Multi-Format Reports
- JSON for developers
- CSV for Excel/Spreadsheets
- Excel with formatted sheets
- HTML for web viewing

### RAG (Retrieval-Augmented Generation)
- Semantic search across documents
- Uses BGE embeddings (high quality)
- RAG Fusion for better results
- Persistent ChromaDB storage

### Intelligent Chatbot
- Multi-turn conversations
- Context-aware responses
- Grounded in actual document data
- Specific methods for common tasks

## 🛠️ Troubleshooting

### "ImportError: No module named..."
```bash
pip install -r requirements.txt
```

### "OPENAI_API_KEY not found"
1. Check .env file exists
2. Your key should look like: `sk-xxxxxxx...`
3. Make sure it's not expired

### "PDFs not found"
1. Place PDFs in the `data/` folder
2. File names should end with `.pdf`
3. PDFs should be text-based, not scanned images

### "First run is slow"
This is normal! First run downloads the embedding model (~200MB). Subsequent runs are much faster.

### "Getting rate limited"
If using OpenAI:
- Wait a bit before retrying
- Use cheaper model: gpt-3.5-turbo
- Check your rate limits: https://platform.openai.com/account/rate-limits

## 📚 Documentation

- **QUICKSTART.md** - More detailed quick start
- **README.md** - Complete documentation
- **PROJECT_SUMMARY.md** - Technical overview
- **examples.py** - Code examples
- **src/*.py** - Source code with docstrings

## 🔄 Typical Workflow

```
1. Place PDFs in data/ folder
2. Run: python setup.py (first time only)
3. Run: python main.py --mode pipeline
4. Answer questions about your documents
5. Check reports/ folder for generated reports
```

## 💡 Pro Tips

### Add More PDFs
Simply drop more PDFs in the `data/` folder and run again.

### Export to Spreadsheet
Open `reports/comparison_report.xlsx` in Excel, Google Sheets, or LibreOffice.

### Integrate with Code
```python
from src.orchestrator import PDFAnalysisOrchestrator

orch = PDFAnalysisOrchestrator()
orch.run_complete_pipeline()
result = orch.chat("Your question here")
```

### Use Different LLM
Edit `src/config.py`:
```python
LLM_MODEL = "gpt-3.5-turbo"  # Faster, cheaper
LLM_MODEL = "gpt-4"          # More powerful
```

## 🎓 Learning Path

1. **Start**: Run `python main.py --mode pipeline`
2. **Explore**: Check files in `reports/`
3. **Read**: Review `README.md`
4. **Experiment**: Modify code in `src/`
5. **Extend**: Add custom tools/features

## ❓ FAQ

**Q: Do I need a GPU?**
A: No! System works on CPU. GPU optional for speed.

**Q: How much does it cost?**
A: OpenAI charges ~$0.01-0.03 per query. Check their pricing.

**Q: Can it handle large PDFs?**
A: Yes! Scales to 100+ page documents.

**Q: Can it work offline?**
A: Embeddings need internet first time. After that, mostly offline.

**Q: What file formats does it support?**
A: Currently PDF. Text-based PDFs only (no scanned images).

**Q: Can I use different LLMs?**
A: Yes! Modify `src/config.py` or use alternatives like Groq.

## 🆘 Need Help?

1. **Check QUICKSTART.md** for common issues
2. **Read README.md** for detailed docs
3. **Run examples.py** to see it in action
4. **Check .env** configuration
5. **Verify PDFs** are in data/ folder

## 🎉 You're Ready!

```bash
cd pdf_rag_analysis
python setup.py
# Edit .env with your API key
python main.py --mode pipeline
```

That's it! You're now running a production-grade PDF analysis system with RAG and chatbot.

---

## What's Next?

After getting comfortable:
1. Explore the `src/` folder to understand components
2. Read full documentation in `README.md`
3. Check `PROJECT_SUMMARY.md` for architecture
4. Modify `src/config.py` for custom settings
5. Add custom tools to the agent
6. Deploy to production

---

**Happy analyzing!** 🚀
