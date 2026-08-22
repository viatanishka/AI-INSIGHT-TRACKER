# 🔍 AI Insight Tracker

An autonomous AI agent that tracks research papers and news for a chosen topic, summarizes them, and displays them in a live dashboard — built for [Hackathon Name].

## Problem it solves

Organizations and researchers need to stay on top of fast-moving research and news, but manually checking arXiv, patent databases, and news sites every day is slow and things get missed. This project automates that: it pulls the latest items from research and news sources, summarizes each one with an LLM, and shows a clean, filterable digest — so staying updated takes seconds instead of hours.

## How it works

1. **Fetch** — pulls the newest papers from arXiv and news articles from an RSS feed for a chosen topic
2. **Summarize** — sends each item to Claude (Anthropic's LLM) to generate a short, relevance-focused summary
3. **Store** — saves everything to a local SQLite database so nothing is lost between sessions
4. **Display** — a Streamlit dashboard shows the digest, filterable by source, with one click to refresh

## Tech stack

- Python
- Streamlit (dashboard UI)
- Anthropic Claude API (summarization)
- arXiv API + RSS feeds (data sources)
- SQLite (storage)

## Setup

```bash
pip install -r requirements.txt
```



```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-key-here"

# Mac/Linux
export ANTHROPIC_API_KEY="your-key-here"
```

Run the app:

```bash
python -m streamlit run app.py
```

**No API key yet?** The app still runs fully — it uses placeholder `[MOCK SUMMARY]` text instead of calling the AI, so you can test the whole pipeline for free.

## Configuration

Edit these values near the top of `app.py` to point the tracker at your own topic:

```python
ARXIV_QUERY = "cat:cs.AI"
NEWS_RSS_URL = "https://news.google.com/rss/search?q=AI+agents"
```

## Roadmap

- Patent tracking (Google Patents integration)
- Social media / X (Twitter) monitoring
- Scheduled auto-refresh instead of manual button click
- Competitor-specific tracking profiles
