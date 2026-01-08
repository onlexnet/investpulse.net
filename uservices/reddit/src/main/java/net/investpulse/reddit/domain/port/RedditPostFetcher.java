package net.investpulse.reddit.domain.port;

import net.investpulse.common.dto.RawRedditPost;

import java.util.List;

/**
 * Port interface for fetching Reddit posts from subreddits.
 * Abstracts Reddit API fetching infrastructure from business logic.
 */
public interface RedditPostFetcher {

    /**
     * Fetches posts from a specific subreddit containing a ticker symbol.
     *
     * @param subreddit the subreddit name (e.g., "stocks", "investing")
     * @param ticker the stock ticker to search for (e.g., "AAPL", "TSLA")
     * @return list of raw Reddit posts matching the ticker
     */
    List<RawRedditPost> fetchPostsByTicker(String subreddit, String ticker);
}
