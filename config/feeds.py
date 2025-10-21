"""
RSS feed configuration.
Easy to modify without changing core code.
"""

# Example feeds - replace with your own RSS feeds
RSS_FEEDS = {
    "Finance & Economics": "https://www.economist.com/finance-and-economics/rss.xml",
    "Europe": "https://www.economist.com/europe/rss.xml",
    "Business": "https://www.economist.com/business/rss.xml",
    "Leaders": "https://www.economist.com/leaders/rss.xml",
    "International": "https://www.economist.com/international/rss.xml",
    "Science & Technology": "https://www.economist.com/science-and-technology/rss.xml",
    "Data journalism" : "https://www.economist.com/graphic-detail/rss.xml"
}

# LLM Prompts - easily adjustable without changing core logic
# Customize these prompts based on your interests and the type of content you're tracking
ARTICLE_ANALYSIS_PROMPT = """Analyze this article headline and RSS snippet for a European data journalist interested in markets and policy.

Title: {title}
Snippet: {rss_summary}
Feed: {feed_category}
Published: {published_date}

Provide (in JSON format):
{{
  "summary": "2-3 sentence summary capturing the key point",
  "category": "one of: European Politics, European Economy, Personal Finance, EU Policy, Global Context, Data Journalism",
  "importance_score": 1-10 (how important/interesting for the target reader),
  "key_entities": ["list", "of", "entities"],
  "data_points": ["any", "numbers", "or", "data", "mentioned"],
  "why_interesting": "One sentence on why this matters to a European data journalist"
}}

Respond ONLY with valid JSON, no additional text."""

DIGEST_GENERATION_PROMPT = """Create a weekly digest for a European data journalist interested in markets and policy.

ARTICLES THIS WEEK ({article_count} articles):
{article_list}

Create a digest with these sections:

1. THIS WEEK'S BIG PICTURE
   Write ONE paragraph in simple, clear language summarizing the main story or theme this week.
   What's happening that matters most?

2. TOP 3 ARTICLES TO READ
   Pick the 3 most important articles this week.
   For each:
   - Title (as clickable link)
   - 2-3 sentence summary in plain language
   - Why it matters (1 sentence)

3. WHAT'S HAPPENING
   Choose ONE article for each of these themes (select DIFFERENT articles from those in TOP 3):

   IN EUROPE:
   - Article title (as link)
   - Simple 2-sentence summary

   INTERNATIONALLY:
   - Article title (as link)
   - Simple 2-sentence summary

   IN THE MARKETS:
   - Article title (as link)
   - Simple 2-sentence summary
   - Include any ECB signals, European markets, or personal finance insights

4. DATA JOURNALISM OPPORTUNITIES
   - Specific story ideas with data angles
   - Datasets or sources mentioned
   - Cross-country comparison opportunities

IMPORTANT: Each article should appear only ONCE in the entire digest. Do not feature the same article in multiple sections.

Use simple, clear language throughout. Write like you're explaining to someone who's half asleep.
Format in clean HTML (use <h2> for sections, <h3> for subsections, <p> for paragraphs, <ul>/<li> for lists, <a> for links).
Do NOT include any introductory text like "Here is your weekly digest...".
Return a html page
"""
