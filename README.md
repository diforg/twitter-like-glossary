# Twitter Likes Archive

A complete Python system for archiving and browsing all your liked tweets from X (formerly Twitter) with a beautiful paginated web interface.

## Features

✨ **Complete OAuth 2.0 Authentication** - Secure login using X API with PKCE flow
🔄 **Automatic Like Collection** - Fetch all your liked tweets with automatic pagination handling
💾 **Local JSON Storage** - Save tweets locally to minimize API calls
📱 **Responsive Web Interface** - Beautiful dark-themed interface inspired by X
📑 **Paginated Display** - Browse 15 likes per page with sequential numbering
🏷️ **Sequential Numbering** - Tweets numbered from oldest (1) to newest
📸 **Media Support** - Display images and video thumbnails from liked posts
⚡ **Rate Limiting** - Intelligent rate limit handling (75 requests per 15 minutes)
🐳 **Docker Ready** - Complete Docker and Docker Compose setup

## System Architecture

```
likes-archive/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── main.py               # Route handlers and logic
│   ├── auth.py               # OAuth 2.0 PKCE authentication
│   ├── x_client.py           # X API client with pagination
│   └── templates/
│       ├── base.html         # Base template with styling
│       ├── index.html        # Login page
│       └── likes.html        # Likes display page
├── data/                     # JSON storage for tweets (created at runtime)
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker container definition
├── docker-compose.yml       # Docker Compose configuration
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.11+ with pip
- X (Twitter) Developer Account with API access

## Step 1: Create an X Developer Application

1. Go to [X Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Sign in or create a developer account
3. Create a new application or select an existing one
4. Go to the application's "Keys and tokens" section
5. Under "Authentication Tokens & Keys", find:
   - **API Key** (Client ID)
   - **API Secret Key** (Client Secret)
6. Go to "App Settings" and scroll to "Authentication settings"
7. Enable **OAuth 2.0** for your app
8. Set the following:
   - **OAuth 2.0 Redirect URLs**: `http://localhost:5000/callback`
   - **Website URL**: `http://localhost:5000`
   - **Terms of Service URL**: (your URL or any valid URL)
   - **Privacy Policy URL**: (your URL or any valid URL)
9. Save the changes
10. Copy your **Client ID** and **Client Secret**

### Important Notes for OAuth 2.0:
- Your app must have "Read" permissions for tweets
- The OAuth 2.0 app type must be selected
- Redirect URI must be set in the X app settings
- Keep your Client Secret safe and never commit it to version control

## Step 2: Setup Environment Variables

1. Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

2. Edit `.env` and add your credentials:

```bash
# X API Credentials (from Step 1)
X_CLIENT_ID=your_client_id_here
X_CLIENT_SECRET=your_client_secret_here

# OAuth Redirect URI (must match X app configuration)
REDIRECT_URI=http://localhost:5000/callback

# Flask Configuration
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=generate_a_random_secret_key_here
```

**To generate a secure SECRET_KEY**, run:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Run with Docker Compose (Recommended)

The easiest way to run the application:

```bash
# Build and start the application
docker-compose up --build

# Access the application at http://localhost:5000
```

The application will:
- Start a Flask server on port 5000
- Create a persistent `data/` volume for storing tweets
- Automatically handle all dependencies

### Docker Compose Commands

```bash
# Start the application
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f app

# Rebuild after code changes
docker-compose up --build
```

## Step 4: Manual Setup (Without Docker)

If you prefer to run without Docker:

```bash
# 1. Create a Python virtual environment
python3.11 -m venv venv

# 2. Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python run.py

# 5. Access at http://localhost:5000
```

## How to Use

### 1. Login with X

1. Open http://localhost:5000 in your browser
2. Click "Login with X"
3. You'll be redirected to X for authorization
4. Grant permission to the application
5. You'll be redirected back to the application

### 2. View and Refresh Likes

1. After login, you'll see your likes archive
2. Initially, there will be no tweets loaded
3. Click the **"Refresh Likes"** button to fetch your likes from X
4. The first fetch may take a few minutes depending on how many likes you have
5. Tweets are saved locally in `data/likes_data.json` to avoid repeated API calls

### 3. Browse Your Likes

- **Sequential Numbers**: Each like is numbered from oldest (1) to newest
- **Author Information**: See the author's name, handle, and verified status
- **Post Date**: View when each post was created
- **Content**: Read the full post text
- **Media**: View images and video thumbnails
- **Metrics**: See like, retweet, and reply counts
- **Direct Link**: Click the arrow to open the post on X

### 4. Pagination

- Tweets are displayed 15 per page
- Use "Previous" and "Next" buttons to navigate
- Page indicator shows your current position

## API Details

### Endpoints

- `GET /` - Login page
- `GET /login` - Initiate OAuth login
- `GET /callback` - OAuth callback handler (redirected by X)
- `GET /likes` - Display paginated likes
- `GET /refresh-likes` - Fetch fresh likes from X API
- `GET /logout` - Clear session and logout
- `GET /api/likes/status` - Get status of likes data (JSON)

### Rate Limiting

The application implements intelligent rate limiting:
- **API Limit**: 75 requests per 15 minutes
- **Minimum Interval**: 1 second between requests
- **Auto-Throttling**: Automatically waits if approaching rate limit
- **Error Handling**: Gracefully handles rate limit errors

## Data Storage

### JSON Format

Tweets are stored in `data/likes_data.json` with the following structure:

```json
{
  "timestamp": "2024-03-19T10:30:00.000000",
  "total_tweets": 42,
  "tweets": [
    {
      "sequence_number": 1,
      "tweet_id": "123456789",
      "text": "Post content here...",
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
  ]
}
```

### Persistence

- Tweets are saved locally in `data/likes_data.json`
- The JSON file persists across application restarts
- You can manually delete the file to start fresh
- Docker volume keeps data even when containers are removed

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `X_CLIENT_ID` | X API Client ID | `your_client_id` |
| `X_CLIENT_SECRET` | X API Client Secret | `your_client_secret` |
| `REDIRECT_URI` | OAuth callback URL | `http://localhost:5000/callback` |
| `FLASK_ENV` | Flask environment | `development` or `production` |
| `FLASK_HOST` | Flask server host | `0.0.0.0` |
| `FLASK_PORT` | Flask server port | `5000` |
| `SECRET_KEY` | Flask session secret key | Random string |
| `SESSION_COOKIE_SECURE` | Use secure cookies | `false` (dev), `true` (prod) |
| `SESSION_COOKIE_HTTPONLY` | HTTP-only cookies | `true` |
| `SESSION_COOKIE_SAMESITE` | SameSite policy | `Lax` |

## Troubleshooting

### "Unauthorized" Error on Refresh
- **Issue**: Token expired or invalid
- **Solution**: Logout and login again to refresh your authentication

### "Rate limit exceeded" Message
- **Issue**: Made too many API requests
- **Solution**: Wait 15 minutes or manually edit `data/likes_data.json` to avoid re-fetching

### No tweets appear after refresh
- **Issue**: No likes in your account or API returned no data
- **Solution**: Check if you have any likes on X; try refreshing again

### Port 5000 already in use
- **Docker**: Change port in `docker-compose.yml`: `"5001:5000"`
- **Manual**: Change `FLASK_PORT` in `.env` file

### Connection refused
- **Issue**: Application not running
- **Solution**: Ensure Docker Compose is running: `docker-compose up`

### Environment variables not loading
- **Issue**: `.env` file not found or not being read
- **Solution**: Make sure `.env` is in the project root directory and restart the application

## Development

### Project Structure
- **app/__init__.py** - Flask app factory with configuration
- **app/main.py** - Route handlers and business logic
- **app/auth.py** - OAuth 2.0 PKCE authentication flow
- **app/x_client.py** - X API client with rate limiting and pagination
- **app/templates/** - Jinja2 HTML templates with Bootstrap 5 styling

### Key Classes

#### XAuthManager (auth.py)
Handles OAuth 2.0 authentication:
- `generate_pkce()` - Generate PKCE code challenge and verifier
- `get_authorization_url()` - Get X authorization URL
- `exchange_code_for_token()` - Exchange auth code for access token
- `refresh_access_token()` - Refresh expired tokens

#### XAPIClient (x_client.py)
Handles X API interactions:
- `get_user_id()` - Get authenticated user's ID
- `get_liked_tweets()` - Fetch a page of liked tweets
- `fetch_all_liked_tweets()` - Generator for pagination
- `process_liked_tweets()` - Process and save all tweets

### Modifying the Application

To add features or modify behavior:

1. **Add new routes** in `app/main.py`
2. **Modify styling** in `app/templates/base.html`
3. **Change API calls** in `app/x_client.py`
4. **Update environment** variables in `.env.example`
5. **Rebuild Docker** image: `docker-compose up --build`

## Security Considerations

- **Client Secret**: Never commit `.env` to version control (already in `.gitignore`)
- **HTTPS**: In production, use HTTPS for secure cookie transmission
- **Session Cookie**: Set `SESSION_COOKIE_SECURE=true` in production
- **Secret Key**: Generate a new random key for production
- **Token Storage**: Tokens are only stored in Flask sessions (not persisted)

## Performance

### Optimization Tips

1. **First fetch** may take a few minutes depending on number of likes
2. **Subsequent visits** load from local JSON (instant)
3. **Large like counts** (1000+) are handled efficiently with pagination
4. **Rate limiting** ensures you stay within API limits
5. **Media** displays are lazy-loaded in the browser

### API Optimization

- Batch requests with `max_results=100`
- Automatic pagination through all likes
- Selective field expansion (only fetch needed data)
- Local caching to minimize API calls

## Production Deployment

For production deployment:

1. **Update .env**:
   ```bash
   FLASK_ENV=production
   SESSION_COOKIE_SECURE=true
   SECRET_KEY=<generate-new-secure-key>
   REDIRECT_URI=https://your-domain.com/callback
   ```

2. **Update X app settings**: Set redirect URI to your production URL

3. **Use a production server** like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
   ```

4. **Use a reverse proxy** like Nginx

5. **Enable HTTPS** with SSL certificates

6. **Use environment secrets** instead of .env files

7. **Monitor logs** and set up alerting

## Contributing

To contribute improvements:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with clear commit messages
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:

1. Check the Troubleshooting section above
2. Review X API documentation: https://developer.twitter.com/en/docs/twitter-api
3. Check Flask documentation: https://flask.palletsprojects.com/

## Changelog

### Version 1.0.0 (Initial Release)
- Complete OAuth 2.0 authentication with PKCE
- Like collection with automatic pagination
- JSON data persistence
- Paginated web interface with 15 likes per page
- Sequential numbering from oldest to newest
- Media support (photos and videos)
- Rate limit handling
- Docker and Docker Compose setup
- Comprehensive documentation

---

**Created:** March 2024

**Happy archiving! 📚**
