"""
Database Module
Handles all Supabase database operations for article storage and retrieval.
"""

import logging
from datetime import datetime, date
from typing import List, Dict, Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class Database:
    """Manages Supabase database operations for the digest system."""

    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Initialize database connection.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
        """
        self.client: Client = create_client(supabase_url, supabase_key)
        self.table_name = "articles"
        logger.info("Database connection initialized")

    def article_exists(self, url: str) -> bool:
        """
        Check if an article already exists in the database.

        Args:
            url: Article URL to check

        Returns:
            True if article exists, False otherwise
        """
        try:
            response = self.client.table(self.table_name).select("url").eq("url", url).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error checking article existence: {str(e)}")
            return False

    def insert_article(self, article: Dict) -> Optional[str]:
        """
        Insert a new article into the database.

        Args:
            article: Article dictionary with all fields

        Returns:
            Article ID if successful, None otherwise
        """
        try:
            # Check if already exists
            if self.article_exists(article['url']):
                logger.info(f"Article already exists: {article['title']}")
                return None

            # Prepare data for insertion
            data = {
                'url': article['url'],
                'title': article['title'],
                'rss_summary': article.get('rss_summary', ''),
                'feed_category': article.get('feed_category', ''),
                'published_date': article.get('published_date').isoformat() if article.get('published_date') else None,
                'processed': False
            }

            response = self.client.table(self.table_name).insert(data).execute()

            if response.data:
                article_id = response.data[0]['id']
                logger.info(f"Inserted article: {article['title']} (ID: {article_id})")
                return article_id
            else:
                logger.error(f"Failed to insert article: {article['title']}")
                return None

        except Exception as e:
            logger.error(f"Error inserting article: {str(e)}")
            return None

    def update_article_analysis(
        self,
        url: str,
        llm_summary: str,
        llm_category: str,
        importance_score: int,
        key_entities: List[str],
        data_points: List[str]
    ) -> bool:
        """
        Update an article with LLM analysis results.

        Args:
            url: Article URL to update
            llm_summary: Generated summary
            llm_category: Categorized category
            importance_score: 1-10 importance rating
            key_entities: List of extracted entities
            data_points: List of data points mentioned

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'llm_summary': llm_summary,
                'llm_category': llm_category,
                'importance_score': importance_score,
                'key_entities': key_entities,
                'data_points': data_points,
                'processed': True
            }

            response = self.client.table(self.table_name).update(data).eq("url", url).execute()

            if response.data:
                logger.info(f"Updated article analysis: {url}")
                return True
            else:
                logger.error(f"Failed to update article: {url}")
                return False

        except Exception as e:
            logger.error(f"Error updating article: {str(e)}")
            return False

    def get_unprocessed_articles(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve articles that haven't been processed by LLM yet.

        Args:
            limit: Maximum number of articles to retrieve (None for all)

        Returns:
            List of unprocessed article dictionaries
        """
        try:
            query = self.client.table(self.table_name).select("*").eq("processed", False)

            if limit:
                query = query.limit(limit)

            response = query.execute()
            logger.info(f"Retrieved {len(response.data)} unprocessed articles")
            return response.data

        except Exception as e:
            logger.error(f"Error retrieving unprocessed articles: {str(e)}")
            return []

    def get_articles_for_digest(
        self,
        start_date: datetime,
        end_date: datetime,
        only_processed: bool = True
    ) -> List[Dict]:
        """
        Retrieve articles for digest generation within a date range.

        Args:
            start_date: Start of date range
            end_date: End of date range
            only_processed: Only return processed articles (default True)

        Returns:
            List of article dictionaries sorted by importance score
        """
        try:
            query = self.client.table(self.table_name).select("*") \
                .gte("published_date", start_date.isoformat()) \
                .lte("published_date", end_date.isoformat())

            if only_processed:
                query = query.eq("processed", True)

            # Filter out articles already included in a digest
            query = query.is_("included_in_email_date", "null")

            response = query.order("importance_score", desc=True).execute()

            logger.info(f"Retrieved {len(response.data)} articles for digest")
            return response.data

        except Exception as e:
            logger.error(f"Error retrieving articles for digest: {str(e)}")
            return []

    def mark_articles_sent(self, article_ids: List[str], email_date: date) -> bool:
        """
        Mark articles as included in an email digest.

        Args:
            article_ids: List of article IDs
            email_date: Date of the digest email

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {'included_in_email_date': email_date.isoformat()}

            response = self.client.table(self.table_name) \
                .update(data) \
                .in_("id", article_ids) \
                .execute()

            if response.data:
                logger.info(f"Marked {len(article_ids)} articles as sent")
                return True
            else:
                logger.error("Failed to mark articles as sent")
                return False

        except Exception as e:
            logger.error(f"Error marking articles as sent: {str(e)}")
            return False

    def get_stats(self) -> Dict:
        """
        Get database statistics.

        Returns:
            Dictionary with various statistics
        """
        try:
            total = self.client.table(self.table_name).select("id", count="exact").execute()
            processed = self.client.table(self.table_name).select("id", count="exact").eq("processed", True).execute()
            sent = self.client.table(self.table_name).select("id", count="exact").not_.is_("included_in_email_date", "null").execute()

            return {
                'total_articles': total.count,
                'processed_articles': processed.count,
                'sent_articles': sent.count,
                'pending_processing': total.count - processed.count
            }

        except Exception as e:
            logger.error(f"Error retrieving stats: {str(e)}")
            return {}


def test_database(supabase_url: str, supabase_key: str) -> None:
    """
    Test database connectivity and basic operations.

    Args:
        supabase_url: Supabase project URL
        supabase_key: Supabase API key
    """
    db = Database(supabase_url, supabase_key)

    print("\n=== Database Test ===")

    # Test stats
    stats = db.get_stats()
    print(f"\nDatabase Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test article existence
    test_url = "https://www.economist.com/test-article"
    exists = db.article_exists(test_url)
    print(f"\nTest URL exists: {exists}")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if supabase_url and supabase_key:
        test_database(supabase_url, supabase_key)
    else:
        print("Please set SUPABASE_URL and SUPABASE_KEY in .env file")
