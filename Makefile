.PHONY: help install sync test setup clean run test-run dry-run fetch process send stats

# Default target
help:
	@echo "RSS Weekly Digest - Available Commands"
	@echo "============================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install      - Install Python dependencies with uv"
	@echo "  make sync         - Sync dependencies from lockfile"
	@echo "  make setup        - Create .env file from template"
	@echo "  make test-setup   - Verify all credentials and services"
	@echo ""
	@echo "Run Commands:"
	@echo "  make run          - Run full digest workflow"
	@echo "  make test-run     - Test mode (5 articles, real email)"
	@echo "  make dry-run      - Generate digest without sending email"
	@echo "  make fetch        - Only fetch and store articles"
	@echo "  make process      - Only process unprocessed articles"
	@echo "  make send         - Only generate and send digest"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make stats        - Show database statistics"
	@echo "  make clean        - Remove generated files and caches"
	@echo "  make logs         - View recent logs"
	@echo ""

# Setup commands
install:
	uv sync

sync:
	uv sync

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your credentials."; \
	else \
		echo ".env file already exists."; \
	fi

test-setup:
	uv run python test_setup.py

# Run commands
run:
	uv run python src/main.py

test-run:
	uv run python src/main.py --test

dry-run:
	uv run python src/main.py --dry-run

fetch:
	uv run python src/main.py --fetch-only

process:
	uv run python src/main.py --process-only

send:
	uv run python src/main.py --send-only

# Utility commands
stats:
	@echo "Database statistics:"
	@uv run python -c "import sys; sys.path.insert(0, 'src'); from database import Database; import os; from dotenv import load_dotenv; load_dotenv(); db = Database(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); stats = db.get_stats(); print('\\n'.join([f'{k}: {v}' for k, v in stats.items()]))"

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "digest_*.html" -delete
	rm -f src/rss_digest.log
	@echo "Cleaned generated files and caches"

logs:
	@if [ -f src/rss_digest.log ]; then \
		tail -50 src/rss_digest.log; \
	else \
		echo "No log file found"; \
	fi
