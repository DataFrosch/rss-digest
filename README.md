![](img/robot_writing.jpg)

# RSS Weekly Digest

A simple, stateless system to fetch RSS articles, generate AI-powered digests, and deliver them via email. No database, no complexity—just RSS feeds, an LLM, and your inbox.

## Features

- **Stateless & Simple**: No database, no state tracking, no complex setup
- **AI-Powered Digests**: Uses any OpenAI-compatible LLM API (OpenAI, DeepSeek, OpenRouter, etc.)
- **Email Delivery**: Clean HTML digests sent via SendGrid
- **Flexible Scheduling**: Run locally, via cron, or GitHub Actions
- **Cost-Effective**: ~$0.007/month with Gemini Flash or DeepSeek (~1 cent!)
- **Easy to Customize**: Simple config files for feeds and prompts

## How It Works

```
RSS Feeds → Fetch Articles → LLM Analysis → Email Digest
```

1. **Fetch**: Pull articles from configured RSS feeds (default: last 7 days)
2. **Analyze**: Send all articles to LLM in a single API call to generate digest
3. **Send**: Email the HTML digest via SendGrid

That's it. No database, no state, no tracking.

## Quick Start

```bash
# 1. Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone <your-repo-url>
cd rss-digest
uv sync

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys (see Setup section)

# 4. Run
uv run python src/main.py
```

## Setup

### 1. Get API Keys

You'll need two accounts:

**LLM API** (Choose one provider)

Option A: **OpenAI**
- Sign up at [platform.openai.com](https://platform.openai.com)
- Go to [API Keys](https://platform.openai.com/api-keys) and create a key
- Copy your API key (will be `OPENAI_API_KEY`)
- Leave `OPENAI_BASE_URL` empty in your `.env`

Option B: **DeepSeek** (Cost-effective)
- Sign up at [platform.deepseek.com](https://platform.deepseek.com)
- Go to API Keys and create a key
- Copy your API key (will be `OPENAI_API_KEY`)
- Set `OPENAI_BASE_URL=https://api.deepseek.com` in your `.env`

Option C: **OpenRouter** (Access to multiple models)
- Sign up at [openrouter.ai](https://openrouter.ai)
- Go to [Keys](https://openrouter.ai/keys) and create an API key
- Copy your API key (will be `OPENAI_API_KEY`)
- Set `OPENAI_BASE_URL=https://openrouter.ai/api/v1` in your `.env`

**SendGrid** (Email)
- Sign up at [sendgrid.com](https://sendgrid.com) (free tier: 100 emails/day)
- Go to Settings → API Keys → Create API Key
- Choose "Mail Send" permissions and copy your `SENDGRID_API_KEY`
- Go to Settings → Sender Authentication
- Verify your sender email address (this becomes `FROM_EMAIL`)

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` based on your chosen provider:

**For OpenAI:**
```bash
OPENAI_API_KEY=sk-xxx...
OPENAI_BASE_URL=
LLM_MODEL=gpt-4o-mini
SENDGRID_API_KEY=SG.xxx...
RECIPIENT_EMAIL=you@example.com
FROM_EMAIL=verified-sender@example.com
```

**For DeepSeek:**
```bash
OPENAI_API_KEY=sk-xxx...
OPENAI_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
SENDGRID_API_KEY=SG.xxx...
RECIPIENT_EMAIL=you@example.com
FROM_EMAIL=verified-sender@example.com
```

**For OpenRouter:**
```bash
OPENAI_API_KEY=sk-or-v1-xxx...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=google/gemini-flash-1.5-8b
SENDGRID_API_KEY=SG.xxx...
RECIPIENT_EMAIL=you@example.com
FROM_EMAIL=verified-sender@example.com
```

### 3. Customize Feeds (Optional)

Edit `config/feeds.py` to add your RSS feeds:

```python
RSS_FEEDS = {
    "Tech News": "https://example.com/feed.xml",
    "Your Blog": "https://yourblog.com/rss",
}
```

You can also customize the LLM prompt in the same file.

## Usage

### Basic Commands

```bash
# Full digest (fetch, generate, send)
uv run python src/main.py

# Test with 5 articles only
uv run python src/main.py --test

# Generate but don't send email
uv run python src/main.py --dry-run

# Custom date range (last 14 days)
uv run python src/main.py --days 14

# Verbose logging
uv run python src/main.py --verbose

# Don't save HTML file locally
uv run python src/main.py --no-save
```

### Command Options

- `--test`: Process only 5 articles (for testing)
- `--dry-run`: Generate digest but don't send email
- `--days N`: Look back N days for articles (default: 7)
- `--verbose`: Enable detailed logging
- `--no-save`: Don't save digest HTML file locally

## Automation

### GitHub Actions

The repository includes a workflow file (`.github/workflows/weekly_digest.yml`) for automated weekly runs.

**Setup:**
1. Push to GitHub
2. Go to Settings → Secrets and variables → Actions
3. Add these secrets:
   - `OPENAI_API_KEY` (your LLM provider API key)
   - `OPENAI_BASE_URL` (optional, only if using DeepSeek/OpenRouter)
   - `LLM_MODEL`
   - `SENDGRID_API_KEY`
   - `RECIPIENT_EMAIL`
   - `FROM_EMAIL`
4. Enable GitHub Actions in the Actions tab

**Manual trigger:**
- Actions tab → "Weekly RSS Digest" → Run workflow

### Cron Job

Add to your crontab for weekly runs:
```bash
# Run every Monday at 9 AM
0 9 * * 1 cd /path/to/rss-digest && /path/to/uv run python src/main.py
```

## Customization

### RSS Feeds

Edit `config/feeds.py` to change your feeds:

```python
RSS_FEEDS = {
    "Tech": "https://example.com/tech.xml",
    "News": "https://example.com/news.xml",
}
```

### LLM Prompt

Customize the digest format in `config/feeds.py`:

```python
DIGEST_GENERATION_PROMPT = """Create a digest with these sections:
1. Summary
2. Top stories
3. Key insights
..."""
```

The prompt controls the structure, tone, and analysis of your digest.

### LLM Model

Change model in `.env` based on your provider:

**OpenAI models** (no OPENAI_BASE_URL):
```bash
LLM_MODEL=gpt-4o-mini        # Balanced quality and cost
# LLM_MODEL=gpt-4o           # High quality
# LLM_MODEL=gpt-3.5-turbo    # Fast and cheap
```

**DeepSeek models** (OPENAI_BASE_URL=https://api.deepseek.com):
```bash
LLM_MODEL=deepseek-chat      # Recommended, cost-effective
# LLM_MODEL=deepseek-reasoner # For complex reasoning
```

**OpenRouter models** (OPENAI_BASE_URL=https://openrouter.ai/api/v1):
```bash
LLM_MODEL=google/gemini-flash-1.5-8b  # Fast, cheap
# LLM_MODEL=anthropic/claude-3-5-sonnet # High quality
# See all models: https://openrouter.ai/models
```

### Email Template

Edit `templates/email_template.html` to customize the email design.

## Project Structure

```
rss-digest/
├── src/
│   ├── main.py           # Main orchestration
│   ├── rss_fetcher.py    # RSS feed fetching
│   ├── llm_processor.py  # LLM digest generation
│   └── email_sender.py   # Email sending
├── config/
│   └── feeds.py          # Feed URLs & prompts
├── templates/
│   └── email_template.html
├── .github/workflows/
│   └── weekly_digest.yml # GitHub Actions
├── .env.example          # Environment template
└── pyproject.toml        # Dependencies
```

## Cost Estimate

**With DeepSeek** (`deepseek-chat`):
- **Per digest**: ~$0.001-0.002 (50 articles)
- **Monthly**: ~$0.004-0.008 (less than 1 cent!)

**With OpenRouter** (`google/gemini-flash-1.5-8b`):
- **Per digest**: ~$0.0017 (50 articles)
- **Monthly**: ~$0.007 (less than 1 cent!)

**With OpenAI** (`gpt-4o-mini`):
- **Per digest**: ~$0.01-0.02 (50 articles)
- **Monthly**: ~$0.04-0.08 (about 5-8 cents)

**SendGrid**: Free tier (100 emails/day)

## Troubleshooting

**No articles?**
```bash
uv run python src/main.py --days 14 --verbose
```

**Email not sending?**
- Verify sender email in SendGrid
- Check `digest.log` for errors

**LLM errors?**
- Verify your LLM provider API key is correct
- Check that OPENAI_BASE_URL is set correctly for your provider
- Check account balance/credits

## Contributing

Issues and PRs welcome!

## License

MIT
