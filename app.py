"""
AI Insight Tracker — Streamlit Skeleton
----------------------------------------
Pulls recent items from arXiv + an RSS news feed, summarizes them with an LLM,
stores results in SQLite, and displays a daily digest dashboard.

Run:
    pip install -r requirements.txt
    streamlit run app.py
"""

import os
import re
import sqlite3
import feedparser
import requests
import streamlit as st
from datetime import datetime


def strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()

# ---------- CONFIG ----------
DB_PATH = "insights.db"
ARXIV_QUERY = "cat:cs.AI"          # change to your chosen niche
NEWS_RSS_URL = "https://news.google.com/rss/search?q=AI+agents"  # swap in your topic
MAX_ITEMS_PER_SOURCE = 5

# No API key yet? The app still runs fully using a placeholder summary,
# so you can test everything and add the real key later before your demo.
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
USE_MOCK = not API_KEY

if not USE_MOCK:
    from anthropic import Anthropic
    client = Anthropic()  # expects ANTHROPIC_API_KEY in env


# ---------- STORAGE ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            link TEXT,
            summary TEXT,
            fetched_at TEXT
        )
    """)
    conn.commit()
    return conn


def save_item(conn, source, title, link, summary):
    conn.execute(
        "INSERT INTO insights (source, title, link, summary, fetched_at) VALUES (?, ?, ?, ?, ?)",
        (source, title, link, summary, datetime.utcnow().isoformat()),
    )
    conn.commit()


def get_all_items(conn):
    return conn.execute(
        "SELECT source, title, link, summary, fetched_at FROM insights ORDER BY id DESC"
    ).fetchall()


# ---------- SOURCE FETCHERS ----------
def fetch_arxiv(query=ARXIV_QUERY, max_results=MAX_ITEMS_PER_SOURCE):
    url = f"http://export.arxiv.org/api/query?search_query={query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    feed = feedparser.parse(requests.get(url, timeout=10).text)
    return [{"title": e.title, "link": e.link, "raw": e.summary} for e in feed.entries]


def fetch_news(url=NEWS_RSS_URL, max_results=MAX_ITEMS_PER_SOURCE):
    feed = feedparser.parse(url)
    return [{"title": e.title, "link": e.link, "raw": strip_html(getattr(e, "summary", e.title))} for e in feed.entries[:max_results]]


# ---------- LLM SUMMARIZER ----------
def summarize(text, title):
    if USE_MOCK:
        # Placeholder so the app runs end-to-end with no API cost.
        # Swap in a real ANTHROPIC_API_KEY to get real AI summaries.
        snippet = text.strip().replace("\n", " ")[:180]
        return f"[MOCK SUMMARY] {snippet}..."

    prompt = f"""Summarize this in 2 sentences for a competitive-intel digest.
Focus on what's new/notable and why it might matter.

Title: {title}
Content: {text[:1500]}"""
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


# ---------- PIPELINE ----------
def run_pipeline(conn):
    with st.spinner("Fetching arXiv..."):
        for item in fetch_arxiv():
            summary = summarize(item["raw"], item["title"])
            save_item(conn, "arXiv", item["title"], item["link"], summary)

    with st.spinner("Fetching news..."):
        for item in fetch_news():
            summary = summarize(item["raw"], item["title"])
            save_item(conn, "News", item["title"], item["link"], summary)


# ---------- UI ----------
st.set_page_config(page_title="AI Insight Tracker", layout="wide")
st.title("🔍 AI Insight Tracker")
st.caption("Autonomous digest of research + news for your niche")

if USE_MOCK:
    st.warning("Running in MOCK mode (no ANTHROPIC_API_KEY set) — summaries are placeholders, not real AI output. Set the key before your final demo.")

conn = init_db()

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔄 Run tracker now"):
        run_pipeline(conn)
        st.success("Updated!")

source_filter = st.selectbox("Filter by source", ["All", "arXiv", "News"])

rows = get_all_items(conn)
if source_filter != "All":
    rows = [r for r in rows if r[0] == source_filter]

if not rows:
    st.info("No insights yet — click 'Run tracker now' to fetch the latest.")
else:
    for source, title, link, summary, fetched_at in rows:
        with st.container(border=True):
            st.markdown(f"**[{title}]({link})**  \n*{source} • {fetched_at[:16]}*")
            st.write(summary)