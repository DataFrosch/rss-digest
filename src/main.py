"""
Main Orchestration Script
Simplified workflow: Fetch RSS articles → Generate AI digest → Send email
No database dependencies - completely stateless.
"""

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv

from rss_fetcher import RSSFetcher
from llm_processor import LLMProcessor
from email_sender import EmailSender
from config.feeds import RSS_FEEDS, DIGEST_GENERATION_PROMPT


# Configure logging
def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('digest.log')
        ]
    )


logger = logging.getLogger(__name__)


class DigestOrchestrator:
    """Main orchestrator for the digest system."""

    def __init__(
        self,
        openai_api_key: str,
        sendgrid_api_key: str,
        from_email: str,
        recipient_email: str,
        openai_base_url: Optional[str] = None
    ):
        """
        Initialize the orchestrator with all necessary credentials.

        Args:
            openai_api_key: OpenAI-compatible API key
            sendgrid_api_key: SendGrid API key
            from_email: Sender email address (must be verified in SendGrid)
            recipient_email: Email address to send digest to
            openai_base_url: Base URL for OpenAI-compatible API (optional)
        """
        self.rss_fetcher = RSSFetcher(RSS_FEEDS)
        self.llm_processor = LLMProcessor(openai_api_key, base_url=openai_base_url)
        self.email_sender = EmailSender(sendgrid_api_key, from_email)
        self.recipient_email = recipient_email

        logger.info("Digest orchestrator initialized")

    def generate_and_send_digest(
        self,
        days: int = 7,
        dry_run: bool = False,
        save_html: bool = True,
        limit: Optional[int] = None
    ) -> bool:
        """
        Complete workflow: Fetch articles, generate digest, and send email.

        Args:
            days: Number of days to look back for articles
            dry_run: If True, generate but don't send email
            save_html: If True, save digest as HTML file
            limit: Limit number of articles (for testing)

        Returns:
            True if successful, False otherwise
        """
        logger.info("=" * 60)
        logger.info("STARTING RSS DIGEST WORKFLOW")
        logger.info("=" * 60)

        try:
            # Step 1: Fetch articles from RSS feeds
            logger.info(f"\n[STEP 1] Fetching articles from past {days} days")
            articles = self.rss_fetcher.fetch_recent_articles(days)

            if not articles:
                logger.warning("No articles fetched from RSS feeds")
                return False

            logger.info(f"✓ Fetched {len(articles)} articles")

            # Limit articles if specified (for testing)
            if limit:
                articles = articles[:limit]
                logger.info(f"Limited to {limit} articles for testing")

            # Step 2: Generate digest with LLM
            logger.info(f"\n[STEP 2] Generating digest from {len(articles)} articles")

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

            # Generate digest HTML in a single LLM call
            digest_html = self.llm_processor.generate_digest_from_articles(
                articles,
                DIGEST_GENERATION_PROMPT,
                date_range
            )

            if not digest_html:
                logger.error("Failed to generate digest")
                return False

            logger.info("✓ Digest generated successfully")

            # Log token usage
            usage = self.llm_processor.get_token_usage_summary()
            logger.info(f"Token usage: {usage['total_tokens']} tokens")

            # Step 3: Save HTML if requested
            if save_html:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = f"digest_{timestamp}.html"
                self.email_sender.save_digest_html(digest_html, date_range, filepath)
                logger.info(f"✓ Digest saved to {filepath}")

            # Step 3: Send email (unless dry run)
            if not dry_run:
                logger.info("\n[STEP 3] Sending digest email")
                success = self.email_sender.send_digest(
                    recipient_email=self.recipient_email,
                    digest_html=digest_html,
                    date_range=date_range,
                    article_count=len(articles),
                    template_path="templates/email_template.html"
                )

                if success:
                    logger.info("✓ Digest sent successfully")
                    logger.info("\n" + "=" * 60)
                    logger.info("WORKFLOW COMPLETE")
                    logger.info("=" * 60)
                    logger.info(f"\nSummary:")
                    logger.info(f"  Articles processed: {len(articles)}")
                    logger.info(f"  Date range: {date_range}")
                    logger.info(f"  Total tokens: {usage['total_tokens']}")
                    return True
                else:
                    logger.error("Failed to send digest email")
                    return False
            else:
                logger.info("\nDry run mode - email not sent")
                logger.info("✓ Digest saved to HTML file")
                logger.info("\n" + "=" * 60)
                logger.info("WORKFLOW COMPLETE (DRY RUN)")
                logger.info("=" * 60)
                logger.info(f"\nSummary:")
                logger.info(f"  Articles processed: {len(articles)}")
                logger.info(f"  Date range: {date_range}")
                logger.info(f"  Total tokens: {usage['total_tokens']}")
                return True

        except Exception as e:
            logger.error(f"Error in workflow: {str(e)}", exc_info=True)
            return False


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="RSS Weekly Digest - Automated RSS monitoring and digest generation"
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: process only 5 articles'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode: generate digest but do not send email'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back for articles (default: 7)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save digest as HTML file'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Load environment variables
    load_dotenv()

    # Check required environment variables
    required_vars = [
        'OPENAI_API_KEY',
        'LLM_MODEL',
        'SENDGRID_API_KEY',
        'FROM_EMAIL',
        'RECIPIENT_EMAIL'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file")
        sys.exit(1)

    # Initialize orchestrator
    orchestrator = DigestOrchestrator(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        sendgrid_api_key=os.getenv('SENDGRID_API_KEY'),
        from_email=os.getenv('FROM_EMAIL'),
        recipient_email=os.getenv('RECIPIENT_EMAIL'),
        openai_base_url=os.getenv('OPENAI_BASE_URL')
    )

    # Run workflow
    limit = 5 if args.test else None
    success = orchestrator.generate_and_send_digest(
        days=args.days,
        dry_run=args.dry_run,
        save_html=not args.no_save,
        limit=limit
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
