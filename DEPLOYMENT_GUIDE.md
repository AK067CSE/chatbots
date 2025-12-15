# Deployment & Integration Guide - Fine-Tuned Gemma-2B System

## Overview

This guide covers deploying the fine-tuned Gemma-2B system in production environments and integrating it with existing applications.

---

## Part 1: Integration with Existing Streamlit App

### Step 1: Update SQL Agent

**File**: `src/agents/sql_agent.py`

Add fine-tuned model support to existing `SQLAgent` class:

```python
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class SQLAgent:
    def __init__(self):
        # ... existing init code ...
        self.ft_model = None
        self.ft_tokenizer = None
        self.use_finetuned = False
    
    def load_finetuned_model(self):
        """Load fine-tuned Gemma-2B model"""
        model_path = Path("models/gemma-2b-text2sql-merged")
        
        if not model_path.exists():
            print(f"⚠️ Fine-tuned model not found at {model_path}")
            print("Using template-based approach only")
            return False
        
        try:
            self.ft_model = AutoModelForCausalLM.from_pretrained(
                str(model_path),
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                quantization_config=BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                ) if torch.cuda.is_available() else None
            )
            
            self.ft_tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            self.ft_tokenizer.pad_token = self.ft_tokenizer.eos_token
            self.use_finetuned = True
            print("✓ Fine-tuned model loaded successfully")
            return True
        except Exception as e:
            print(f"⚠️ Failed to load fine-tuned model: {e}")
            return False
    
    def _generate_sql_finetuned(self, query: str, rag_context: str = None) -> str:
        """Generate SQL using fine-tuned Gemma-2B"""
        
        if self.ft_model is None:
            return None
        
        # Build prompt with RAG context
        if rag_context:
            prompt = f"""<start_of_turn>user
{rag_context}

Generate SQL for: {query}
<end_of_turn>
<start_of_turn>model
"""
        else:
            prompt = f"""<start_of_turn>user
Convert to SQL for sales analytics database:
{query}
<end_of_turn>
<start_of_turn>model
"""
        
        # Generate
        inputs = self.ft_tokenizer(prompt, return_tensors="pt").to(self.ft_model.device)
        
        with torch.no_grad():
            outputs = self.ft_model.generate(
                **inputs,
                max_length=512,
                temperature=0.1,
                top_p=0.95,
                do_sample=False,
            )
        
        response = self.ft_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract SQL
        if "<start_of_turn>model" in response:
            sql = response.split("<start_of_turn>model")[-1].strip()
            if "<end_of_turn>" in sql:
                sql = sql.split("<end_of_turn>")[0].strip()
        else:
            sql = response
        
        return sql
    
    def answer(self, query: str, model_type: str = "ensemble") -> tuple:
        """
        Answer query using specified model
        
        Args:
            query: User natural language query
            model_type: "template", "finetuned", or "ensemble"
            
        Returns:
            (sql, dataframe, metadata)
        """
        
        if model_type == "finetuned" and self.use_finetuned:
            # Use fine-tuned model with RAG
            from src.rag.enhanced_rag_builder import RAGQueryEnhancer
            enhancer = RAGQueryEnhancer()
            context = enhancer.get_context(query)
            
            sql = self._generate_sql_finetuned(query, context["full_context"])
            
            if sql:
                try:
                    df = self.db.query(sql)
                    return sql, df, {"model": "gemma-2b-finetuned", "rag": True}
                except Exception as e:
                    print(f"⚠️ Fine-tuned SQL failed: {e}")
                    # Fall back to template-based
                    sql, df, meta = self.answer(query, "template")
                    meta["model"] = "gemma-2b-finetuned-fallback"
                    return sql, df, meta
        
        elif model_type == "ensemble":
            # Try fine-tuned first, fallback to template
            if self.use_finetuned:
                try:
                    return self.answer(query, "finetuned")
                except:
                    pass
            
            # Fall back to template
            return self.answer(query, "template")
        
        # Default: template-based
        # ... existing code ...
        return self._answer_template_based(query)
```

### Step 2: Update Streamlit UI

**File**: `src/ui/streamlit_app.py`

Add model selection UI:

```python
import streamlit as st
from src.agents.sql_agent import SQLAgent

# Initialize agent
agent = SQLAgent()

# Load fine-tuned model at startup
@st.cache_resource
def load_agent():
    agent = SQLAgent()
    agent.load_finetuned_model()
    return agent

agent = load_agent()

# Add sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Model selection
model_choice = st.sidebar.radio(
    "Select Model",
    ["Template-Based", "Fine-Tuned (Recommended)", "Ensemble"]
)

model_map = {
    "Template-Based": "template",
    "Fine-Tuned (Recommended)": "finetuned",
    "Ensemble": "ensemble",
}

# RAG toggle
use_rag = st.sidebar.checkbox("Use RAG Enhancement", value=True)

# Main query interface
st.header("🤖 Sales Data Analyzer")

query = st.text_input("Ask a question about sales:", placeholder="e.g., What were total sales in 2023?")

if st.button("Analyze", type="primary"):
    with st.spinner(f"Processing with {model_choice}..."):
        try:
            sql, df, meta = agent.answer(query, model_map[model_choice])
            
            # Display results
            st.success(f"✓ Query processed using {meta['model']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Generated SQL")
                st.code(sql, language="sql")
            
            with col2:
                st.subheader("Query Results")
                st.dataframe(df, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
```

### Step 3: Test Integration

```bash
streamlit run src/ui/streamlit_app.py
```

Test with both model types:
1. Template-based (should be fast, ~100ms)
2. Fine-tuned (should be 2-5 seconds on CPU)
3. Ensemble (fallback strategy)

---

## Part 2: Docker Deployment

### Create Dockerfile

**File**: `Dockerfile`

```dockerfile
FROM pytorch/pytorch:2.1.0-runtime-cuda12.1-devel

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -q -r requirements.txt

# Copy application
COPY . .

# Download model at build time (optional, can be runtime)
RUN python -c "from transformers import AutoModel; AutoModel.from_pretrained('google/gemma-2b-it')"

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "src/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build & Run Docker Container

```bash
# Build image
docker build -t gemma-text2sql:latest .

# Run container
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  --gpus all \
  gemma-text2sql:latest

# Run on CPU only
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  gemma-text2sql:latest
```

### Docker Compose Setup

**File**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  gemma-text2sql:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - HF_TOKEN=${HF_TOKEN}
      - CUDA_VISIBLE_DEVICES=0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Model serving with vLLM for faster inference
  vllm-server:
    image: vllm/vllm-openai:latest
    ports:
      - "8000:8000"
    volumes:
      - ./models:/models
    command: --model /models/gemma-2b-text2sql-merged --tensor-parallel-size 1
    environment:
      - HF_TOKEN=${HF_TOKEN}
```

Run:
```bash
docker-compose up -d
```

---

## Part 3: Production Deployment

### Option 1: AWS Deployment with SageMaker

```python
# Deploy fine-tuned model to SageMaker
import boto3
from sagemaker.huggingface.model import HuggingFaceModel

# Create SageMaker role and execution role
role = "arn:aws:iam::ACCOUNT:role/sagemaker-role"

# Create HuggingFace model
huggingface_model = HuggingFaceModel(
    model_data="s3://your-bucket/gemma-2b-text2sql-merged",
    role=role,
    transformers_version="4.26",
    pytorch_version="2.0",
    py_version="py39",
)

# Deploy to SageMaker endpoint
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type="ml.g4dn.xlarge",  # GPU instance
    endpoint_name="gemma-text2sql"
)
```

### Option 2: Azure Deployment

```python
# Deploy to Azure Container Instances
from azure.containerregistry import ContainerRegistryClient
from azure.identity import DefaultAzureCredential

# Push image to ACR
credential = DefaultAzureCredential()
registry_client = ContainerRegistryClient(
    registry_url="your-registry.azurecr.io",
    credential=credential
)

# Deploy with Azure Container Instances
import subprocess
subprocess.run([
    "az", "container", "create",
    "--resource-group", "your-rg",
    "--name", "gemma-text2sql",
    "--image", "your-registry.azurecr.io/gemma-text2sql:latest",
    "--ports", "8501",
    "--environment-variables", f"HF_TOKEN={hf_token}"
])
```

### Option 3: Google Cloud Deployment

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/gemma-text2sql

# Deploy to Cloud Run
gcloud run deploy gemma-text2sql \
  --image gcr.io/PROJECT_ID/gemma-text2sql \
  --platform managed \
  --region us-central1 \
  --memory 8Gi \
  --cpu 4 \
  --gpu \
  --set-env-vars HF_TOKEN=your_token
```

---

## Part 4: FastAPI Deployment

### Create API Service

**File**: `api/main.py`

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import asyncio
from src.agents.langgraph_multi_agent import MultiAgentOrchestrator
from src.rag.enhanced_rag_builder import RAGQueryEnhancer

app = FastAPI(
    title="Gemma Text-to-SQL API",
    version="1.0.0",
    description="Fine-tuned Gemma-2B for sales data queries"
)

# Initialize at startup
orchestrator = None
rag_enhancer = None

@app.on_event("startup")
async def startup_event():
    global orchestrator, rag_enhancer
    orchestrator = MultiAgentOrchestrator()
    rag_enhancer = RAGQueryEnhancer()
    print("✓ Model loaded and ready")

class QueryRequest(BaseModel):
    query: str
    use_rag: bool = True
    model_type: str = "ensemble"  # "template", "finetuned", "ensemble"

class QueryResponse(BaseModel):
    query: str
    sql: str
    result_count: int
    results: list
    chart_data: Optional[dict]
    execution_time: float
    model_used: str

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process natural language query and return results
    
    Args:
        query: Natural language question
        use_rag: Whether to use RAG enhancement
        model_type: Which model to use
        
    Returns:
        QueryResponse with SQL, results, and chart
    """
    import time
    start_time = time.time()
    
    try:
        # Process query through orchestrator
        state = orchestrator.process(request.query, use_rag=request.use_rag)
        
        # Prepare response
        results = state.results_df.to_dict(orient="records") if state.results_df is not None else []
        
        return QueryResponse(
            query=request.query,
            sql=state.sql or "No SQL generated",
            result_count=len(results),
            results=results,
            chart_data=state.chart_data,
            execution_time=time.time() - start_time,
            model_used=state.query_type.value if state.query_type else "unknown"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": orchestrator is not None}

@app.post("/batch-query")
async def batch_query(queries: list[str], background_tasks: BackgroundTasks):
    """
    Process multiple queries asynchronously
    
    Args:
        queries: List of queries to process
        
    Returns:
        List of results
    """
    results = []
    for query in queries:
        state = orchestrator.process(query)
        results.append({
            "query": query,
            "sql": state.sql,
            "status": "success" if not state.error else "failed"
        })
    
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run FastAPI server:
```bash
python api/main.py

# Or with Uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Part 5: Monitoring & Observability

### Add Logging

```python
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log queries and performance
def log_query(query: str, sql: str, execution_time: float, success: bool):
    logger.info(f"Query: {query[:100]}... | "
                f"SQL: {sql[:50]}... | "
                f"Time: {execution_time:.2f}s | "
                f"Success: {success}")
```

### Add Metrics Collection

```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
query_counter = Counter('sql_queries_total', 'Total queries processed')
query_duration = Histogram('sql_query_duration_seconds', 'Query execution time')
sql_errors = Counter('sql_errors_total', 'Total SQL errors')

@app.post("/query")
async def process_query(request: QueryRequest):
    query_counter.inc()
    
    with query_duration.time():
        try:
            state = orchestrator.process(request.query)
        except Exception as e:
            sql_errors.inc()
            raise

# Start metrics server
if __name__ == "__main__":
    start_http_server(8001)  # Prometheus metrics at :8001/metrics
```

---

## Part 6: Scaling & Optimization

### Model Quantization for Inference

```python
# Use 8-bit quantization for faster inference
from bitsandbytes.nn import Linear8bitLt

model = AutoModelForCausalLM.from_pretrained(
    "gemma-2b-text2sql-merged",
    quantization_config=BitsAndBytesConfig(
        load_in_8bit=True,  # Faster than 4-bit
    )
)
```

### Batch Processing Optimization

```python
def batch_generate_sql(queries: list[str], batch_size: int = 8):
    """Generate SQL for multiple queries efficiently"""
    results = []
    
    for i in range(0, len(queries), batch_size):
        batch = queries[i:i+batch_size]
        
        # Tokenize batch
        inputs = tokenizer(batch, return_tensors="pt", padding=True)
        
        # Generate for batch
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=512)
        
        # Decode
        for output in outputs:
            sql = tokenizer.decode(output, skip_special_tokens=True)
            results.append(sql)
    
    return results
```

### Caching Strategy

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_cached_sql(query_hash: str) -> Optional[str]:
    """Cache SQL results for identical queries"""
    return None

def cache_sql(query: str, sql: str):
    """Cache generated SQL"""
    query_hash = hashlib.md5(query.encode()).hexdigest()
    # Store in cache
    cache[query_hash] = sql
```

---

## Monitoring Checklist

✅ Model loading time
✅ Query processing latency (p50, p95, p99)
✅ SQL execution success rate
✅ RAG retrieval quality
✅ Error rates and types
✅ GPU/CPU utilization
✅ Memory usage
✅ Cache hit rates
✅ User satisfaction metrics

---

## Production Deployment Checklist

- [ ] Model tested thoroughly
- [ ] Fallback strategies in place
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Monitoring dashboard setup
- [ ] Scaling strategy defined
- [ ] Backup & recovery plan
- [ ] Security hardened (API keys, HTTPS)
- [ ] Load testing completed
- [ ] Documentation up-to-date

---

## Support

For deployment questions, refer to:
- `GEMMA_FINE_TUNING_GUIDE.md` - Technical details
- `QUICK_START_GEMMA.md` - Quick reference
- `IMPLEMENTATION_SUMMARY.md` - Architecture overview
