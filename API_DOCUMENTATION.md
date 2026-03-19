# API Integration & Pagination Flow

## OAuth 2.0 Authentication Flow

```
User
  │
  ├─ Clicks "Login with X"
  │
  ├─ Redirected to X authorization server
  │  │
  │  ├─ User grants permission
  │  │
  │  └─ X redirects back with authorization code
  │
  ├─ Application exchanges code for access token
  │  │
  │  └─ X returns: access_token, refresh_token, expires_in
  │
  └─ Application stores tokens in session
     │
     └─ User can now access their likes
```

## Liked Tweets Collection Process

```
User Clicks "Refresh Likes"
  │
  └─ Application:
     │
     ├─ Gets authenticated user ID (/users/me)
     │
     ├─ Fetches first page of likes (100 per page)
     │  └─ GET /2/users/{user_id}/liked_tweets
     │     │
     │     ├─ Query Parameters:
     │     │  ├─ max_results: 100
     │     │  ├─ tweet.fields: created_at, author_id, public_metrics
     │     │  ├─ expansions: author_id, attachments.media_keys
     │     │  ├─ user.fields: username, name, verified
     │     │  └─ media.fields: type, url, preview_image_url
     │     │
     │     └─ Response:
     │        ├─ data: [tweets...]
     │        ├─ includes:
     │        │  ├─ users: [author info...]
     │        │  └─ media: [images/videos...]
     │        └─ meta:
     │           ├─ result_count: 100
     │           └─ next_token: "pagination_token"
     │
     ├─ Continues fetching pages while next_token exists
     │  └─ Each request includes: pagination_token={next_token}
     │
     ├─ Collects all tweets, users, and media
     │
     ├─ Processes tweets:
     │  ├─ Assigns sequence numbers (1, 2, 3... = oldest to newest)
     │  ├─ Enriches with author info from users
     │  ├─ Links media attachments
     │  └─ Extracts metrics (likes, retweets, replies)
     │
     ├─ Saves to data/likes_data.json
     │
     └─ Displays in paginated interface (15 per page)
```

## Rate Limiting Strategy

```
API Limit: 75 requests per 15 minutes
Minimum Interval: 1 second between requests

Application Behavior:
│
├─ Before each request:
│  ├─ Check if rate_limit_remaining <= 0
│  │  └─ If yes: wait until rate_limit_reset time
│  │
│  ├─ Check time since last request
│  │  └─ If < 1 second: wait (1 second - elapsed)
│  │
│  └─ Make the request
│
├─ After each request:
│  ├─ Read x-rate-limit-remaining header
│  └─ Update rate_limit_remaining counter
│
└─ If rate limit exceeded:
   └─ Display user-friendly message
      └─ Suggest waiting or manually retrying later
```

## Pagination Logic (Code Flow)

```python
next_token = None
all_tweets = []

while True:
    # Build parameters
    params = {
        'max_results': 100,
        'tweet.fields': '...',
        'expansions': '...',
        ...
        'pagination_token': next_token  # Add if not None
    }
    
    # Make request
    response = make_request('/users/{id}/liked_tweets', params)
    
    # No more data
    if 'data' not in response:
        break
    
    # Collect tweets
    all_tweets.extend(response['data'])
    
    # Check for next page
    if 'meta' in response and 'next_token' in response['meta']:
        next_token = response['meta']['next_token']
    else:
        break  # No more pages
```

## Data Model

### Tweet Object (Processed)
```json
{
  "sequence_number": 1,
  "tweet_id": "1234567890",
  "text": "Post content...",
  "created_at": "2023-01-15T20:15:30.000Z",
  "author": {
    "id": "987654321",
    "name": "Author Name",
    "username": "authorhandle",
    "verified": true
  },
  "media": [
    {
      "type": "photo",
      "url": "https://pbs.twimg.com/...",
      "preview_image_url": null
    }
  ],
  "metrics": {
    "like_count": 150,
    "retweet_count": 30,
    "reply_count": 5
  }
}
```

## API Response Example

### Request
```
GET /2/users/123456/liked_tweets?max_results=100&tweet.fields=created_at,author_id,public_metrics&expansions=author_id,attachments.media_keys&user.fields=username,name,verified&media.fields=type,url,preview_image_url
Authorization: Bearer ACCESS_TOKEN
```

### Response
```json
{
  "data": [
    {
      "id": "1234567890",
      "text": "Awesome post!",
      "created_at": "2023-01-15T20:15:30.000Z",
      "author_id": "987654321",
      "attachments": {
        "media_keys": ["7_1234567890123456789"]
      },
      "public_metrics": {
        "like_count": 150,
        "retweet_count": 30,
        "reply_count": 5,
        "bookmark_count": 10
      }
    }
  ],
  "includes": {
    "users": [
      {
        "id": "987654321",
        "name": "Author Name",
        "username": "authorhandle",
        "verified": true
      }
    ],
    "media": [
      {
        "media_key": "7_1234567890123456789",
        "type": "photo",
        "url": "https://pbs.twimg.com/media/...",
        "preview_image_url": null
      }
    ]
  },
  "meta": {
    "result_count": 1,
    "next_token": "b26v89c19zqg8o3fpza4y3a7u4kqq4o3zqa33a5za11a7q"
  }
}
```

## Field Expansion & Query Parameters

### Tweet Fields
- `created_at` - Creation timestamp
- `author_id` - ID of the tweet author
- `public_metrics` - Like/RT/reply counts

### Expansions
- `author_id` - Include author object in response
- `attachments.media_keys` - Include media keys for fetching media data

### User Fields
- `username` - Twitter handle
- `name` - Display name
- `verified` - Verification status

### Media Fields
- `type` - photo, video, or animated_gif
- `url` - Direct URL to media
- `preview_image_url` - Thumbnail for videos

## Error Handling

```
┌─ Request Error
│  ├─ 401 Unauthorized → Token expired or invalid
│  ├─ 429 Rate Limited → Wait for x-rate-limit-reset
│  ├─ 404 Not Found → Resource doesn't exist
│  ├─ Timeout → Network issue, retry later
│  └─ Other → Log and continue
│
└─ Response Issues
   ├─ No 'data' field → End pagination
   └─ Missing 'includes' → Use empty defaults
```

## Storage & Persistence

```
File: data/likes_data.json

Structure:
{
  "timestamp": "2024-03-19T10:30:00.000000",
  "total_tweets": 42,
  "tweets": [
    { tweet1... },
    { tweet2... },
    ...
  ]
}

Benefits:
├─ Avoid repeated API calls
├─ Instant page loads
├─ Work around rate limits
└─ Allow offline browsing
```

---

This document illustrates how the application handles X API authentication, pagination, rate limiting, and data processing.
