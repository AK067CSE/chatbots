# Quick Start: Fine-Tuning Gemma-2B for Text-to-SQL

## In 5 Minutes

### 1. Install Dependencies
```bash
pip install -q torch transformers peft trl bitsandbytes datasets \
    langchain langchain-community langchain-huggingface chromadb \
    sentence-transformers duckdb pandas plotly scikit-learn
```

### 2. Prepare Training Data
```bash
cd scripts
python generate_training_data.py
cd ..
```
This creates:
- `data/training_data.jsonl` (combined dataset)
- `data/training_data_train.jsonl` (80% for training)
- `data/training_data_val.jsonl` (20% for validation)

### 3. Run Fine-Tuning Notebook
```bash
jupyter notebook notebooks/Gemma2B_FT_Text2SQL_RAG.ipynb
```

Execute cells in order:
1. **Section 1-4**: Setup & model loading
2. **Section 5-7**: LoRA config & training
3. **Section 8-12**: Model merging & evaluation

### 4. Test the Model
```bash
python -m pytest tests/test_gemma_finetuning.py -v
```

### 5. Use in Application
```python
from src.agents.langgraph_multi_agent import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator()
state = orchestrator.process("What were total sales in 2023?", use_rag=True)
print(state.sql)  # Generated SQL
print(state.results_df)  # Query results
```

---

## Important Configuration

### For CPU Training (Recommended)
```python
# Already configured in notebook Section 2
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)
```

### For GPU Training (Optional)
```python
# Set in notebook Section 6
training_args.bf16 = True
training_args.per_device_train_batch_size = 8  # Can be larger on GPU
```

### HuggingFace Token
```bash
huggingface-cli login
# Or export HF_TOKEN="your_token"
```

---

## Expected Outputs

After fine-tuning (Section 8):
```
models/
├── gemma-2b-text2sql-merged/    ← Use this for inference
│   └── ~5GB total
└── gemma-2b-text2sql-lora/      ← Efficient adapter version
    └── ~50MB total
```

---

## Test Queries

The notebook tests these query types:

| Query | Type | Expected SQL |
|-------|------|--------------|
| "Total sales 2023?" | Aggregation | SELECT SUM(amount) |
| "Sales 2023 vs 2024?" | Comparison | GROUP BY YEAR(date) |
| "Top 5 brands?" | Ranking | ORDER BY DESC LIMIT 5 |
| "Active stores?" | Counting | WHERE status='active' |

---

## Troubleshooting

### "CUDA out of memory"
→ Use CPU (default in notebook)

### "HuggingFace token not found"
```bash
huggingface-cli login
```

### "Model file not found"
```bash
# Download base Gemma model first
from transformers import AutoModel
AutoModel.from_pretrained("google/gemma-2b-it")
```

### "Training is too slow"
- Already optimized for CPU (4-bit quantization)
- Use GPU if available: `cuda` in `device_map`
- Reduce `max_steps` in Section 6

### "Generated SQL is invalid"
- Check RAG context is being used (Section 9)
- Verify training data format (Section 4)
- Reduce `temperature` in Section 11

---

## Performance Benchmarks

| Operation | CPU | GPU |
|-----------|-----|-----|
| Model loading | 5-10s | 2-3s |
| Training (500 steps) | 2-4h | 30 min |
| Inference (per query) | 2-5s | 0.3-0.5s |
| Batch inference (10 queries) | 20-50s | 3-5s |

---

## Next Steps

1. **✅ Run fine-tuning** (2-4 hours on CPU)
2. **✅ Test model** with test suite
3. **✅ Integrate with Streamlit** app (see section in GEMMA_FINE_TUNING_GUIDE.md)
4. **✅ Deploy to production** (HuggingFace Hub or your server)

---

## Key Files

| File | Purpose |
|------|---------|
| `notebooks/Gemma2B_FT_Text2SQL_RAG.ipynb` | Main fine-tuning notebook (12 sections) |
| `scripts/generate_training_data.py` | Generate JSONL training data |
| `src/agents/langgraph_multi_agent.py` | Multi-agent orchestrator |
| `src/rag/enhanced_rag_builder.py` | RAG vector store |
| `tests/test_gemma_finetuning.py` | Comprehensive test suite |
| `GEMMA_FINE_TUNING_GUIDE.md` | Detailed documentation |

---

## One-Liner Commands

```bash
# Setup & test everything
pip install -q bitsandbytes peft trl langchain chromadb && \
cd scripts && python generate_training_data.py && cd .. && \
python -m pytest tests/test_gemma_finetuning.py -v

# Run only specific test
python -m pytest tests/test_gemma_finetuning.py::TestMultiAgentOrchestrator -v

# Check if model is loaded
python -c "from transformers import AutoModel; AutoModel.from_pretrained('google/gemma-2b-it')"
```

---

## Success Indicators

✅ Fine-tuning notebook runs without errors
✅ Training loss decreases over epochs
✅ Model saves to `models/gemma-2b-text2sql-merged/`
✅ Test suite shows > 90% pass rate
✅ Inference generates valid SQL
✅ RAG retrieval returns relevant context
✅ Multi-agent orchestrator processes queries end-to-end

---

**Estimated Total Time**: 3-5 hours (setup + training on CPU)

**Support**: See GEMMA_FINE_TUNING_GUIDE.md for detailed troubleshooting
