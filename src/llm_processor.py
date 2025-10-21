"""
LLM Processor Module
Handles digest generation directly from raw articles using OpenAI-compatible APIs.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from openai import OpenAI
from openai import RateLimitError, APIError, APIConnectionError

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Processes articles using LLM via OpenAI-compatible APIs."""

    def __init__(self, api_key: str, model: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize LLM processor.

        Args:
            api_key: OpenAI-compatible API key
            model: Model to use (optional, will use LLM_MODEL env var or default)
            base_url: Base URL for OpenAI-compatible API (optional, defaults to OpenAI API)
        """
        import os
        if model is None:
            model = os.getenv("LLM_MODEL")

        # Only pass base_url if it's provided and not empty
        if base_url:
            self.client = OpenAI(
                base_url=base_url,
                api_key=api_key
            )
            logger.info(f"LLM Processor initialized with model: {model}, base_url: {base_url}")
        else:
            self.client = OpenAI(
                api_key=api_key
            )
            logger.info(f"LLM Processor initialized with model: {model}")

        self.model = model
        self.total_tokens_used = 0

    def generate_digest_from_articles(
        self,
        articles: List[Dict],
        prompt_template: str,
        date_range: str
    ) -> Optional[str]:
        """
        Generate digest HTML directly from raw RSS articles in a single LLM call.

        Args:
            articles: List of raw article dictionaries from RSS feeds
            prompt_template: Prompt template for digest generation
            date_range: String describing the date range (e.g., "Jan 15-21, 2025")

        Returns:
            HTML formatted digest or None if failed
        """
        try:
            if not articles:
                logger.warning("No articles provided for digest generation")
                return None

            # Format article list for prompt
            article_list = self._format_raw_articles_for_prompt(articles)

            # Format prompt
            prompt = prompt_template.format(
                article_count=len(articles),
                article_list=article_list,
                date_range=date_range
            )

            logger.info(f"Generating digest for {len(articles)} articles")

            # Call LLM with larger token limit for digest
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skilled editor creating weekly news digests for data journalists. Analyze the provided articles and create a comprehensive digest in clean, semantic HTML."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,  # Balanced for analysis and creative synthesis
                max_tokens=4000  # Larger limit for full digest with analysis
            )

            # Track token usage
            if hasattr(response, 'usage'):
                tokens = response.usage.total_tokens
                self.total_tokens_used += tokens
                logger.info(f"Digest generation tokens used: {tokens}")

            digest_html = response.choices[0].message.content.strip()

            logger.info("Successfully generated digest")
            return digest_html

        except RateLimitError as e:
            logger.warning(f"Rate limit hit (429 Too Many Requests) during digest generation.")
            logger.debug(f"Rate limit error details: {str(e)}")
            return None
        except APIConnectionError as e:
            logger.error(f"API connection error during digest generation: {str(e)}")
            return None
        except APIError as e:
            logger.error(f"API error during digest generation: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error generating digest: {str(e)}")
            return None

    def _format_raw_articles_for_prompt(self, articles: List[Dict]) -> str:
        """
        Format raw RSS articles into a readable list for the LLM prompt.

        Args:
            articles: List of raw article dictionaries from RSS feeds

        Returns:
            Formatted string with article details
        """
        formatted = []

        for i, article in enumerate(articles, 1):
            # Format published date
            pub_date = article.get('published_date')
            if isinstance(pub_date, datetime):
                pub_date_str = pub_date.strftime('%Y-%m-%d')
            else:
                pub_date_str = str(pub_date) if pub_date else 'Unknown'

            article_text = f"""
Article {i}:
Title: {article.get('title', 'Unknown')}
URL: {article.get('url', 'Unknown')}
Feed: {article.get('feed_category', 'Unknown')}
Published: {pub_date_str}
Summary: {article.get('rss_summary', 'No summary available')}
"""
            formatted.append(article_text.strip())

        return "\n\n---\n\n".join(formatted)

    def get_token_usage_summary(self) -> Dict:
        """
        Get summary of token usage.

        Returns:
            Dictionary with token usage statistics
        """
        return {
            'total_tokens': self.total_tokens_used
        }


def test_llm(api_key: str, base_url: Optional[str] = None) -> None:
    """
    Test LLM processor functionality.

    Args:
        api_key: OpenAI-compatible API key
        base_url: Base URL for OpenAI-compatible API (optional)
    """
    processor = LLMProcessor(api_key, base_url=base_url)

    print("\n=== LLM Processor Test ===")
    print(f"Using model: {processor.model}")

    # Test digest generation from raw articles
    test_articles = [
        {
            'title': 'Europe\'s economy faces headwinds from energy crisis',
            'rss_summary': 'Rising energy costs and supply chain disruptions continue to challenge European economies, with Germany and France showing slowest growth in years.',
            'feed_category': 'Europe',
            'published_date': datetime(2025, 1, 20),
            'url': 'https://example.com/article1'
        },
        {
            'title': 'ECB signals potential rate cuts',
            'rss_summary': 'European Central Bank hints at easing monetary policy as inflation shows signs of cooling.',
            'feed_category': 'Finance & Economics',
            'published_date': datetime(2025, 1, 21),
            'url': 'https://example.com/article2'
        }
    ]

    from config.feeds import DIGEST_GENERATION_PROMPT

    result = processor.generate_digest_from_articles(
        test_articles,
        DIGEST_GENERATION_PROMPT,
        "Jan 15-21, 2025"
    )

    if result:
        print("\nDigest Generated Successfully!")
        print(f"Length: {len(result)} characters")
    else:
        print("\nDigest generation failed")

    # Print token usage
    usage = processor.get_token_usage_summary()
    print(f"\nToken Usage:")
    for key, value in usage.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if api_key:
        test_llm(api_key, base_url)
    else:
        print("Please set OPENAI_API_KEY in .env file")
