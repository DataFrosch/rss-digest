![](img/robot_writing.jpg)

# RSS Weekly Digest

Automated system to fetch, analyze, and deliver weekly digests from RSS feeds. Powered by AI to summarize and categorize articles based on your interests.

## Features

- 📰 **Automated RSS Monitoring**: Fetches articles from any RSS feeds you configure
- 🤖 **AI-Powered Analysis**: Uses LLM (via OpenRouter) to summarize and categorize articles
- 📊 **Smart Prioritization**: Rates articles by importance (1-10) and extracts key entities/data points
- 📧 **Email Delivery**: HTML digest sent via SendGrid
- ⚡ **Automated Scheduling**: Runs every Monday at 7 AM CET via GitHub Actions
- 💾 **Database Storage**: Persistent storage in Supabase (PostgreSQL)
- 💰 **Cost-Optimized**: Sacrifices privacy to use free models from [openrouter.ai](https://openrouter.ai/) (you can also use paid models and not sacrifice anything)

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ RSS Feeds   │───▶│  Supabase    │───▶│  OpenRouter │
│ (Any Source)│    │  (Database)  │    │  (LLM API)  │
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
rss-digest/
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
│   └── feeds.py                    # RSS feeds and LLM prompts
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
cd rss-digest
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
   - Verify a single sender email address
   - This will be your `FROM_EMAIL` in the `.env` file
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
   FROM_EMAIL=your-verified-sender@example.com
   ```

### 8. Set Up GitHub Actions

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: RSS digest system"
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
     - `LLM_MODEL`
     - `SENDGRID_API_KEY`
     - `RECIPIENT_EMAIL`
     - `FROM_EMAIL`

3. **Enable GitHub Actions**
   - Go to Actions tab
   - Enable workflows if prompted
   - The workflow will run every Monday at 7 AM CET

## Usage

### Run Locally

#### Full Workflow
```bash
uv run python src/main.py
```

#### Test Mode (5 articles only)
```bash
uv run python src/main.py --test
```

#### Dry Run (generate but don't send email)
```bash
uv run python src/main.py --dry-run
```

#### Fetch Only
```bash
uv run python src/main.py --fetch-only
```

#### Process Only (analyze unprocessed articles)
```bash
uv run python src/main.py --process-only
```

#### Send Only (generate digest from processed articles)
```bash
uv run python src/main.py --send-only
```

#### Custom Date Range
```bash
uv run python src/main.py --days 14  # Last 14 days
```

### Manual GitHub Actions Trigger

1. Go to Actions tab in your GitHub repository
2. Click "Weekly RSS Digest"
3. Click "Run workflow"
4. Choose options:
   - Test mode: Yes/No
   - Dry run: Yes/No
5. Click "Run workflow"

## Customization

### Change RSS Feeds

Edit `config/feeds.py`:

```python
RSS_FEEDS = {
    "Your Category": "https://example.com/your-feed/rss.xml",
    # Add or remove feeds as needed
    # Works with any RSS feed from any source
}
```

### Modify LLM Prompts

Edit prompts in `config/feeds.py` to customize for your interests:

```python
ARTICLE_ANALYSIS_PROMPT = """Your custom prompt here..."""
DIGEST_GENERATION_PROMPT = """Your custom digest prompt..."""
```

### LLM Model

Available models: [OpenRouter Models](https://openrouter.ai/docs#models)

### Customize Email Template

Edit `templates/email_template.html` to change the look and feel of your digest emails.

## Contributing

Feel free to open issues or submit pull requests for improvements!

## License

MIT License - feel free to use and modify