-- Supabase Database Setup Script for Economist Digest
-- Run this in your Supabase SQL Editor to create the necessary tables

-- Create articles table
CREATE TABLE IF NOT EXISTS articles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    rss_summary TEXT,
    feed_category TEXT,
    published_date TIMESTAMPTZ,
    scraped_date TIMESTAMPTZ DEFAULT NOW(),
    llm_summary TEXT,
    llm_category TEXT,
    importance_score INTEGER CHECK (importance_score >= 1 AND importance_score <= 10),
    key_entities TEXT[],
    data_points TEXT[],
    processed BOOLEAN DEFAULT FALSE,
    included_in_email_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index on URL for faster lookups
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);

-- Create index on published_date for date range queries
CREATE INDEX IF NOT EXISTS idx_articles_published_date ON articles(published_date DESC);

-- Create index on processed status
CREATE INDEX IF NOT EXISTS idx_articles_processed ON articles(processed);

-- Create index on included_in_email_date for tracking sent digests
CREATE INDEX IF NOT EXISTS idx_articles_email_date ON articles(included_in_email_date);

-- Create index on importance_score for sorting
CREATE INDEX IF NOT EXISTS idx_articles_importance ON articles(importance_score DESC);

-- Create composite index for digest queries
CREATE INDEX IF NOT EXISTS idx_articles_digest_query
ON articles(published_date DESC, processed, included_in_email_date);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at on every update
CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Create a view for digest statistics
CREATE OR REPLACE VIEW digest_stats AS
SELECT
    COUNT(*) as total_articles,
    COUNT(*) FILTER (WHERE processed = TRUE) as processed_articles,
    COUNT(*) FILTER (WHERE included_in_email_date IS NOT NULL) as sent_articles,
    COUNT(*) FILTER (WHERE processed = FALSE) as pending_processing,
    COUNT(DISTINCT feed_category) as feed_categories,
    COUNT(DISTINCT DATE(published_date)) as days_covered,
    MIN(published_date) as earliest_article,
    MAX(published_date) as latest_article,
    ROUND(AVG(importance_score), 2) as avg_importance_score
FROM articles;

-- Optional: Create a view for weekly digest summaries
CREATE OR REPLACE VIEW weekly_digest_summary AS
SELECT
    included_in_email_date as digest_date,
    COUNT(*) as article_count,
    ROUND(AVG(importance_score), 2) as avg_importance,
    array_agg(DISTINCT feed_category) as categories_covered,
    array_agg(DISTINCT llm_category) as llm_categories
FROM articles
WHERE included_in_email_date IS NOT NULL
GROUP BY included_in_email_date
ORDER BY included_in_email_date DESC;

-- Optional: Create error log table for tracking failures
CREATE TABLE IF NOT EXISTS digest_errors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    error_type TEXT NOT NULL,
    error_message TEXT,
    article_id UUID REFERENCES articles(id),
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    additional_context JSONB
);

-- Create index on error occurred_at
CREATE INDEX IF NOT EXISTS idx_errors_occurred_at ON digest_errors(occurred_at DESC);

-- Grant necessary permissions (adjust as needed for your Supabase setup)
-- Note: Supabase typically handles permissions through their dashboard
-- These are here for reference/manual setups

-- Comment explaining the schema
COMMENT ON TABLE articles IS 'Stores articles fetched from Economist RSS feeds with LLM analysis';
COMMENT ON COLUMN articles.url IS 'Unique URL of the article (used for deduplication)';
COMMENT ON COLUMN articles.rss_summary IS 'Summary text from the RSS feed';
COMMENT ON COLUMN articles.llm_summary IS 'AI-generated summary from LLM analysis';
COMMENT ON COLUMN articles.llm_category IS 'Category assigned by LLM (European Politics, Economy, etc.)';
COMMENT ON COLUMN articles.importance_score IS 'Relevance score 1-10 assigned by LLM';
COMMENT ON COLUMN articles.key_entities IS 'Array of named entities extracted by LLM';
COMMENT ON COLUMN articles.data_points IS 'Array of data points/statistics mentioned in article';
COMMENT ON COLUMN articles.processed IS 'Whether article has been analyzed by LLM';
COMMENT ON COLUMN articles.included_in_email_date IS 'Date of digest email that included this article';

-- Display success message
DO $$
BEGIN
    RAISE NOTICE 'Database setup complete!';
    RAISE NOTICE 'Tables created: articles, digest_errors';
    RAISE NOTICE 'Views created: digest_stats, weekly_digest_summary';
    RAISE NOTICE 'You can now run queries like: SELECT * FROM digest_stats;';
END $$;
