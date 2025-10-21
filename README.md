# Economist Weekly Digest

Automated system to fetch, analyze, and deliver weekly digests of The Economist articles tailored for European data journalists interested in markets, policy, and data-driven stories.

## Features

- 📰 **Automated RSS Monitoring**: Fetches articles from 6+ Economist RSS feeds
- 🤖 **AI-Powered Analysis**: Uses LLM (via OpenRouter) to summarize and categorize articles
- 📊 **Smart Prioritization**: Rates articles by importance (1-10) and extracts key entities/data points
- 📧 **Email Delivery**: Beautiful HTML digest sent via SendGrid
- ⚡ **Automated Scheduling**: Runs every Monday at 7 AM CET via GitHub Actions
- 💾 **Database Storage**: Persistent storage in Supabase (PostgreSQL)
- 💰 **Cost-Optimized**: Uses Gemini Flash 1.5 for minimal API costs

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ RSS Feeds   │───▶│  Supabase    │───▶│  OpenRouter │
│ (Economist) │    │  (Database)  │    │  (LLM API)  │
└─────────────┘    └──────────────┘    └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌──────────────────────────────┐
                    │   Main Orchestrator          │
                    │   (Python Script)            │
                    └──────────────────────────────┘
                                   │
                                   ▼
                           ┌───────────────┐
                           │   SendGrid    │
                           │   (Email)     │
                           └───────────────┘
                                   │
                                   ▼
                           📧 Weekly Digest
```

## Project Structure

```
economist-digest/
├── .github/
│   └── workflows/
│       └── weekly_digest.yml       # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── rss_fetcher.py              # RSS feed fetching
│   ├── database.py                 # Supabase database operations
│   ├── llm_processor.py            # LLM analysis
│   ├── email_sender.py             # SendGrid email sending
│   └── main.py                     # Main orchestration script
├── config/
│   └── rss_feeds.py                # RSS feeds and LLM prompts
├── templates/
│   └── email_template.html         # Email HTML template
├── .env.example                    # Environment variables template
├── .gitignore
├── requirements.txt                # Python dependencies
├── setup_database.sql              # Supabase schema setup
└── README.md                       # This file
```

## Setup Instructions

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- GitHub account (for automation)
- Supabase account (free tier)
- OpenRouter account (API access)
- SendGrid account (free tier)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd economist-digest
```

### 2. Install uv (if not already installed)

```bash
# On macOS and Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip:
pip install uv
```

### 3. Set Up Python Environment and Install Dependencies

```bash
# uv will automatically create a virtual environment and install dependencies
uv sync

# This will:
# - Install Python 3.13 if needed
# - Create a virtual environment (.venv)
# - Install all dependencies from pyproject.toml
```

### 4. Set Up Supabase

1. **Create a Supabase Project**
   - Go to [Supabase](https://supabase.com)
   - Click "New Project"
   - Choose a name and region (EU recommended)
   - Wait for project to be created

2. **Set Up Database**
   - Go to SQL Editor in your Supabase dashboard
   - Copy the contents of `setup_database.sql`
   - Paste and run the SQL script
   - Verify the `articles` table was created

3. **Get API Credentials**
   - Go to Project Settings → API
   - Copy your `Project URL` (SUPABASE_URL)
   - Copy your `anon/public` key (SUPABASE_KEY)

### 5. Set Up OpenRouter

1. **Get API Key**
   - Go to [OpenRouter](https://openrouter.ai)
   - Sign up or log in
   - Go to [Keys](https://openrouter.ai/keys)
   - Create a new API key
   - Copy your API key (OPENROUTER_API_KEY)

2. **Add Credits** (Optional)
   - Add $5-10 in credits
   - Gemini Flash 1.5 is very cheap (~$0.01-0.05 per week)

### 6. Set Up SendGrid

1. **Create Account**
   - Go to [SendGrid](https://sendgrid.com)
   - Sign up for free tier (100 emails/day)
   - Complete sender verification

2. **Create API Key**
   - Go to Settings → API Keys
   - Create new API key
   - Choose "Full Access" or "Mail Send" permissions
   - Copy your API key (SENDGRID_API_KEY)

3. **Verify Sender Email**
   - Go to Settings → Sender Authentication
   - Verify a single sender email (your email)
   - Or verify a domain if you have one

### 7. Configure Environment Variables

1. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials**
   ```bash
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   OPENROUTER_API_KEY=your-openrouter-key
   SENDGRID_API_KEY=your-sendgrid-key
   RECIPIENT_EMAIL=your-email@example.com
   ```

### 8. Set Up GitHub Actions

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Economist digest system"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Add GitHub Secrets**
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `OPENROUTER_API_KEY`
     - `SENDGRID_API_KEY`
     - `RECIPIENT_EMAIL`

3. **Enable GitHub Actions**
   - Go to Actions tab
   - Enable workflows if prompted
   - The workflow will run every Monday at 7 AM CET

## Usage

### Run Locally

#### Full Workflow
```bash
uv run python src/main.py
# Or using make:
make run
```

#### Test Mode (5 articles only)
```bash
uv run python src/main.py --test
# Or using make:
make test-run
```

#### Dry Run (generate but don't send email)
```bash
uv run python src/main.py --dry-run
# Or using make:
make dry-run
```

#### Fetch Only
```bash
uv run python src/main.py --fetch-only
# Or using make:
make fetch
```

#### Process Only (analyze unprocessed articles)
```bash
uv run python src/main.py --process-only
# Or using make:
make process
```

#### Send Only (generate digest from processed articles)
```bash
uv run python src/main.py --send-only
# Or using make:
make send
```

#### Verbose Logging
```bash
uv run python src/main.py --verbose
```

#### Custom Date Range
```bash
uv run python src/main.py --days 14  # Last 14 days
```

### Test Individual Modules

#### Test RSS Fetcher
```bash
uv run python src/rss_fetcher.py
```

#### Test Database Connection
```bash
uv run python src/database.py
```

#### Test LLM Processor
```bash
uv run python src/llm_processor.py
```

#### Test Email Sender
```bash
uv run python src/email_sender.py
```

### Manual GitHub Actions Trigger

1. Go to Actions tab in your GitHub repository
2. Click "Weekly Economist Digest"
3. Click "Run workflow"
4. Choose options:
   - Test mode: Yes/No
   - Dry run: Yes/No
5. Click "Run workflow"

## Customization

### Change RSS Feeds

Edit `config/rss_feeds.py`:

```python
RSS_FEEDS = {
    "Your Category": "https://www.economist.com/your-feed/rss.xml",
    # Add or remove feeds as needed
}
```

### Modify LLM Prompts

Edit prompts in `config/rss_feeds.py`:

```python
ARTICLE_ANALYSIS_PROMPT = """Your custom prompt here..."""
DIGEST_GENERATION_PROMPT = """Your custom digest prompt..."""
```

### Change LLM Model

Edit `src/llm_processor.py` or pass in constructor:

```python
processor = LLMProcessor(api_key, model="anthropic/claude-3-haiku")
```

Available models: [OpenRouter Models](https://openrouter.ai/docs#models)

### Customize Email Template

Edit `templates/email_template.html` to change the look and feel of your digest emails.

## Cost Estimation

### Weekly Costs (approximate)

- **Supabase**: Free tier (500 MB database, plenty for this use)
- **OpenRouter** (Gemini Flash 1.5):
  - ~50 articles/week × 1000 tokens = 50K tokens
  - Input: $0.075 per 1M tokens = ~$0.004
  - Output: $0.30 per 1M tokens = ~$0.015
  - **Total: ~$0.02/week** or **$1/year**
- **SendGrid**: Free tier (100 emails/day, we send 1/week)
- **GitHub Actions**: Free for public repos, 2000 min/month for private

**Total estimated cost: ~$1-2/year** 🎉

## Troubleshooting

### "No articles to process"

- Check if RSS feeds are accessible
- Verify date range (try `--days 14`)
- Check `articles` table in Supabase

### "Failed to send email"

- Verify SendGrid API key is correct
- Check sender email is verified in SendGrid
- Check SendGrid dashboard for error messages
- Look at `economist_digest.log` for details

### "Database connection failed"

- Verify Supabase URL and key are correct
- Check if Supabase project is active
- Verify `articles` table exists

### "LLM API error"

- Check OpenRouter API key is valid
- Verify you have credits in OpenRouter account
- Try a different model if rate limited

### GitHub Actions not running

- Check if secrets are properly set
- Verify workflow file syntax
- Check Actions tab for error messages
- Ensure repository has Actions enabled

### Import errors when running locally

- Run `uv sync` to ensure all dependencies are installed
- Check Python version is 3.13+ with `uv python list`
- Try `uv sync --reinstall` to reinstall dependencies

## Logs and Debugging

- **Log file**: `economist_digest.log` (created in working directory)
- **Verbose mode**: Use `--verbose` flag for detailed logging
- **GitHub Actions logs**: Available in Actions tab for 30 days
- **Digest HTML backups**: Saved as `digest_YYYYMMDD_HHMMSS.html`

## Database Queries

### View Statistics
```sql
SELECT * FROM digest_stats;
```

### View Recent Articles
```sql
SELECT title, feed_category, importance_score, published_date
FROM articles
ORDER BY published_date DESC
LIMIT 10;
```

### View Past Digests
```sql
SELECT * FROM weekly_digest_summary
ORDER BY digest_date DESC;
```

### Articles Not Yet Sent
```sql
SELECT COUNT(*) as pending_articles
FROM articles
WHERE processed = TRUE
AND included_in_email_date IS NULL;
```

## Advanced Features

### Save Digest as Markdown

The system saves HTML by default. To also save as Markdown, you can extend the `email_sender.py` module.

### Re-process Specific Week

```bash
# Mark articles as not sent
# Then run send-only
uv run python src/main.py --send-only
```

### View Token Usage Statistics

After running, check the logs for token usage:
```
LLM Usage This Run:
  Total tokens: 45234
  Estimated cost: $0.0178
```

## RSS Feeds Currently Monitored

1. Finance & Economics
2. Europe
3. Business
4. Britain
5. International
6. Science & Technology

## Email Digest Structure

1. **This Week's Big Picture**: Thematic overview
2. **Top 10 Articles to Read**: Most important articles
3. **Articles by Theme**: Grouped by topic
4. **Cross-Cutting Patterns**: Connections across stories
5. **Data Journalism Opportunities**: Story ideas with data angles
6. **Market & Portfolio Watch**: Financial insights and signals

## Security Notes

- Never commit `.env` file to git
- Keep API keys secure
- Use GitHub Secrets for credentials
- Rotate API keys periodically
- Use Supabase Row Level Security (RLS) if needed

## Contributing

Feel free to open issues or submit pull requests for improvements!

## License

MIT License - feel free to use and modify as needed.

## Support

For issues:
1. Check the troubleshooting section above
2. Review logs in `economist_digest.log`
3. Check GitHub Actions logs if using automation
4. Review Supabase logs in dashboard
5. Open a GitHub issue with details

## Roadmap / Future Enhancements

- [ ] Web dashboard to view past digests
- [ ] Multiple recipient support
- [ ] Slack/Discord integration
- [ ] Custom article filtering rules
- [ ] A/B testing for LLM prompts
- [ ] Export digests as Markdown or PDF
- [ ] Sentiment analysis on articles
- [ ] Topic trend tracking over time

---

Built with ❤️ for data journalists who love The Economist
