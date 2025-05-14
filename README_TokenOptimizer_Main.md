
# 🧠 TokenOptimizer – Developer Engineering Overview

**TokenOptimizer** is an LLM observability tool that helps developers monitor token usage and optimize model spend. It works with any GenAI app using OpenAI, Anthropic, Mistral, or other API-accessible models.

---

## 🔍 What It Does

- Tracks LLM API calls from your app
- Logs token usage, latency, and model used
- Calculates estimated cost based on latest pricing data
- Displays this usage in a clean, live web dashboard
- (Future) Suggests cheaper model alternatives based on real usage patterns

---

## 🛠️ How It Works (MVP)

### 1. 🧩 Python SDK

Drop-in wrapper around your LLM API calls:

```python
from tokenoptimizer import tracked_completion

response = tracked_completion(
    model="claude-3-haiku",
    messages=[{"role": "user", "content": "Summarize this PDF"}],
    endpoint_name="default"  # Optional task tag
)
```

**Key behavior:**
- Measures latency
- Extracts `model`, `prompt_tokens`, `completion_tokens`, `total_tokens`
- Calculates estimated request cost using model pricing table
- Sends anonymized metadata to TokenOptimizer backend (`POST /log`)
- Does **not** store prompt contents
- Adds **no latency** or logic impact to your app

#### ✳️ Tagging (Important)

- `endpoint_name` helps group usage by feature (e.g., `"summarization"`, `"chatbot"`)
- If not provided, we tag usage as `"default"`
- In the dashboard, usage will be broken down by these tags

---

### 2. 🌐 Dashboard (React + Supabase)

Accessible at:

`https://dashboard.tokenoptimizer.com` *(coming soon)*

**MVP Features:**
- Total token usage over time (line graph)
- Cost breakdown by model and feature
- Pie chart for model distribution
- Table view for usage by `endpoint_name`
- Latency tracking per model
- Logs view (timestamp, model, latency, tokens, cost)

---

### 3. 💰 Model Pricing Integration

We use an internal `model_pricing` table in Supabase:

```sql
CREATE TABLE model_pricing (
  model TEXT PRIMARY KEY,
  input_price NUMERIC,
  output_price NUMERIC,
  last_updated TIMESTAMP
);
```

This is queried during ingestion to compute:
- `input_cost = prompt_tokens / 1000 * input_price`
- `output_cost = completion_tokens / 1000 * output_price`
- `total_cost = input_cost + output_cost`

**This approach allows us to update pricing without hardcoding.**

---

## 🧰 Tech Stack

| Component | Tech |
|----------|------|
| Frontend Dashboard | React (Vercel) |
| Backend API | Flask (Render) |
| Database | Supabase (Postgres) |
| SDK | Python module (importable or pip-install) |

---

## 🛡️ Privacy & Performance Principles

- ❌ No prompt content is stored
- ✅ No PII is logged by default
- ✅ No impact on application logic
- ✅ No added latency
- ✅ Secure transmission with HTTPS
- ✅ Minimal dev effort to integrate

---

## 🚀 Near-Term Roadmap

- ✅ SDK to log token usage
- ✅ Flask API to ingest and store logs
- ✅ React dashboard to visualize token usage
- ✅ Cost mapping with live pricing DB
- 🔜 Feature grouping (task suggestions, UI labels)
- 🔜 Benchmark runner for silent model comparisons

---

## 📦 Install (Coming)

```bash
pip install tokenoptimizer
```

---

## 📁 Project Layout

```
/backend      → Flask API + Supabase integration
/frontend     → React dashboard UI
/sdk          → Python module to track LLM usage
```

---

## 🧠 Summary

**TokenOptimizer** is your "LLM spend dashboard" — built for devs, with zero risk, and maximum insight.
