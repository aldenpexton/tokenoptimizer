
# 🎨 TokenOptimizer – UI/UX Design Guide

This document defines the core UI/UX principles, visual system, and layout expectations for the TokenOptimizer dashboard. It is intended for use by any frontend developers or AI agents (such as Cursor) to ensure visual consistency and brand alignment.

---

## ✨ Brand Vibe & Tone

- **Clean, modern, minimal**
- Inspired by tools like **Stripe Dashboard**, **Vercel**, and **Linear**
- Trustworthy, professional, and built for developers
- Focused on clarity, whitespace, and high-contrast readability

---

## 🎨 Color Palette

| Use | Color | Hex |
|-----|-------|-----|
| Primary Text / Heading | Dark Gray | `#1F2937` |
| Accent / Interactive | Indigo | `#6366F1` |
| Background | Light Gray | `#F9FAFB` |
| Card Background | White | `#FFFFFF` |
| Warning / Alert | Amber | `#FBBF24` |
| Success / Optimization | Green | `#10B981` |

**Typography:** Use system UI fonts or clean sans-serifs only.  
Examples: `Inter`, `Roboto`, `Helvetica Neue`, `system-ui`

---

## 🖼️ Layout Principles

- Use a **sidebar layout** with navigation on the left
- Header bar should show current date range or context
- Dashboard content should be **modular cards**, stacked vertically
- Use grid or flexbox layout for responsiveness

---

## 📊 Core Components to Implement

### 1. **Top Overview Card**
- **Total Token Usage** (toggle: tokens vs $)
- **This Month’s Cost** with breakdown
- **Primary Model Used**

### 2. **Line Chart: Token Usage Over Time**
- X-axis: Time (by day/week)
- Y-axis: Tokens used or $ spent
- Use light gridlines and smooth animation

### 3. **Pie or Bar Chart: Model Usage Distribution**
- % of tokens per model (e.g., GPT-4, Claude)
- Use accessible color palette

### 4. **Table: Feature Usage**
| Feature | Model | Total Tokens | Est. Cost | Latency |
|---------|-------|--------------|-----------|---------|
| summarizer | claude-3-haiku | 121,000 | $9.20 | 870ms |

### 5. **Logs View (Debug Tool)**
- Timestamp
- Model
- Tokens
- Cost
- Feature (endpoint_name)

---

## ✅ UI Do’s

- Keep whitespace generous
- Align all content to an 8px grid system
- Use hover and click effects sparingly
- Icons: optional, minimalist (Lucide, Tabler Icons)
- Charts: animate on load, support tooltips

---

## 🚫 UI Don’ts

- ❌ No dark mode yet
- ❌ No custom fonts
- ❌ No bloated charting libraries
- ❌ No overly vibrant colors
- ❌ No text shadows or gradients

---

## 📸 Visual References

Reference these live tools for styling:
- https://vercel.com/dashboard
- https://stripe.com/docs/dashboard
- https://linear.app

---

## 🧭 Cursor Agent Note

Follow this document closely for **layout, spacing, color, and hierarchy**. Prioritize **clarity** and **performance** over complexity. This UI must support **quick scanning**, especially for developers managing infrastructure and budgets.

