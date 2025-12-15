# Quick Commands Reference

## Run Streamlit UI (Web Chatbot)
```bash
.venv\Scripts\streamlit.exe run src/ui/streamlit_app.py
```
🌐 Open: http://localhost:8501

## Test All Agents
```bash
.venv\Scripts\python.exe tests/test_queries.py
```

## Install Dependencies
```bash
.venv\Scripts\pip.exe install -r requirements.txt
```

## List All Test Files
```bash
.venv\Scripts\python.exe tests/test_duckdb.py
.venv\Scripts\python.exe tests/test_loader.py
.venv\Scripts\python.exe tests/test_metrics.py
.venv\Scripts\python.exe tests/test_sql_agent.py
```

## Check Database Status
```bash
.venv\Scripts\python.exe -c "from src.db.duckdb_client import DuckDBClient; print(DuckDBClient().fetchdf('SELECT COUNT(*) as row_count FROM sales'))"
```

## Run a Single Query via Python
```bash
.venv\Scripts\python.exe -c "
from src.agents.sql_rag_router import SQLRAGRouter
router = SQLRAGRouter()
result = router.route('Total sales for Delmond in Jan 2024')
print('SQL:', result['sql'])
print('Result:', result['data'])
"
```

## Kill Streamlit Process (if stuck)
```bash
taskkill /F /IM streamlit.exe
```

## Restart Virtual Environment
```bash
.venv\Scripts\Activate.ps1
```

---

## Streamlit UI Features

| Action | How |
|--------|-----|
| Ask Question | Type in text box and press Enter |
| View SQL | Check the "Generated SQL" section |
| See Data | Scroll to the "Data" table |
| Check Chart | Look at the "Chart" visualization |
| Read Explanation | Check "Explanation" or "Business Analysis" |

---

## Test Query Examples

```bash
# Run this to test core functionality:
.venv\Scripts\python.exe tests/test_queries.py
```

Output includes:
- ✅ "Total sales for Delmond in Jan 2024" → $200,824.61
- ✅ "Compare Delmond sales 2024 vs 2025" → Year comparison
- ✅ "Total active stores for Delmond in Feb 2024" → 146 stores
- ✅ "Summarize sales by region" → Region breakdown

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| ModuleNotFoundError: 'src' | Run from project root directory |
| DuckDB not found | Install: `pip install duckdb` |
| OpenAI API error | Check .env has valid OPENAI_API_KEY |
| Streamlit won't start | Run: `taskkill /F /IM streamlit.exe` then restart |

---

**💡 Pro Tip:** Keep Streamlit running in one terminal and use another for running tests!
