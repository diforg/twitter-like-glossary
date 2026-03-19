"""X (Twitter) API client for fetching liked tweets."""

import requests
import time
import json
import os
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path


class XAPIClient:
    """Client for interacting with X API."""
    
    def __init__(self, access_token: str):
        """Initialize the X API client.
        
        Args:
            access_token: OAuth 2.0 access token
        """
        self.access_token = access_token
        self.base_url = 'https://api.twitter.com/2'
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'TwitterLikeGlossary/1.0'
        }
        self.rate_limit_remaining = 75
        self.rate_limit_reset = 0
        self.min_request_interval = 1  # Minimum seconds between requests
        self.last_request_time = 0
    
    def _respect_rate_limit(self):
        """Respect rate limits by checking headers and adding delays."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        # Check if we need to wait for rate limit reset
        if self.rate_limit_remaining <= 0 and current_time < self.rate_limit_reset:
            wait_time = self.rate_limit_reset - current_time + 1
            print(f'Rate limit reached. Waiting {wait_time:.0f} seconds...')
            time.sleep(wait_time)
    
    def _update_rate_limit(self, response_headers):
        """Update rate limit information from response headers."""
        if 'x-rate-limit-remaining' in response_headers:
            self.rate_limit_remaining = int(response_headers['x-rate-limit-remaining'])
        
        if 'x-rate-limit-reset' in response_headers:
            self.rate_limit_reset = int(response_headers['x-rate-limit-reset'])
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to the X API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            JSON response or None if error
        """
        self._respect_rate_limit()
        
        url = f'{self.base_url}{endpoint}'
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            self._update_rate_limit(response.headers)
            self.last_request_time = time.time()
            
            if response.status_code == 401:
                print('Error: Unauthorized. Token may be expired.')
                return None
            
            if response.status_code == 429:
                print('Error: Rate limit exceeded')
                return None
            
            if response.status_code == 404:
                print('Error: Resource not found')
                return None
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            print('Error: Request timeout')
            return None
        except requests.exceptions.RequestException as e:
            print(f'Error making API request: {e}')
            return None
    
    def get_user_id(self) -> Optional[str]:
        """Get the authenticated user's ID.
        
        Returns:
            User ID or None if error
        """
        response = self._make_request('/users/me')
        
        if response and 'data' in response:
            return response['data']['id']
        
        return None
    
    def get_liked_tweets(self, user_id: str, max_results: int = 100) -> Optional[Dict]:
        """Fetch liked tweets for a user.
        
        Args:
            user_id: The user's ID
            max_results: Number of results per page (10-100)
            
        Returns:
            Response containing tweets or None if error
        """
        params = {
            'max_results': min(max_results, 100),
            'tweet.fields': 'created_at,author_id,public_metrics',
            'expansions': 'author_id,attachments.media_keys',
            'user.fields': 'username,name,verified',
            'media.fields': 'type,url,preview_image_url,public_metrics',
        }
        
        endpoint = f'/users/{user_id}/liked_tweets'
        return self._make_request(endpoint, params)
    
    def fetch_all_liked_tweets(self, user_id: str) -> List[Dict]:
        """Fetch all liked tweets with pagination.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of all liked tweets
        """
        all_tweets = []
        next_token = None
        page_count = 0
        
        while True:
            page_count += 1
            print(f'Fetching page {page_count}...')
            
            params = {
                'max_results': 100,
                'tweet.fields': 'created_at,author_id,public_metrics',
                'expansions': 'author_id,attachments.media_keys',
                'user.fields': 'username,name,verified',
                'media.fields': 'type,url,preview_image_url,public_metrics',
            }
            
            if next_token:
                params['pagination_token'] = next_token
            
            endpoint = f'/users/{user_id}/liked_tweets'
            response = self._make_request(endpoint, params)
            
            if not response or 'data' not in response:
                print('No more tweets to fetch or error occurred')
                break
            
            tweets = response['data']
            all_tweets.extend(tweets)
            
            print(f'Fetched {len(tweets)} tweets on this page. Total: {len(all_tweets)}')
            
            # Check for next page
            if 'meta' in response and 'next_token' in response['meta']:
                next_token = response['meta']['next_token']
            else:
                print('No more pages available')
                break
            
            # Get includes for this batch
            if 'includes' not in response:
                response['includes'] = {'users': [], 'media': []}
            
            # Store the response for processing
            response['tweets'] = tweets
            response['page'] = page_count
            
            yield response
    
    def process_liked_tweets(self, user_id: str, data_file: str = 'likes_data.json') -> List[Dict]:
        """Process and save all liked tweets.
        
        Args:
            user_id: The user's ID
            data_file: Path to save the JSON file
            
        Returns:
            List of processed tweets
        """
        all_tweets = []
        all_users = {}
        all_media = {}
        
        try:
            for response in self.fetch_all_liked_tweets(user_id):
                # Collect tweets
                if 'tweets' in response:
                    all_tweets.extend(response['tweets'])
                
                # Collect users
                if 'includes' in response and 'users' in response['includes']:
                    for user in response['includes']['users']:
                        all_users[user['id']] = user
                
                # Collect media
                if 'includes' in response and 'media' in response['includes']:
                    for media in response['includes']['media']:
                        all_media[media['media_key']] = media
        
        except Exception as e:
            print(f'Error fetching tweets: {e}')
        
        # Process tweets with enriched data
        processed_tweets = []
        for idx, tweet in enumerate(all_tweets, 1):
            author = all_users.get(tweet.get('author_id'), {})
            media_keys = tweet.get('attachments', {}).get('media_keys', [])
            media_list = [all_media.get(key) for key in media_keys if key in all_media]
            
            processed_tweet = {
                'sequence_number': idx,
                'tweet_id': tweet['id'],
                'text': tweet.get('text', ''),
                'created_at': tweet.get('created_at', ''),
                'author': {
                    'id': author.get('id'),
                    'name': author.get('name'),
                    'username': author.get('username'),
                    'verified': author.get('verified', False),
                },
                'media': [
                    {
                        'type': m.get('type'),
                        'url': m.get('url'),
                        'preview_image_url': m.get('preview_image_url'),
                    }
                    for m in media_list if m
                ],
                'metrics': tweet.get('public_metrics', {}),
            }
            
            processed_tweets.append(processed_tweet)
        
        # Save to JSON file
        try:
            os.makedirs(os.path.dirname(data_file) or '.', exist_ok=True)
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.utcnow().isoformat(),
                    'total_tweets': len(processed_tweets),
                    'tweets': processed_tweets,
                }, f, indent=2, ensure_ascii=False)
            
            print(f'Saved {len(processed_tweets)} tweets to {data_file}')
        
        except Exception as e:
            print(f'Error saving tweets to file: {e}')
        
        return processed_tweets
