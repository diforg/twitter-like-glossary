# Application User Flow & Features Guide

## 🎯 User Journey Map

```
START
  │
  ├─→ User opens http://localhost:5000
  │   │
  │   └─→ Not logged in?
  │       │
  │       └─→ LOGIN PAGE (index.html)
  │           │
  │           ├─ "📚 Likes Archive" title
  │           ├─ "Login with X" button
  │           ├─ Security information
  │           │
  │           └─→ Click "Login with X"
  │               │
  │               └─→ OAUTH FLOW (auth.py)
  │                   │
  │                   ├─ Generate PKCE
  │                   ├─ Redirect to X authorize
  │                   ├─ User grants permission
  │                   ├─ X redirects to /callback
  │                   ├─ Exchange code for token
  │                   └─ Store token in session
  │
  └─→ Logged in?
      │
      └─→ LIKES PAGE (likes.html)
          │
          ├─ Status indicator
          │ ├─ Total likes count
          │ └─ Last updated timestamp
          │
          ├─ "Refresh Likes" button
          │ │
          │ └─→ Click "Refresh Likes"
          │     │
          │     └─→ FETCH & PROCESS (x_client.py)
          │         │
          │         ├─ Get user ID
          │         ├─ Pagination loop:
          │         │  ├─ Fetch 100 likes
          │         │  ├─ Respect rate limit
          │         │  ├─ Check for next_token
          │         │  └─ Continue until done
          │         │
          │         ├─ Process tweets:
          │         │  ├─ Assign sequence numbers
          │         │  ├─ Enrich with author info
          │         │  ├─ Extract media URLs
          │         │  └─ Get engagement metrics
          │         │
          │         └─ Save to data/likes_data.json
          │             │
          │             └─→ Reload page
          │
          ├─ Tweet Cards (15 per page)
          │ │
          │ └─→ For each tweet:
          │     │
          │     ├─ [1] Sequential number badge
          │     ├─ Author name (linked)
          │     ├─ ✓ Verified badge (if verified)
          │     ├─ @username
          │     ├─ Created date
          │     ├─ Tweet text
          │     ├─ Media images/thumbnails
          │     ├─ ❤️ 150 | 🔄 30 | 💬 5
          │     └─ → (link to tweet on X)
          │
          ├─ Pagination
          │ │
          │ ├─ Page indicator: "Page 1 of 5"
          │ ├─ ← Previous (disabled on page 1)
          │ └─ Next → (disabled on last page)
          │
          └─→ Navigation Bar
              ├─ "My Likes" link
              ├─ "Refresh" link
              └─ "Logout" link
                  │
                  └─→ Clear session & return to login
```

## 📱 Interface Components

### Login Page (index.html)
```
┌─────────────────────────────────┐
│  📚 Likes Archive               │
├─────────────────────────────────┤
│                                 │
│  Archive and browse all your    │
│  liked tweets in one place.     │
│                                 │
│  ┌─────────────────────────────┐│
│  │ 🔗 Login with X             ││
│  └─────────────────────────────┘│
│                                 │
│  This app uses OAuth 2.0 to     │
│  securely authenticate with X.  │
│  Your credentials are never     │
│  stored.                        │
└─────────────────────────────────┘
```

### Likes Page (likes.html)
```
┌─────────────────────────────────────────────────────────────┐
│ 📚 NAVBAR: [My Likes] [Refresh] [Logout]                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Your Liked Tweets                                           │
│ ┌──────────────────────────────────┬──────────────────┐    │
│ │ Total Likes: 42                  │ 🔄 Refresh Likes │    │
│ │ Last updated: 2024-03-19 10:30   └──────────────────┘    │
│ └──────────────────────────────────────────────────────────┘│
│                                                             │
│ TWEET CARD:                                                 │
│ ┌───────────────────────────────────────────────────────┐  │
│ │  ┌───┐                                              → │  │
│ │  │ 1 │  Author Name  ✓                    2024-01-15 │  │
│ │  └───┘  @authorhandle                                │  │
│ │                                                       │  │
│ │  This is an awesome tweet! Check out my latest       │  │
│ │  project. Really excited about it.                   │  │
│ │                                                       │  │
│ │  ┌─────────────────────────────────────────────────┐ │  │
│ │  │ [Image or Video Thumbnail]                      │ │  │
│ │  └─────────────────────────────────────────────────┘ │  │
│ │                                                       │  │
│ │  ❤️ 150    🔄 30    💬 5                             │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                             │
│ [TWEET CARD 2]  [TWEET CARD 3] ... [TWEET CARD 15]        │
│                                                             │
│ Pagination:                                                 │
│ ┌─────────────┬───────────────┬─────────────┐              │
│ │ ← Previous  │ Page 2 of 5    │ Next →      │              │
│ └─────────────┴───────────────┴─────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## 🎨 Color Scheme

| Element | Color | RGB |
|---------|-------|-----|
| Background | Dark Gray | 15, 20, 25 |
| Secondary BG | Darker Gray | 25, 39, 52 |
| Primary Text | Light Gray | 225, 232, 237 |
| Muted Text | Medium Gray | 113, 118, 123 |
| Primary Accent | Twitter Blue | 29, 161, 242 |
| Verified Badge | Twitter Blue | 29, 161, 242 |
| Hover Effect | Subtle White Overlay | rgba(255,255,255,0.05) |

## 🔄 Data Flow Diagram

```
┌──────────────┐
│  User Login  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  OAuth PKCE Flow     │
│ (X Authorization)    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────┐
│  Access Token    │
│  In Session      │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────┐
│ X API Client             │
│ GET /users/me            │ ← Get user ID
│ GET /users/{id}/likes    │ ← Fetch pages with pagination
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Process & Enrich Tweets      │
│ • Add sequence numbers       │
│ • Merge author info          │
│ • Extract media URLs         │
│ • Collect metrics            │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Save to JSON                 │
│ data/likes_data.json         │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Render Paginated HTML        │
│ 15 tweets per page           │
│ Bootstrap + Dark Theme       │
└──────────────────────────────┘
```

## 🌐 Routing Structure

```
/                           GET  Home page (login or redirect)
├─ Not logged in
│  └─ Show: index.html (login page)
│
├─ Logged in
│  └─ Redirect to /likes
│
/login                      GET  Initiate OAuth flow
│  ├─ Generate PKCE code_challenge
│  ├─ Generate state (CSRF protection)
│  └─ Redirect to X authorize URL
│
/callback                   GET  OAuth callback from X
│  ├─ Verify state parameter
│  ├─ Exchange code for access_token
│  ├─ Store token in session
│  └─ Redirect to /likes
│
/likes                      GET  Display likes (paginated)
│  ├─ Load data/likes_data.json
│  ├─ Paginate: 15 tweets per page
│  ├─ Render: likes.html with page data
│  └─ Show: Tweet cards with pagination controls
│
/refresh-likes              GET  Fetch fresh likes from X
│  ├─ Get user ID from API
│  ├─ Fetch all liked tweets (with pagination)
│  ├─ Process and enrich data
│  ├─ Save to data/likes_data.json
│  └─ Redirect to /likes
│
/logout                     GET  Clear session and logout
│  ├─ session.clear()
│  └─ Redirect to /
│
/api/likes/status           GET  JSON status endpoint
│  └─ Returns: {
│       "has_data": boolean,
│       "total_tweets": number,
│       "last_updated": timestamp
│     }
```

## ⚙️ Rate Limiting Behavior

```
Timeline: ← 15 minutes = 1 window →

Request 1:  ✓  (75 remaining)
Request 2:  ✓  (74 remaining)
...
Request 75: ✓  (1 remaining)
Request 76: ⏳ Wait until window resets (15 min)
            ✓  (75 remaining, new window)
```

## 📊 JSON Data Structure

### File: data/likes_data.json
```json
{
  "timestamp": "2024-03-19T10:30:45.123456",
  "total_tweets": 42,
  "tweets": [
    {
      "sequence_number": 1,          ← Oldest = 1
      "tweet_id": "1234567890",
      "text": "Tweet content...",
      "created_at": "2023-01-15T...",
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
    },
    { ... }  ← More tweets
  ]
}
```

## 🔐 Session Management

```
Session Storage (Browser):
├─ access_token        ← X API token (expires after ~2 hours)
├─ refresh_token       ← Used to get new access_token
├─ token_expires_in    ← Expiration time in seconds
├─ oauth_state         ← CSRF token for OAuth
└─ code_verifier       ← PKCE verifier

Session Cookie Settings:
├─ HttpOnly: true      ← Cannot access from JavaScript
├─ SameSite: Lax       ← CSRF protection
└─ Secure: false (dev) / true (prod)
```

## 🚀 Performance Characteristics

### First Load (Fetch Likes)
```
Time depends on:
• Number of likes: 100 = ~1 min, 1000 = ~10 min
• Network speed: 1-5 seconds per request
• X API response time: 0.5-2 seconds per request

Example Timeline:
1. Click "Refresh" → 0 sec
2. Fetch page 1 (100 likes) → 2 sec
3. Fetch page 2 (100 likes) → 2 sec
4. ...
5. Process & save → 1 sec
6. Reload page → 0.5 sec
Total: ~10-15 seconds per 100 likes
```

### Subsequent Loads (From Cache)
```
Load page → Load JSON → Paginate → Render
         0.1 sec    0.1 sec    0.1 sec    0.5 sec
         ↓          ↓          ↓          ↓
        Total: ~0.8 seconds (near instant)
```

## 📋 Feature Checklist

- ✅ OAuth 2.0 with PKCE
- ✅ Like collection with pagination
- ✅ Sequential numbering (oldest = 1)
- ✅ Author information & verification badges
- ✅ Media display (photos & thumbnails)
- ✅ Engagement metrics
- ✅ Rate limit handling
- ✅ JSON persistence
- ✅ Paginated web interface (15 per page)
- ✅ Dark theme design
- ✅ Responsive layout
- ✅ Error handling
- ✅ Docker ready
- ✅ Comprehensive documentation

---

This document provides a complete visual and structural overview of the application's user experience and data flow.
