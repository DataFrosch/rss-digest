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
2. `llm_processor.py` - Sends articles to OpenRouter API for digest generation
3. `email_sender.py` - Sends HTML digest via SendGrid
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
- Returns list of dicts with: title, link, published, source, description

### src/llm_processor.py
- `LLMProcessor` class wraps OpenRouter API
- Uses OpenAI SDK (OpenRouter is OpenAI-compatible)
- `generate_digest_from_articles()` - single LLM call for entire digest
- Tracks token usage for cost estimation
- No streaming, no retries (fails fast)

### src/email_sender.py
- `EmailSender` class wraps SendGrid API
- `send_digest()` - sends HTML email
- `save_digest_html()` - saves to file for testing
- Uses template from `templates/email_template.html`

### config/feeds.py
- `RSS_FEEDS` dict - feed URLs by category
- `DIGEST_GENERATION_PROMPT` - LLM instructions for digest format
- **Important**: This is user configuration, customize for their needs

## Environment Variables

Required in `.env`:
- `OPENROUTER_API_KEY` - From openrouter.ai/keys
- `LLM_MODEL` - Model identifier (e.g., google/gemini-flash-1.5-8b)
- `SENDGRID_API_KEY` - From SendGrid dashboard
- `RECIPIENT_EMAIL` - Where to send digest
- `FROM_EMAIL` - Must be verified in SendGrid

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

### Switching LLM Model
Change `LLM_MODEL` in `.env`. Must be an OpenRouter-compatible model identifier.

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
- `openai` - OpenRouter API client
- `sendgrid` - Email sending
- `python-dateutil` - Date handling
- `python-dotenv` - Environment variables

Install with: `uv sync`

### Python Version
Requires Python 3.13+ (specified in `pyproject.toml`)

## Common Issues

### "No articles found"
- RSS feeds might not have articles in the date range
- Try `--days 14` to extend range
- Use `--verbose` to see what's being fetched

### "Failed to generate digest"
- Check OpenRouter API key is valid
- Verify model name is correct
- Check OpenRouter account has credits
- Review `digest.log` for API errors

### "Failed to send email"
- Verify FROM_EMAIL is verified in SendGrid
- Check SendGrid API key permissions (needs "Mail Send")
- Review SendGrid dashboard for bounce/error details

### Import errors
- Run `uv sync` to install dependencies
- Ensure you're using `uv run python` to run scripts

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

With default settings (Gemini Flash 1.5 8B):
- ~15K input tokens per 50 articles
- ~2K output tokens for digest
- Cost: ~$0.0017 per run
- Monthly (4 runs): ~$0.007

SendGrid free tier: 100 emails/day (more than enough)

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

### Why OpenRouter?
- Access to multiple models via one API
- Competitive pricing
- Simple OpenAI-compatible interface
- No vendor lock-in (can switch models easily)

### Why SendGrid?
- Generous free tier
- Reliable delivery
- Simple API
- Industry standard

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
uv run python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OK' if all([os.getenv(v) for v in ['OPENROUTER_API_KEY', 'SENDGRID_API_KEY', 'FROM_EMAIL', 'RECIPIENT_EMAIL']]) else 'Missing vars')"
```

## Code Style

- Standard Python conventions
- Type hints encouraged but not required
- Docstrings for public methods
- Simple, readable code over clever optimizations
- Logging at INFO level for user actions, DEBUG for details

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
