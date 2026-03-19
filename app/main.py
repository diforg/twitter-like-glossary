"""Main Flask application with routes and authentication flow."""

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import secrets
import json
import os
from datetime import datetime
from app.auth import XAuthManager
from app.x_client import XAPIClient

main_bp = Blueprint('main', __name__)

auth_manager = XAuthManager()


@main_bp.route('/')
def index():
    """Home page - login or show likes if authenticated."""
    if 'access_token' in session:
        return redirect(url_for('main.likes'))
    
    return render_template('index.html')


@main_bp.route('/login')
def login():
    """Initiate OAuth login flow."""
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    auth_url, code_verifier = auth_manager.get_authorization_url(state)
    session['code_verifier'] = code_verifier
    
    return redirect(auth_url)


@main_bp.route('/callback')
def callback():
    """OAuth callback handler."""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    # Check for errors
    if error:
        return render_template('index.html', error=f'Authorization failed: {error}'), 400
    
    # Verify state
    if state != session.get('oauth_state'):
        return render_template('index.html', error='State mismatch'), 400
    
    if not code:
        return render_template('index.html', error='Missing authorization code'), 400
    
    # Exchange code for token
    code_verifier = session.get('code_verifier')
    token_response = auth_manager.exchange_code_for_token(code, code_verifier)
    
    if not token_response:
        return render_template('index.html', error='Failed to obtain access token'), 400
    
    # Store token in session
    session['access_token'] = token_response.get('access_token')
    session['refresh_token'] = token_response.get('refresh_token')
    session['token_expires_in'] = token_response.get('expires_in')
    
    return redirect(url_for('main.likes'))


@main_bp.route('/logout')
def logout():
    """Logout the user."""
    session.clear()
    return redirect(url_for('main.index'))


@main_bp.route('/likes')
def likes():
    """Display paginated liked tweets."""
    if 'access_token' not in session:
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    
    # Load tweets from JSON file
    tweets_data = load_tweets_data()
    
    if not tweets_data:
        return render_template('likes.html', 
                             tweets=[],
                             page=page,
                             total_pages=0,
                             total_tweets=0,
                             message='No tweets found. Click "Refresh" to fetch your likes.')
    
    # Pagination
    tweets = tweets_data.get('tweets', [])
    per_page = 15
    total_pages = (len(tweets) + per_page - 1) // per_page
    
    # Ensure page is valid
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Get tweets for this page (tweets are sorted oldest first)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_tweets = tweets[start_idx:end_idx]
    
    return render_template('likes.html',
                         tweets=page_tweets,
                         page=page,
                         total_pages=total_pages,
                         total_tweets=len(tweets))


@main_bp.route('/refresh-likes')
def refresh_likes():
    """Fetch fresh likes from X API."""
    if 'access_token' not in session:
        return redirect(url_for('main.index'))
    
    try:
        client = XAPIClient(session['access_token'])
        user_id = client.get_user_id()
        
        if not user_id:
            return render_template('likes.html',
                                 error='Failed to get user ID')
        
        # Get data directory
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        data_file = os.path.join(data_dir, 'likes_data.json')
        
        # Fetch and process tweets
        tweets = client.process_liked_tweets(user_id, data_file)
        
        # Reverse to get newest first for storage, but keep sequence numbers from oldest
        # The process_liked_tweets already assigns sequence numbers correctly (oldest = 1)
        
        return redirect(url_for('main.likes'))
    
    except Exception as e:
        print(f'Error refreshing likes: {e}')
        return render_template('likes.html',
                             error=f'Error fetching likes: {str(e)}')


@main_bp.route('/api/likes/status')
def likes_status():
    """Get status of likes data."""
    tweets_data = load_tweets_data()
    
    if tweets_data:
        return jsonify({
            'has_data': True,
            'total_tweets': tweets_data.get('total_tweets', 0),
            'last_updated': tweets_data.get('timestamp'),
        })
    
    return jsonify({
        'has_data': False,
        'total_tweets': 0,
        'last_updated': None,
    })


def load_tweets_data():
    """Load tweets from JSON file.
    
    Returns:
        Dictionary with tweets data or None
    """
    data_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data',
        'likes_data.json'
    )
    
    if not os.path.exists(data_file):
        return None
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f'Error loading tweets: {e}')
        return None
