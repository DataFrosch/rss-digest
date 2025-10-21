"""
RSS Feed Fetcher
Retrieves articles from RSS feeds and parses them.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import feedparser
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


class RSSFetcher:
    """Fetches and parses RSS feeds."""

    def __init__(self, feeds: Dict[str, str]):
        """
        Initialize RSS fetcher with feed configuration.

        Args:
            feeds: Dictionary mapping feed names to URLs
        """
        self.feeds = feeds

    def fetch_recent_articles(self, days: int = 7) -> List[Dict]:
        """
        Fetch articles from all configured feeds from the past N days.

        Args:
            days: Number of days to look back (default 7)

        Returns:
            List of article dictionaries with parsed metadata
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        all_articles = []

        for feed_name, feed_url in self.feeds.items():
            logger.info(f"Fetching feed: {feed_name}")
            try:
                articles = self._fetch_single_feed(feed_url, feed_name, cutoff_date)
                all_articles.extend(articles)
                logger.info(f"Retrieved {len(articles)} articles from {feed_name}")
            except Exception as e:
                logger.error(f"Failed to fetch {feed_name}: {str(e)}")
                # Continue with other feeds even if one fails
                continue

        logger.info(f"Total articles retrieved: {len(all_articles)}")
        return all_articles

    def _fetch_single_feed(
        self,
        feed_url: str,
        feed_name: str,
        cutoff_date: datetime
    ) -> List[Dict]:
        """
        Fetch and parse a single RSS feed.

        Args:
            feed_url: URL of the RSS feed
            feed_name: Name/category of the feed
            cutoff_date: Only return articles after this date

        Returns:
            List of parsed article dictionaries
        """
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries:
            try:
                # Parse publication date
                pub_date = self._parse_date(entry)

                # Skip if too old
                if pub_date and pub_date < cutoff_date:
                    continue

                article = {
                    'url': entry.get('link', ''),
                    'title': entry.get('title', ''),
                    'rss_summary': entry.get('summary', ''),
                    'feed_category': feed_name,
                    'published_date': pub_date,
                }

                # Only add if we have essential fields
                if article['url'] and article['title']:
                    articles.append(article)

            except Exception as e:
                logger.warning(f"Failed to parse entry: {str(e)}")
                continue

        return articles

    def _parse_date(self, entry) -> Optional[datetime]:
        """
        Parse publication date from feed entry.
        Tries multiple common date fields.

        Args:
            entry: Feed entry object

        Returns:
            Parsed datetime or None if parsing fails
        """
        date_fields = ['published', 'updated', 'created']

        for field in date_fields:
            date_str = entry.get(field)
            if date_str:
                try:
                    return date_parser.parse(date_str)
                except Exception:
                    continue

        # Try parsed date fields
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6])
            except Exception:
                pass

        logger.warning(f"Could not parse date for entry: {entry.get('title', 'Unknown')}")
        return None


def test_feeds(feeds: Dict[str, str], days: int = 7) -> None:
    """
    Test function to verify RSS feeds are working.

    Args:
        feeds: Dictionary of feed names to URLs
        days: Number of days to look back
    """
    fetcher = RSSFetcher(feeds)
    articles = fetcher.fetch_recent_articles(days)

    print(f"\n=== RSS Feed Test Results ===")
    print(f"Total articles retrieved: {len(articles)}")
    print(f"\nSample articles:")

    for i, article in enumerate(articles[:5], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   Feed: {article['feed_category']}")
        print(f"   Date: {article['published_date']}")
        print(f"   URL: {article['url']}")
        print(f"   Summary: {article['rss_summary'][:100]}...")


if __name__ == "__main__":
    # Test the RSS fetcher
    from config.feeds import RSS_FEEDS

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    test_feeds(RSS_FEEDS)
