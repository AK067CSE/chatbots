# Fine-Tuning Setup & Integration Guide

## Project Status

### Completed ✓
- [x] Training data generation (JSONL format)
  - `data/training_data.jsonl` - 68 training examples
  - `data/training_splits/` - Split by query type
- [x] Fine-tuning script created
  - `scripts/finetune_gemma.py` - Full fine-tuning pipeline
- [x] Gemma SQL Agent created
  - `src/agents/gemma_sql_agent.py` - Fine-tuned model inference
- [x] Multi-agent integration
  - Updated `langgraph_multi_agent.py` with Gemma support
  - Falls back to templates if fine-tuned model unavailable

## Running Fine-Tuning

### Step 1: Install Fine-tuning Dependencies
```bash
pip install torch transformers accelerate peft
```

### Step 2: Run Fine-Tuning
```bash
python scripts/finetune_gemma.py
```

**Note:** This requires:
- ~6GB VRAM for GPU fine-tuning
- ~20-30 minutes on NVIDIA GPU
- Or use CPU mode (slower, ~2-3 hours)

### Step 3: Model Output
Fine-tuning will create:
- `models/gemma-2b-text2sql/` - LoRA weights
- `models/gemma-2b-text2sql-merged/` - Merged model (ready for inference)

## Architecture Integration

### System Flow

```
User Query
    ↓
[Intent Classifier] → Intent type
    ↓
[Entity Extractor] → Metrics, filters, dimensions
    ↓
[RAG Retriever] (optional) → Context from KB
    ↓
[SQL Generator]
    ├→ Try Gemma-2B (if loaded)
    └→ Fallback to templates
    ↓
[SQL Executor] → Query results
    ↓
[Chart Generator] → Visualization
    ↓
Results → User
```

### SQL Generation Strategy

1. **If Gemma model is loaded:**
   - Use fine-tuned model for generation
   - More flexible natural language understanding
   - Better handling of complex queries

2. **If Gemma model not available:**
   - Fall back to SQL templates
   - Deterministic, reliable generation
   - Fast execution

## Testing Integration

### Quick Test
```bash
python -c "
from src.agents.gemma_sql_agent import GemmaSQLAgent
agent = GemmaSQLAgent()
if agent.is_loaded():
    print('[OK] Gemma model loaded successfully')
else:
    print('[INFO] Gemma model not found - using templates')
"
```

### Full Integration Test
```bash
python -m pytest tests/test_gemma_finetuning.py -v
```

### Manual Test
```bash
from src.agents.langgraph_multi_agent import MultiAgentOrchestrator

orchestrator = MultiAgentOrchestrator()
query = "Total sales in 2024?"
state = orchestrator.process(query, use_rag=True)

print(f"Query: {state.user_query}")
print(f"Intent: {state.intent}")
print(f"SQL: {state.sql}")
print(f"Results:\n{state.results_df}")
print(f"Model Used: {state.sql_model if hasattr(state, 'sql_model') else 'template'}")
```

## File Structure

```
salesbot/
├── data/
│   ├── training_data.jsonl          # 68 training examples
│   └── training_splits/              # Split by query type
├── models/
│   ├── gemma-2b-text2sql/           # LoRA weights (after fine-tuning)
│   └── gemma-2b-text2sql-merged/    # Merged model (production-ready)
├── scripts/
│   ├── generate_training_data.py     # Generate JSONL
│   └── finetune_gemma.py             # Fine-tuning script
└── src/
    └── agents/
        ├── gemma_sql_agent.py        # Gemma inference
        └── langgraph_multi_agent.py   # Multi-agent orchestrator
```

## Performance Notes

- **Template-based SQL**: ~50ms per query
- **Gemma-based SQL**: ~200-500ms per query (GPU), ~2-5s (CPU)
- **RAG retrieval**: ~100-200ms
- **SQL execution**: Depends on database complexity

## Troubleshooting

### Gemma Model Not Loading
- Check if model files exist in `models/gemma-2b-text2sql-merged/`
- Ensure sufficient VRAM or use CPU mode
- Check CUDA availability: `python -c "import torch; print(torch.cuda.is_available())"`

### Fine-Tuning Out of Memory
- Reduce `batch_size` in `finetune_gemma.py` (try 2 or 1)
- Use quantized model variant
- Enable gradient accumulation

### Template Fallback
- Gemma model not available? System automatically uses SQL templates
- All queries will still work, just with template-based generation
- No action needed - seamless fallback

## Next Steps

1. Run fine-tuning: `python scripts/finetune_gemma.py`
2. Verify integration: Check `models/gemma-2b-text2sql-merged/` exists
3. Test system: Run test suite or manual queries
4. Deploy: System automatically uses Gemma if available

## Resources

- [Gemma Model Card](https://huggingface.co/google/gemma-2b)
- [LoRA Fine-tuning](https://huggingface.co/docs/peft/conceptual_guides/lora)
- [Transformers Trainer](https://huggingface.co/docs/transformers/training)
