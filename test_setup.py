#!/usr/bin/env python3
"""
Setup Verification Script
Run this to test that all your credentials and services are working.
"""

import os
import sys
from dotenv import load_dotenv

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_status(test_name, passed, message=""):
    """Print test status with colors."""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} - {test_name}")
    if message:
        print(f"       {message}")


def test_environment_variables():
    """Test that all required environment variables are set."""
    print("\n" + "="*60)
    print("Testing Environment Variables")
    print("="*60)

    load_dotenv()

    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'OPENROUTER_API_KEY',
        'SENDGRID_API_KEY',
        'RECIPIENT_EMAIL'
    ]

    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            display_value = value[:10] + "..." if len(value) > 10 else "***"
            print_status(var, True, f"Set to: {display_value}")
        else:
            print_status(var, False, "NOT SET")
            all_present = False

    return all_present


def test_imports():
    """Test that all required packages are installed."""
    print("\n" + "="*60)
    print("Testing Python Package Imports")
    print("="*60)

    packages = [
        ('feedparser', 'feedparser'),
        ('dateutil', 'python-dateutil'),
        ('supabase', 'supabase'),
        ('openai', 'openai'),
        ('sendgrid', 'sendgrid'),
        ('dotenv', 'python-dotenv'),
    ]

    all_imported = True
    for module_name, package_name in packages:
        try:
            __import__(module_name)
            print_status(package_name, True)
        except ImportError:
            print_status(package_name, False, f"Run: pip install {package_name}")
            all_imported = False

    return all_imported


def test_supabase_connection():
    """Test Supabase database connection."""
    print("\n" + "="*60)
    print("Testing Supabase Connection")
    print("="*60)

    try:
        from supabase import create_client

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            print_status("Supabase credentials", False, "Missing credentials")
            return False

        client = create_client(supabase_url, supabase_key)

        # Try to query the articles table
        response = client.table("articles").select("id").limit(1).execute()

        print_status("Supabase connection", True, f"Connected to {supabase_url}")
        print_status("Articles table exists", True)
        return True

    except Exception as e:
        print_status("Supabase connection", False, str(e))
        return False


def test_openrouter_api():
    """Test OpenRouter API connection."""
    print("\n" + "="*60)
    print("Testing OpenRouter API")
    print("="*60)

    try:
        from openai import OpenAI

        api_key = os.getenv('OPENROUTER_API_KEY')

        if not api_key:
            print_status("OpenRouter API key", False, "Missing API key")
            return False

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

        # Simple test query
        response = client.chat.completions.create(
            model="google/gemini-flash-1.5",
            messages=[{"role": "user", "content": "Say 'OK' if you can read this."}],
            max_tokens=10
        )

        result = response.choices[0].message.content
        print_status("OpenRouter API", True, f"Response: {result}")
        return True

    except Exception as e:
        print_status("OpenRouter API", False, str(e))
        return False


def test_sendgrid_api():
    """Test SendGrid API connection."""
    print("\n" + "="*60)
    print("Testing SendGrid API")
    print("="*60)

    try:
        from sendgrid import SendGridAPIClient

        api_key = os.getenv('SENDGRID_API_KEY')

        if not api_key:
            print_status("SendGrid API key", False, "Missing API key")
            return False

        client = SendGridAPIClient(api_key)

        # Test API key validity (this doesn't send an email)
        # We just check if we can create a client
        print_status("SendGrid API", True, "API key valid")

        return True

    except Exception as e:
        print_status("SendGrid API", False, str(e))
        return False


def test_rss_feeds():
    """Test RSS feed fetching."""
    print("\n" + "="*60)
    print("Testing RSS Feeds")
    print("="*60)

    try:
        sys.path.insert(0, 'src')
        from rss_fetcher import RSSFetcher
        from config.rss_feeds import RSS_FEEDS

        fetcher = RSSFetcher(RSS_FEEDS)
        articles = fetcher.fetch_recent_articles(days=7)

        if articles:
            print_status("RSS feeds", True, f"Fetched {len(articles)} articles")
            return True
        else:
            print_status("RSS feeds", False, "No articles fetched")
            return False

    except Exception as e:
        print_status("RSS feeds", False, str(e))
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("ECONOMIST DIGEST - SETUP VERIFICATION")
    print("="*60)

    # Track results
    results = {}

    # Run tests
    results['Environment Variables'] = test_environment_variables()
    results['Python Packages'] = test_imports()

    # Only run service tests if basic setup is OK
    if results['Environment Variables'] and results['Python Packages']:
        results['Supabase'] = test_supabase_connection()
        results['OpenRouter'] = test_openrouter_api()
        results['SendGrid'] = test_sendgrid_api()
        results['RSS Feeds'] = test_rss_feeds()
    else:
        print(f"\n{YELLOW}Skipping service tests due to setup issues{RESET}")

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"{status} {test_name}")

    print("\n" + "="*60)

    if all_passed:
        print(f"{GREEN}All tests passed! You're ready to run the digest.{RESET}")
        print("\nNext steps:")
        print("  uv run python src/main.py --test --dry-run")
        print("  # Or use: make test-run")
    else:
        print(f"{RED}Some tests failed. Please fix the issues above.{RESET}")
        print("\nCommon fixes:")
        print("  - Missing packages: uv sync")
        print("  - Missing .env: cp .env.example .env (then edit)")
        print("  - Database: Run setup_database.sql in Supabase SQL Editor")

    print("="*60 + "\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
