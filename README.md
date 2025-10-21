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

**LLM Provider** - Choose one:
- **OpenAI**: [platform.openai.com](https://platform.openai.com) → API Keys → Leave `OPENAI_BASE_URL` empty
- **DeepSeek** (recommended): [platform.deepseek.com](https://platform.deepseek.com) → Set `OPENAI_BASE_URL=https://api.deepseek.com`
- **OpenRouter**: [openrouter.ai/keys](https://openrouter.ai/keys) → Set `OPENAI_BASE_URL=https://openrouter.ai/api/v1`

**SendGrid** (Email):
- Sign up at [sendgrid.com](https://sendgrid.com) (free tier: 100 emails/day)
- Settings → API Keys → Create API Key
- Settings → Sender Authentication → Verify your email

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your keys - see .env.example for provider-specific examples
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

```bash
# Full digest
uv run python src/main.py

# Options:
#   --test        Process only 5 articles
#   --dry-run     Generate but don't send email
#   --days N      Look back N days (default: 7)
#   --verbose     Detailed logging
#   --no-save     Don't save HTML file locally
```

## Automation

**GitHub Actions**: Settings → Secrets → Add: `OPENAI_API_KEY`, `OPENAI_BASE_URL` (if needed), `LLM_MODEL`, `SENDGRID_API_KEY`, `FROM_EMAIL`, `RECIPIENT_EMAIL`

**Cron**: `0 9 * * 1 cd /path/to/rss-digest && uv run python src/main.py`

## Customization

- **RSS Feeds**: Edit `config/feeds.py`
- **LLM Prompt**: Edit `DIGEST_GENERATION_PROMPT` in `config/feeds.py`
- **LLM Model**: Change `LLM_MODEL` in `.env` (see `.env.example` for options)
- **Email Template**: Edit `templates/email_template.html`

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

- **DeepSeek**: ~$0.007/month (less than 1 cent!)
- **OpenRouter (Gemini)**: ~$0.007/month
- **OpenAI (GPT-4o-mini)**: ~$0.05/month
- **SendGrid**: Free (100 emails/day)

## Troubleshooting

- **No articles**: Try `--days 14 --verbose`
- **Email fails**: Verify sender in SendGrid, check `digest.log`
- **LLM errors**: Verify API key, check `OPENAI_BASE_URL`, check credits

## Contributing

Issues and PRs welcome!

## License

MIT
