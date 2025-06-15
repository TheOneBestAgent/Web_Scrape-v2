# 🧠 Autonomous AI Web Scraper Framework

## Overview

This project is an intelligent, domain-adaptive, self-healing web scraper built with Playwright and Python. It leverages AI-powered heuristics, selector memory, and structured per-domain configurations to extract complex data (e.g., auction lots, dynamic listings) from static or JavaScript-heavy websites without human intervention.

Designed to operate as a modular service or scheduled job, it automatically learns from failures, logs its own behavior, and improves selector strategies over time. It is capable of crawling, parsing, and interpreting websites similarly to a human analyst.

---

## 🧩 Features

### ✅ Core Extraction
- Full HTML parsing via Selectolax
- JavaScript-rendered content via Playwright
- Extraction of:
  - Title, meta tags, paragraphs, headings
  - Links, images, navigation (breadcrumbs, menus)
  - JSON-LD, RDFa, Microdata via `extruct`
  - Pagination (next/prev, total pages)
  - Dynamic content (e.g. infinite scroll)

### 🛠️ Auction Intelligence
- Recognizes and extracts:
  - Lot/item blocks
  - Bid price
  - Time remaining
  - Images and detail URLs
- Custom selectors per domain
- Optional direct API parsing (JSON endpoint detection)

### 🤖 AI & Heuristics
- Self-healing selector system
  - Fallback to alternates from config
  - Retry up to 5 selectors per block
  - Logs successes and failures
- Per-domain memory (`config/sites/{domain}.yaml`)
  - Controls dynamic behavior, selectors, toggles
- Heuristic logger (`logs/heuristics/*.json`)
  - Duration, scrolls, selector hits, endpoint patterns
- Optional OpenAI integration (`ai_assist.py`)
  - Summarization, failure explanation, self-improving patch generation

### 🧠 Config & Memory
- YAML config per domain
- Auto-syncs to SQLite for dashboarding or bulk analysis
- Dynamic config builder planned

---

## 🗃️ File Structure

```bash
.
├── config/
│   └── sites/
│       └── example.com.yaml
├── data/
│   └── extracted/
├── docs/
│   └── spec.md
├── logs/
│   └── heuristics/
├── schemas/
│   └── auction.json
├── scraper/
│   ├── core.py
│   ├── extractor.py
│   ├── selector_repair.py
│   ├── selector_logger.py
│   ├── config_manager.py
│   ├── config_sync.py
│   ├── heuristics_logger.py
│   └── ai_assist.py
├── launch.py
├── .env
├── requirements.txt
└── README.md
```

---

## 🚀 How It Works

1. **Launch**: Run `launch.py` with a target URL.
2. **Load Config**: Domain-specific YAML is loaded or created.
3. **Page Load**: Playwright renders the page if `enable_dynamic` is set.
4. **Extraction**: `extractor.py` parses the DOM.
5. **Self-Healing**: If selectors fail, `selector_repair.py` retries others.
6. **Log & Learn**: Successful selectors are logged; heuristics are stored.
7. **Sync**: Config is pushed to SQLite or other persistence layer.

---

## ⚙️ Configuration Example (config/sites/example.com.yaml)
```yaml
enable_dynamic: true
enable_navigation: true
enable_auction: true

custom_selectors:
  auction_items:
    - ".lot-item"
    - ".custom-lot"
    - "[data-lot-id]"
  pagination:
    - ".pager"
    - "nav.pagination"
```

---

## 🧪 Testing & Debugging

- Logs available in `logs/heuristics/`
- Errors are caught and printed with domain context
- Uses defensive try/except for all selector actions
- Print debug can be toggled or extended to structured logger

---

## 📅 Future Enhancements

- Selector scoring model
- Link crawler planner (recursive + queueing)
- Web dashboard for real-time monitoring
- Autonomous sitemap builder
- Embedding AI patch cycles for dynamic failure recovery

---

## 🧠 Codex Handoff Summary
This repo contains everything needed to:
- Scrape dynamic/static websites
- Adapt across domains
- Retry intelligently when selectors fail
- Store what worked for the next scrape
- Extract auction/marketplace data
- Learn and improve over time

Feed this to Codex or any code generator to rehydrate full modules based on structure and behavior.

---

## 🔐 Environment

Your `.env` should include:
```bash
OPENAI_API_KEY=sk-...
DATABASE_URL=sqlite:///scraper.db
```

---

## 👤 Author
Built for automated domain-intelligent scraping. Maintained by Dariusalexander Jacobs.
