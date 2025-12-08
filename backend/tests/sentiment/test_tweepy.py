import os
from datetime import datetime, timezone, timedelta
import tweepy

def test_twitter_client():
    """Initialize and test a Tweepy client using bearer token from environment."""
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("TWITTER_BEARER_TOKEN not set in environment")
    
    # Create polling client instead of streaming
    client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
    
    # Test by fetching a user and their recent tweets
    test_username = "Benzinga"  # Financial news account
    
    try:
        # Get user info
        user_response = client.get_user(username=test_username)
        if not user_response or not user_response.data:  # type: ignore
            print(f"User not found: {test_username}")
            return
        
        user_data = user_response.data  # type: ignore
        print(f"Found user: @{test_username} (ID: {user_data.id})")  # type: ignore
        
        # Fetch recent tweets
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        tweets_response = client.get_users_tweets(
            id=user_data.id,  # type: ignore
            max_results=10,
            tweet_fields=['created_at', 'public_metrics'],
            exclude=['retweets', 'replies'],
            start_time=start_time
        )
        
        if tweets_response and tweets_response.data:  # type: ignore
            tweets_data = tweets_response.data  # type: ignore
            print(f"Found {len(tweets_data)} recent tweets from @{test_username}")
            for tweet in tweets_data[:3]:  # Show first 3
                print(f"  - [{tweet.created_at}] {tweet.text[:80]}...")
        else:
            print(f"No recent tweets found for @{test_username}")
            
    except tweepy.TweepyException as e:
        print(f"Twitter API error: {e}")
    except Exception as e:
        print(f"Error: {e}")

