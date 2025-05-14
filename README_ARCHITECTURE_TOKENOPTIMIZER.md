
# 📐 TokenOptimizer – Project Architecture & Coding Standards

This document outlines the architecture principles, naming conventions, and development rules that **must be followed** throughout the TokenOptimizer project. It serves as a "project constitution" to ensure consistency, clarity, and maintainability as we build.

---

## 🧱 Folder & Code Structure

### ✅ General Guidelines
- All code must be **modular and well-separated**
- Avoid monolithic files (e.g., `app.py` should only handle app instantiation and routing)
- Use **folders** to organize by function (e.g., `/routes`, `/utils`, `/services`, `/db`)
- Follow an **8/20 rule**: no single file should exceed 80 lines if it can be cleanly split

---

## 🗂️ File Naming Conventions

| Purpose | Example |
|---------|---------|
| Route handlers | `log_routes.py` |
| DB operations | `db_client.py`, `supabase_connector.py` |
| Cost calculation | `pricing_engine.py` |
| Helpers/utilities | `format_tokens.py`, `validate_payload.py` |

---

## ⚙️ Config & Environment

- Use `.env` files for **ALL** config (Supabase keys, API base URLs)
- Never hardcode URLs or secrets
- Make use of `dotenv` or similar packages in Python and React

---

## 📊 Database Integrity Rules

- Always refer to database schema definitions explicitly
- Never assume column names — confirm from source (e.g., README, schema.sql, or Supabase browser)
- If a new field is added to a table, update the shared schema documentation

---

## ✅ Data Flow Overview

```
[Developer SDK] → 
[Flask API (`/log`)] → 
[Supabase DB (`token_logs` + `model_pricing`)] → 
[Dashboard (React)] → 
[Insights UI]
```

---

## 🔧 Backend Rules (Python/Flask)

- Use `Blueprints` to organize routes by module
- Use `services/` for computation (e.g., cost calculation)
- Use `db/` or `models/` folder for Supabase interaction logic
- All request validation must happen before any inserts or updates

---

## 🧩 Frontend Rules (React)

- Use `pages/` for high-level views
- Use `components/` for reusable UI blocks
- Styling should follow the Tailwind utility-first approach (if enabled)
- Don’t use inline styles or unapproved design libraries

---

## ❗Cursor & Collaborator Checklist (Always Follow)

- [ ] Did you organize code into clearly named folders?
- [ ] Did you avoid putting everything in one file?
- [ ] Are you using `.env` for all configs?
- [ ] Did you refer to the actual DB schema, not make assumptions?
- [ ] Are files named clearly based on purpose?
- [ ] Did you add new fields/modules in the proper place?

---

## 🤝 Contribution Mindset

Every line of code is part of a long-term, production-grade product. Prioritize:
- Maintainability
- Clear logic flow
- Reusability
- Avoiding surprises

---

This document is a mandatory guide for all development in TokenOptimizer. Cursor and collaborators must refer to this **before writing code** or generating file structures.

