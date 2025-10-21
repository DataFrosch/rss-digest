# Quick Start Guide

Get your RSS digest running in 10 minutes!

## 1. Install uv and Dependencies (2 min)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## 2. Get API Keys (5 min)

### LLM Provider (Choose one)

**Option A: OpenAI**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up and add payment method
3. Go to [API Keys](https://platform.openai.com/api-keys) → Create key
4. Copy your API key

**Option B: DeepSeek (Recommended - Cost-effective)**
1. Go to [platform.deepseek.com](https://platform.deepseek.com)
2. Sign up
3. Go to API Keys → Create key
4. Copy your API key

**Option C: OpenRouter (Access to multiple models)**
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign in with Google/GitHub
3. Go to [Keys](https://openrouter.ai/keys) → Create key
4. Copy your API key

### SendGrid
1. Go to [sendgrid.com](https://sendgrid.com) → Sign up (free)
2. Complete email verification
3. Settings → API Keys → Create API Key
4. Choose "Full Access" → Copy key
5. Settings → Sender Authentication → Verify your email

## 3. Configure Environment (2 min)

```bash
cp .env.example .env
nano .env  # or use your favorite editor
```

Fill in based on your chosen provider:

**For OpenAI:**
```
OPENAI_API_KEY=sk-xxxx...
OPENAI_BASE_URL=
LLM_MODEL=gpt-4o-mini
SENDGRID_API_KEY=SG.xxxx...
RECIPIENT_EMAIL=your-email@example.com
FROM_EMAIL=your-verified-sender@example.com
```

**For DeepSeek:**
```
OPENAI_API_KEY=sk-xxxx...
OPENAI_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
SENDGRID_API_KEY=SG.xxxx...
RECIPIENT_EMAIL=your-email@example.com
FROM_EMAIL=your-verified-sender@example.com
```

**For OpenRouter:**
```
OPENAI_API_KEY=sk-or-xxxx...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=google/gemini-flash-1.5-8b
SENDGRID_API_KEY=SG.xxxx...
RECIPIENT_EMAIL=your-email@example.com
FROM_EMAIL=your-verified-sender@example.com
```

## 4. Test It! (1 min)

```bash
uv run python src/main.py --test --dry-run
```

This will:
- Fetch 5 articles from RSS feeds
- Generate digest with AI in a single call
- Save digest as HTML (won't send email)

Check the generated `digest_XXXXXX.html` file!

## 5. Send Real Digest

```bash
uv run python src/main.py --test
```

Check your email! 📧

## 6. Set Up Automation (Optional)

### GitHub Actions
1. Push to GitHub
2. Go to Settings → Secrets and variables → Actions
3. Add all secrets from your `.env` file:
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL` (optional, only if using DeepSeek/OpenRouter)
   - `LLM_MODEL`
   - `SENDGRID_API_KEY`
   - `RECIPIENT_EMAIL`
   - `FROM_EMAIL`
4. Edit `.github/workflows/weekly_digest.yml` to set your schedule
5. Done!

### Cron Job (Linux/macOS)
```bash
# Edit crontab
crontab -e

# Add line to run every Monday at 7 AM
0 7 * * 1 cd /path/to/rss-digest && /path/to/.venv/bin/python src/main.py
```

## Troubleshooting

**No articles found?**
```bash
uv run python src/main.py --days 14 --test  # Try longer date range
```

**Email not sending?**
- Check SendGrid dashboard for errors
- Verify sender email is confirmed
- Check `digest.log`

**LLM errors?**
- Verify your LLM provider API key is correct
- Check that OPENAI_BASE_URL is set correctly for your provider
- Check account balance/credits
- Review error messages in `digest.log`

## What's Next?

- Read the full [README.md](README.md) for all options
- Customize RSS feeds in `config/feeds.py`
- Adjust LLM prompt for your interests in `config/feeds.py`
- Modify email template in `templates/email_template.html`

## How It Works

The application is completely stateless:
1. **Fetch**: Grabs articles from RSS feeds (last 7 days by default)
2. **Analyze**: Sends all articles to LLM in one API call to generate comprehensive digest
3. **Send**: Emails the digest via SendGrid

No database, no storage, no complexity!

## Command Line Options

```bash
# Basic usage
uv run python src/main.py

# Test with 5 articles
uv run python src/main.py --test

# Generate but don't send
uv run python src/main.py --dry-run

# Look back 14 days
uv run python src/main.py --days 14

# Verbose logging
uv run python src/main.py --verbose

# Don't save HTML file
uv run python src/main.py --no-save

# Combine options
uv run python src/main.py --test --dry-run --verbose
```

Enjoy your automated RSS digest! 🎉
