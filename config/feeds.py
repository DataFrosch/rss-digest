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

# LLM Prompt for digest generation
# Customize this prompt based on your interests and the type of content you're tracking
DIGEST_GENERATION_PROMPT = """You are creating a weekly digest for a European data journalist interested in markets and policy.

ARTICLES FROM {date_range} ({article_count} articles):
{article_list}

TONE AND LANGUAGE:
- Use factual, descriptive language
- State what happened, where, when, who was involved, and direct factual consequences
- Let events speak for themselves through clear description
- Focus on observable actions and stated positions
- Write in plain, straightforward prose

TASK: Analyze these articles and create a comprehensive digest with the following sections:

1. THIS WEEK'S BIG PICTURE
   - Analyze all articles to identify the main story or theme this week
   - Write ONE paragraph describing the main developments in simple, factual language
   - Focus on what's happening that matters most

2. TOP 3 ARTICLES TO READ
   - Select the 3 most important/interesting articles based on:
     * Relevance to European data journalists
     * Impact on markets and policy
     * Data journalism opportunities
   - For each article provide:
     * Title (as clickable link using the URL)
     * 2-3 sentence summary in plain language
     * Key context or direct impact (1 sentence, stated factually)

3. WHAT'S HAPPENING
   Choose ONE article for each theme below (select DIFFERENT articles from those in TOP 3):

   IN EUROPE:
   - Article title (as clickable link)
   - Simple 2-sentence summary
   - Focus on European politics, economy, or EU policy

   INTERNATIONALLY:
   - Article title (as clickable link)
   - Simple 2-sentence summary
   - Focus on global context relevant to Europe

   IN THE MARKETS:
   - Article title (as clickable link)
   - Simple 2-sentence summary
   - Include any ECB signals, European markets, or personal finance insights

4. DATA JOURNALISM OPPORTUNITIES
   - Specific story ideas with data angles from the articles
   - Datasets or sources mentioned
   - Cross-country comparison opportunities
   - Trends worth tracking

FORMATTING REQUIREMENTS:
- Use simple, clear language throughout (write like you're explaining to someone who's half asleep)
- Be to the point, use sober language, state facts directly
- Describe events as they occurred 
- Format as clean, semantic HTML:
  * <h2> for main sections
  * <h3> for subsections
  * <p> for paragraphs
  * <ul>/<li> for lists
  * <a href="url"> for article links
- Each article should appear only ONCE in the entire digest
- Do NOT include introductory text like "Here is your weekly digest..."
- Return ONLY the HTML content for the digest body (no html/head/body tags)

Begin your analysis and digest creation now:
"""
