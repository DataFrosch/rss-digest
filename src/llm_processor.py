"""
LLM Processor Module
Handles article analysis and digest generation using OpenRouter API.
"""

import logging
import json
from typing import List, Dict, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Processes articles using LLM via OpenRouter API."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize LLM processor.

        Args:
            api_key: OpenRouter API key
            model: Model to use (optional, will use LLM_MODEL env var or default)
        """
        import os
        if model is None:
            model = os.getenv("LLM_MODEL", "google/gemini-flash-1.5-8b")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = model
        self.total_tokens_used = 0
        logger.info(f"LLM Processor initialized with model: {model}")

    def analyze_article(self, article: Dict, prompt_template: str) -> Optional[Dict]:
        """
        Analyze a single article using LLM.

        Args:
            article: Article dictionary with title, summary, etc.
            prompt_template: Prompt template with placeholders

        Returns:
            Dictionary with analysis results or None if failed
        """
        try:
            # Format prompt with article data
            prompt = prompt_template.format(
                title=article.get('title', 'Unknown'),
                rss_summary=article.get('rss_summary', 'No summary available'),
                feed_category=article.get('feed_category', 'Unknown'),
                published_date=article.get('published_date', 'Unknown')
            )

            logger.debug(f"Analyzing article: {article.get('title', 'Unknown')[:50]}...")

            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=500  # Reasonable limit for article analysis
            )

            # Track token usage
            if hasattr(response, 'usage'):
                tokens = response.usage.total_tokens
                self.total_tokens_used += tokens
                logger.debug(f"Tokens used: {tokens}")

            # Parse JSON response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            analysis = json.loads(content)

            logger.info(f"Successfully analyzed: {article.get('title', 'Unknown')[:50]}")
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"Response content: {content if 'content' in locals() else 'N/A'}")
            return None
        except Exception as e:
            logger.error(f"Error analyzing article: {str(e)}")
            return None

    def generate_digest(
        self,
        articles: List[Dict],
        prompt_template: str,
        date_range: str
    ) -> Optional[str]:
        """
        Generate weekly digest from analyzed articles.

        Args:
            articles: List of analyzed article dictionaries
            prompt_template: Prompt template for digest generation
            date_range: String describing the date range (e.g., "Jan 15-21, 2025")

        Returns:
            HTML formatted digest or None if failed
        """
        try:
            # Sort articles by importance score
            sorted_articles = sorted(
                articles,
                key=lambda x: x.get('importance_score', 0),
                reverse=True
            )

            # Format article list for prompt
            article_list = self._format_articles_for_prompt(sorted_articles)

            # Format prompt
            prompt = prompt_template.format(
                article_count=len(sorted_articles),
                article_list=article_list
            )

            logger.info(f"Generating digest for {len(sorted_articles)} articles")

            # Call LLM with larger token limit for digest
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skilled editor creating weekly news digests for data journalists. Format your output in clean, semantic HTML."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,  # Slightly higher for more creative synthesis
                max_tokens=3000  # Larger limit for full digest
            )

            # Track token usage
            if hasattr(response, 'usage'):
                tokens = response.usage.total_tokens
                self.total_tokens_used += tokens
                logger.info(f"Digest generation tokens used: {tokens}")

            digest_html = response.choices[0].message.content.strip()

            logger.info("Successfully generated digest")
            return digest_html

        except Exception as e:
            logger.error(f"Error generating digest: {str(e)}")
            return None

    def _format_articles_for_prompt(self, articles: List[Dict]) -> str:
        """
        Format articles into a readable list for the LLM prompt.

        Args:
            articles: List of article dictionaries

        Returns:
            Formatted string with article details
        """
        formatted = []

        for i, article in enumerate(articles, 1):
            article_text = f"""
Article {i}:
Title: {article.get('title', 'Unknown')}
URL: {article.get('url', 'Unknown')}
Feed: {article.get('feed_category', 'Unknown')}
Published: {article.get('published_date', 'Unknown')}
Summary: {article.get('llm_summary', article.get('rss_summary', 'No summary'))}
Category: {article.get('llm_category', 'Unknown')}
Importance Score: {article.get('importance_score', 'N/A')}/10
Key Entities: {', '.join(article.get('key_entities', []))}
Data Points: {', '.join(article.get('data_points', []))}
"""
            formatted.append(article_text.strip())

        return "\n\n---\n\n".join(formatted)

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost based on token usage.
        Pricing for google/gemini-flash-1.5-8b:
        - Input: $0.075 per 1M tokens
        - Output: $0.30 per 1M tokens

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        input_cost = (input_tokens / 1_000_000) * 0.075
        output_cost = (output_tokens / 1_000_000) * 0.30
        return input_cost + output_cost

    def get_token_usage_summary(self) -> Dict:
        """
        Get summary of token usage.

        Returns:
            Dictionary with token usage statistics
        """
        # Rough estimate: 60% input, 40% output
        estimated_input = int(self.total_tokens_used * 0.6)
        estimated_output = int(self.total_tokens_used * 0.4)
        estimated_cost = self.estimate_cost(estimated_input, estimated_output)

        return {
            'total_tokens': self.total_tokens_used,
            'estimated_input_tokens': estimated_input,
            'estimated_output_tokens': estimated_output,
            'estimated_cost_usd': round(estimated_cost, 4)
        }


def test_llm(api_key: str) -> None:
    """
    Test LLM processor functionality.

    Args:
        api_key: OpenRouter API key
    """
    processor = LLMProcessor(api_key)

    print("\n=== LLM Processor Test ===")
    print(f"Using model: {processor.model}")

    # Test article analysis
    test_article = {
        'title': 'Europe\'s economy faces headwinds from energy crisis',
        'rss_summary': 'Rising energy costs and supply chain disruptions continue to challenge European economies, with Germany and France showing slowest growth in years.',
        'feed_category': 'Europe',
        'published_date': '2025-01-20'
    }

    from config.feeds import ARTICLE_ANALYSIS_PROMPT

    result = processor.analyze_article(test_article, ARTICLE_ANALYSIS_PROMPT)

    if result:
        print("\nAnalysis Result:")
        print(json.dumps(result, indent=2))
    else:
        print("\nAnalysis failed")

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

    api_key = os.getenv("OPENROUTER_API_KEY")

    if api_key:
        test_llm(api_key)
    else:
        print("Please set OPENROUTER_API_KEY in .env file")
