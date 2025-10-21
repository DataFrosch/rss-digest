"""
Main Orchestration Script
Coordinates RSS fetching, LLM processing, and email sending.
"""

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta, date
from typing import Optional

from dotenv import load_dotenv

from rss_fetcher import RSSFetcher
from database import Database
from llm_processor import LLMProcessor
from email_sender import EmailSender
from config.rss_feeds import RSS_FEEDS, ARTICLE_ANALYSIS_PROMPT, DIGEST_GENERATION_PROMPT


# Configure logging
def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('economist_digest.log')
        ]
    )


logger = logging.getLogger(__name__)


class DigestOrchestrator:
    """Main orchestrator for the digest system."""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        openrouter_api_key: str,
        sendgrid_api_key: str,
        recipient_email: str
    ):
        """
        Initialize the orchestrator with all necessary credentials.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
            openrouter_api_key: OpenRouter API key
            sendgrid_api_key: SendGrid API key
            recipient_email: Email address to send digest to
        """
        self.rss_fetcher = RSSFetcher(RSS_FEEDS)
        self.database = Database(supabase_url, supabase_key)
        self.llm_processor = LLMProcessor(openrouter_api_key)
        self.email_sender = EmailSender(sendgrid_api_key)
        self.recipient_email = recipient_email

        logger.info("Digest orchestrator initialized")

    def fetch_and_store_articles(self, days: int = 7, limit: Optional[int] = None) -> int:
        """
        Fetch articles from RSS feeds and store in database.

        Args:
            days: Number of days to look back
            limit: Limit number of articles (for testing)

        Returns:
            Number of new articles stored
        """
        logger.info(f"Fetching articles from past {days} days")

        # Fetch articles
        articles = self.rss_fetcher.fetch_recent_articles(days)

        if limit:
            articles = articles[:limit]
            logger.info(f"Limited to {limit} articles for testing")

        # Store in database
        new_count = 0
        for article in articles:
            article_id = self.database.insert_article(article)
            if article_id:
                new_count += 1

        logger.info(f"Stored {new_count} new articles (out of {len(articles)} fetched)")
        return new_count

    def process_articles(self, limit: Optional[int] = None) -> int:
        """
        Process unprocessed articles with LLM.

        Args:
            limit: Limit number of articles to process (for testing)

        Returns:
            Number of articles processed
        """
        logger.info("Processing articles with LLM")

        # Get unprocessed articles
        articles = self.database.get_unprocessed_articles(limit)

        if not articles:
            logger.info("No articles to process")
            return 0

        logger.info(f"Processing {len(articles)} articles")

        processed_count = 0
        for article in articles:
            try:
                # Analyze article
                analysis = self.llm_processor.analyze_article(
                    article,
                    ARTICLE_ANALYSIS_PROMPT
                )

                if analysis:
                    # Update database with analysis
                    success = self.database.update_article_analysis(
                        url=article['url'],
                        llm_summary=analysis.get('summary', ''),
                        llm_category=analysis.get('category', 'Unknown'),
                        importance_score=analysis.get('importance_score', 5),
                        key_entities=analysis.get('key_entities', []),
                        data_points=analysis.get('data_points', [])
                    )

                    if success:
                        processed_count += 1
                else:
                    logger.warning(f"Failed to analyze article: {article['title']}")

            except Exception as e:
                logger.error(f"Error processing article {article['title']}: {str(e)}")
                continue

        logger.info(f"Successfully processed {processed_count} articles")

        # Log token usage
        usage = self.llm_processor.get_token_usage_summary()
        logger.info(f"Token usage: {usage['total_tokens']} tokens, estimated cost: ${usage['estimated_cost_usd']}")

        return processed_count

    def generate_and_send_digest(
        self,
        days: int = 7,
        dry_run: bool = False,
        save_html: bool = True
    ) -> bool:
        """
        Generate digest from processed articles and send via email.

        Args:
            days: Number of days to include in digest
            dry_run: If True, generate but don't send email
            save_html: If True, save digest as HTML file

        Returns:
            True if successful, False otherwise
        """
        logger.info("Generating weekly digest")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

        # Get articles for digest
        articles = self.database.get_articles_for_digest(start_date, end_date)

        if not articles:
            logger.warning("No articles available for digest")
            return False

        logger.info(f"Generating digest from {len(articles)} articles")

        # Generate digest
        digest_html = self.llm_processor.generate_digest(
            articles,
            DIGEST_GENERATION_PROMPT,
            date_range
        )

        if not digest_html:
            logger.error("Failed to generate digest")
            return False

        # Save HTML if requested
        if save_html:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"digest_{timestamp}.html"
            self.email_sender.save_digest_html(digest_html, date_range, filepath)

        # Send email (unless dry run)
        if not dry_run:
            logger.info("Sending digest email")
            success = self.email_sender.send_digest(
                recipient_email=self.recipient_email,
                digest_html=digest_html,
                date_range=date_range,
                article_count=len(articles),
                template_path="templates/email_template.html"
            )

            if success:
                # Mark articles as sent
                article_ids = [a['id'] for a in articles]
                self.database.mark_articles_sent(article_ids, date.today())
                logger.info("Digest sent successfully")
                return True
            else:
                logger.error("Failed to send digest email")
                return False
        else:
            logger.info("Dry run mode - email not sent")
            logger.info(f"Digest saved to HTML file")
            return True

    def run_full_workflow(
        self,
        days: int = 7,
        test_mode: bool = False,
        dry_run: bool = False
    ) -> None:
        """
        Run the complete workflow: fetch, process, and send.

        Args:
            days: Number of days to look back
            test_mode: If True, process only 5 articles
            dry_run: If True, generate but don't send email
        """
        logger.info("=" * 60)
        logger.info("STARTING ECONOMIST DIGEST WORKFLOW")
        logger.info("=" * 60)

        limit = 5 if test_mode else None

        try:
            # Step 1: Fetch and store articles
            logger.info("\n[STEP 1] Fetching articles from RSS feeds")
            new_articles = self.fetch_and_store_articles(days, limit)
            logger.info(f"✓ Fetched {new_articles} new articles")

            # Step 2: Process articles with LLM
            logger.info("\n[STEP 2] Processing articles with LLM")
            processed = self.process_articles(limit)
            logger.info(f"✓ Processed {processed} articles")

            # Step 3: Generate and send digest
            logger.info("\n[STEP 3] Generating and sending digest")
            success = self.generate_and_send_digest(days, dry_run)

            if success:
                logger.info("✓ Digest generated and sent successfully")
            else:
                logger.warning("⚠ Digest generation completed but email not sent")

            # Print statistics
            logger.info("\n" + "=" * 60)
            logger.info("WORKFLOW COMPLETE")
            logger.info("=" * 60)

            stats = self.database.get_stats()
            logger.info(f"\nDatabase Statistics:")
            for key, value in stats.items():
                logger.info(f"  {key}: {value}")

            usage = self.llm_processor.get_token_usage_summary()
            logger.info(f"\nLLM Usage This Run:")
            logger.info(f"  Total tokens: {usage['total_tokens']}")
            logger.info(f"  Estimated cost: ${usage['estimated_cost_usd']}")

        except Exception as e:
            logger.error(f"Error in workflow: {str(e)}", exc_info=True)
            sys.exit(1)


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Economist Weekly Digest - Automated RSS monitoring and digest generation"
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: process only 5 articles and send to test address'
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
        '--fetch-only',
        action='store_true',
        help='Only fetch and store articles, do not process or send'
    )

    parser.add_argument(
        '--process-only',
        action='store_true',
        help='Only process unprocessed articles, do not fetch or send'
    )

    parser.add_argument(
        '--send-only',
        action='store_true',
        help='Only generate and send digest from processed articles'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Load environment variables
    load_dotenv()

    # Check required environment variables
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'OPENROUTER_API_KEY',
        'SENDGRID_API_KEY',
        'RECIPIENT_EMAIL'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please check your .env file")
        sys.exit(1)

    # Initialize orchestrator
    orchestrator = DigestOrchestrator(
        supabase_url=os.getenv('SUPABASE_URL'),
        supabase_key=os.getenv('SUPABASE_KEY'),
        openrouter_api_key=os.getenv('OPENROUTER_API_KEY'),
        sendgrid_api_key=os.getenv('SENDGRID_API_KEY'),
        recipient_email=os.getenv('RECIPIENT_EMAIL')
    )

    # Run appropriate workflow based on arguments
    if args.fetch_only:
        logger.info("Running fetch-only mode")
        orchestrator.fetch_and_store_articles(args.days, 5 if args.test else None)
    elif args.process_only:
        logger.info("Running process-only mode")
        orchestrator.process_articles(5 if args.test else None)
    elif args.send_only:
        logger.info("Running send-only mode")
        orchestrator.generate_and_send_digest(args.days, args.dry_run)
    else:
        # Run full workflow
        orchestrator.run_full_workflow(
            days=args.days,
            test_mode=args.test,
            dry_run=args.dry_run
        )


if __name__ == "__main__":
    main()
