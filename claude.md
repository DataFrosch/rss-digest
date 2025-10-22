# RSS Weekly Digest - Claude Documentation

This document provides context for AI assistants (like Claude) working on this project.

## Project Overview

**Purpose**: A stateless RSS digest generator that fetches articles, uses LLM to create summaries, and emails them.

**Key Design Principle**: Simplicity. No database, no state tracking, no complexity. Each run is completely independent.

## Architecture

```
RSS Feeds → fetch_recent_articles() → generate_digest() → send_email()
```

**Components**:
1. `rss_fetcher.py` - Fetches articles from RSS feeds using feedparser
2. `llm_processor.py` - Sends articles to any OpenAI-compatible API for digest generation
3. `email_sender.py` - Sends HTML digest via Gmail SMTP (Google Workspace)
4. `main.py` - Orchestrates the workflow

**No Database**: Articles are fetched fresh each run based on date range. Nothing is stored between runs.

## Project History

**Original Design**: Had a PostgreSQL database to track processed articles and avoid duplicates.

**Current Design**: Database removed entirely. The system fetches articles from the last N days (default: 7) and processes them all in a single LLM call. This is acceptable because:
- Weekly digests don't need deduplication
- Cost is negligible (~$0.002 per run with Gemini Flash, even free with openrouter.ai free models)
- Simpler architecture means easier maintenance

**Files Removed**:
- `src/database.py` - Database connection and queries
- `setup_database.sql` - Database schema
- `test_setup.py` - Database testing
- `Makefile` - Build tasks (no longer needed)
- `PROJECT_SUMMARY.md` - Outdated documentation

## Code Structure

### src/main.py
- Entry point with CLI argument parsing
- `DigestOrchestrator` class coordinates the workflow
- Handles environment variables and logging
- No business logic - pure orchestration

### src/rss_fetcher.py
- `RSSFetcher` class with single public method: `fetch_recent_articles(days)`
- Uses `feedparser` library
- Filters articles by publication date
- Returns list of dicts with: `url`, `title`, `rss_summary`, `feed_category`, `published_date`

### src/llm_processor.py
- `LLMProcessor` class wraps any OpenAI-compatible API
- Uses OpenAI SDK with configurable `base_url`
- Supports OpenAI, DeepSeek, OpenRouter, and other compatible providers
- `generate_digest_from_articles()` - single LLM call for entire digest
- Tracks token usage for cost estimation
- No streaming, no retries (fails fast)

### src/email_sender.py
- `EmailSender` class wraps Gmail SMTP
- `send_digest()` - sends HTML email via SMTP
- `save_digest_html()` - saves to file for testing
- Uses template from `templates/email_template.html`

### config/feeds.py
- `RSS_FEEDS` dict - feed URLs by category
- `DIGEST_GENERATION_PROMPT` - LLM instructions for digest format
- **Important**: This is user configuration, customize for their needs

## Environment Variables

Required in `.env`:
- `OPENAI_API_KEY` - API key from your chosen provider (OpenAI, DeepSeek, OpenRouter, etc.)
- `LLM_MODEL` - Model identifier (e.g., `gpt-4o-mini`, `deepseek-chat`, `google/gemini-flash-1.5-8b`)
- `SMTP_PASSWORD` - Google App Password for Gmail SMTP
- `FROM_EMAIL` - Gmail address for sending emails
- `RECIPIENT_EMAIL` - Where to send digest

Optional in `.env`:
- `OPENAI_BASE_URL` - Base URL for API provider. Leave empty for OpenAI, set to `https://api.deepseek.com` for DeepSeek, or `https://openrouter.ai/api/v1` for OpenRouter

## Common Tasks

### Adding a New RSS Feed
Edit `config/feeds.py`:
```python
RSS_FEEDS = {
    "Existing": "https://example.com/feed.xml",
    "New Feed": "https://newfeed.com/rss.xml",  # Add here
}
```

### Changing Digest Format
Edit `DIGEST_GENERATION_PROMPT` in `config/feeds.py`. The prompt is the entire UI for digest customization.

### Switching LLM Provider or Model
Change `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `LLM_MODEL` in `.env`:
- **OpenAI**: Leave `OPENAI_BASE_URL` empty, use models like `gpt-4o-mini`
- **DeepSeek**: Set `OPENAI_BASE_URL=https://api.deepseek.com`, use `deepseek-chat`
- **OpenRouter**: Set `OPENAI_BASE_URL=https://openrouter.ai/api/v1`, use any OpenRouter model

### Testing Changes
```bash
uv run python src/main.py --test --dry-run --verbose
```
This processes 5 articles, doesn't send email, and shows detailed logs.

## Development Guidelines

### When Making Changes

1. **Preserve Statelessness**: Don't add databases, caches, or persistent state
2. **Keep It Simple**: If it adds complexity, question if it's needed
3. **Test Locally First**: Use `--test --dry-run` flags
4. **Check Logs**: Output goes to both console and `digest.log`

### Dependencies

Managed via `pyproject.toml`:
- `feedparser` - RSS parsing
- `openai` - OpenAI-compatible API client
- `python-dateutil` - Date handling
- `python-dotenv` - Environment variables

Install with: `uv sync`

Note: Email sending uses Python's built-in `smtplib` and `email.mime` modules (no external dependency needed)

### Python Version
Requires Python 3.13+ (specified in `pyproject.toml`)

## Common Issues

### "No articles found"
- RSS feeds might not have articles in the date range
- Try `--days 14` to extend range
- Use `--verbose` to see what's being fetched

### "Failed to generate digest"
- Check `OPENAI_API_KEY` is valid for your provider
- Verify `OPENAI_BASE_URL` is set correctly (empty for OpenAI, provider URL otherwise)
- Verify model name is correct for your provider
- Check account has credits/balance
- Review `digest.log` for API errors

### "Failed to send email"
- Verify FROM_EMAIL is a valid Gmail address
- Check SMTP_PASSWORD is a valid Google App Password (not your regular Gmail password)
- Ensure 2-Factor Authentication is enabled on your Google Account
- Review `digest.log` for specific SMTP error messages

### Import errors
- Run `uv sync` to install dependencies
- Ensure you're using `uv run python` to run scripts
- Note: `main.py` uses relative imports (e.g., `from rss_fetcher import RSSFetcher`) which work because scripts are run from the project root with `uv run python src/main.py`

## File Locations

- **Logs**: `digest.log` (created in project root)
- **Generated digests**: `digest_YYYYMMDD_HHMMSS.html` (unless `--no-save`)
- **Config**: `config/feeds.py` and `.env`
- **Template**: `templates/email_template.html`

## GitHub Actions

Workflow in `.github/workflows/weekly_digest.yml`:
- Scheduled runs (weekly)
- Manual triggers with options
- Requires secrets configured in repo settings
- Runs on Ubuntu with Python 3.13

## Cost Considerations

Typical costs per run (50 articles):
- **DeepSeek** (`deepseek-chat`): ~$0.001-0.002
- **OpenRouter** (`google/gemini-flash-1.5-8b`): ~$0.0017
- **OpenAI** (`gpt-4o-mini`): ~$0.01-0.02

Monthly costs (4 weekly runs):
- **DeepSeek**: ~$0.007 (less than 1 cent)
- **OpenRouter**: ~$0.007 (less than 1 cent)
- **OpenAI**: ~$0.05 (about 5 cents)

## Design Decisions

### Why No Database?
- Adds operational complexity (backups, migrations, hosting)
- Not needed for weekly digests (occasional duplicates are fine)
- LLM costs are negligible anyway
- Easier to deploy (just environment variables)

### Why Single LLM Call?
- Simpler code (no multi-step processing)
- More coherent digests (LLM sees all context)
- Faster execution
- Cost difference is negligible vs. multiple calls

### Why OpenAI-Compatible APIs?
- Supports multiple providers (OpenAI, DeepSeek, OpenRouter, etc.)
- Simple, standardized interface via OpenAI SDK
- Configurable base URL allows easy provider switching
- No vendor lock-in (can switch providers with just env vars)
- Access to best price/performance for your needs

### Why Gmail SMTP?
- Free (included with any Gmail account)
- No API key registration or verification required (just App Password)
- Reliable delivery with Google's infrastructure
- No third-party service dependencies
- Uses standard SMTP protocol (built into Python)

## Future Considerations

If extending this project, consider:
- **Multi-language support**: Add prompt templates for different languages
- **Multiple recipients**: Loop over recipient list in email sender
- **Custom filters**: Allow filtering articles by keyword in config
- **Digest comparison**: Show what's new vs. last week (would need state)
- **Web interface**: View digests in browser instead of email

But remember: Keep it simple. The power of this tool is its simplicity.

## Quick Reference

```bash
# Test run (5 articles, no email)
uv run python src/main.py --test --dry-run

# Full run with verbose logs
uv run python src/main.py --verbose

# Custom date range
uv run python src/main.py --days 14

# Install dependencies
uv sync

# Check logs
cat digest.log

# Validate environment
uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OK' if all([os.getenv(v) for v in ['OPENAI_API_KEY', 'SMTP_PASSWORD', 'FROM_EMAIL', 'RECIPIENT_EMAIL']]) else 'Missing vars')"
```

## Code Style

- Standard Python conventions
- Type hints encouraged but not required
- Docstrings for public methods
- Simple, readable code over clever optimizations
- Logging at INFO level for user actions, DEBUG for details
- Emojis: Acceptable in user-facing content (email templates, final output) but not in code, logs, or technical documentation

## Testing Philosophy

No formal test suite. Testing approach:
1. Use `--test --dry-run` for quick validation
2. Check `digest.log` for errors
3. Manual verification of digest quality
4. Production runs are the real test

This is acceptable because:
- Simple codebase (< 500 lines)
- Failure is obvious (no email or error in logs)
- Low risk (worst case: no digest sent)

## When to Modify This File

Update `claude.md` when:
- Architecture changes significantly
- New major features added
- Design decisions change
- Common issues patterns emerge
- Development workflows change

Keep it focused on what AI assistants need to know to help effectively.
