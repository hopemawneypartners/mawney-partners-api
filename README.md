# Mawney Partners API

Credit markets news aggregation and AI summarization API for the Mawney Partners iOS app.

## Features

- 📰 Aggregates articles from 35+ financial news sources (RSS feeds)
- 🤖 AI-powered daily summaries using GPT-4
- 📊 Article categorization (Market Moves, People Moves, etc.)
- 🔍 Relevance scoring for credit markets content
- 🔄 Manual refresh endpoint for on-demand updates

## API Endpoints

### `GET /api/health`
Health check endpoint

### `GET /api/articles`
Returns all collected articles with categories and relevance scores

### `GET /api/ai/summary`
Returns AI-generated summary of articles from the past 24 hours

### `POST /api/trigger-collection`
Manually triggers article collection and refresh

## Deployment

Deployed on [Render.com](https://render.com) with automatic deployments from GitHub.

### Deploy Steps:
1. Push changes to GitHub repository
2. Render automatically detects changes and redeploys
3. API is live at: `https://mawney-daily-news-api.onrender.com`

## Environment Variables

Required on Render:
- `OPENAI_API_KEY` - For AI summarization features

## Tech Stack

- Python 3.11
- Flask (Web framework)
- OpenAI GPT-4 (AI summaries)
- feedparser (RSS parsing)
- Gunicorn (Production server)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

API will be available at `http://localhost:5000`

---

**Mawney Partners** - Credit Markets Intelligence Platform

