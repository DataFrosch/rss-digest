# Quick Start Guide

Get your Economist digest running in 15 minutes!

## 1. Install uv and Dependencies (2 min)

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## 2. Set Up Supabase (5 min)

1. Go to [supabase.com](https://supabase.com) → Create new project
2. Once ready, go to SQL Editor
3. Copy and paste contents of `setup_database.sql`
4. Click "Run"
5. Go to Settings → API
   - Copy your Project URL
   - Copy your anon/public key

## 3. Get API Keys (5 min)

### OpenRouter
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign in with Google/GitHub
3. Go to [Keys](https://openrouter.ai/keys) → Create key
4. Add $5 credits (optional, but recommended)

### SendGrid
1. Go to [sendgrid.com](https://sendgrid.com) → Sign up (free)
2. Complete email verification
3. Settings → API Keys → Create API Key
4. Choose "Full Access" → Copy key
5. Settings → Sender Authentication → Verify your email

## 4. Configure Environment (2 min)

```bash
cp .env.example .env
nano .env  # or use your favorite editor
```

Fill in:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxxx...
OPENROUTER_API_KEY=sk-or-xxxx...
SENDGRID_API_KEY=SG.xxxx...
RECIPIENT_EMAIL=your-email@example.com
```

## 5. Test It! (1 min)

```bash
uv run python src/main.py --test --dry-run
# Or use: make test-run
```

This will:
- Fetch 5 articles
- Process them with AI
- Save digest as HTML (won't send email)

Check the generated `digest_XXXXXX.html` file!

## 6. Send Real Digest

```bash
uv run python src/main.py --test
# Or use: make test-run
```

Check your email! 📧

## 7. Set Up GitHub Actions (Optional)

1. Push to GitHub
2. Go to Settings → Secrets and variables → Actions
3. Add all 5 secrets from your `.env` file
4. Done! Runs every Monday at 7 AM CET

## Troubleshooting

**No articles found?**
```bash
uv run python src/main.py --days 14 --test  # Try longer date range
```

**Email not sending?**
- Check SendGrid dashboard for errors
- Verify sender email is confirmed
- Check `economist_digest.log`

**Database errors?**
- Verify Supabase credentials
- Make sure you ran `setup_database.sql`

## What's Next?

- Read the full [README.md](README.md) for all options
- Customize RSS feeds in `config/rss_feeds.py`
- Adjust LLM prompts for your interests
- Set up GitHub Actions for automation

Enjoy your automated Economist digest! 🎉
