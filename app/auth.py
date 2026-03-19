"""OAuth 2.0 authentication logic for X API."""

import os
import secrets
import hashlib
import base64
import requests
from urllib.parse import urlencode, parse_qs
from typing import Optional, Dict, Any


class XAuthManager:
    """Manages OAuth 2.0 authentication with X API."""
    
    def __init__(self):
        """Initialize the authentication manager."""
        self.client_id = os.getenv('X_CLIENT_ID')
        self.client_secret = os.getenv('X_CLIENT_SECRET')
        self.redirect_uri = os.getenv('REDIRECT_URI')
        self.auth_url = 'https://twitter.com/i/oauth2/authorize'
        self.token_url = 'https://api.twitter.com/2/oauth2/token'
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError('Missing required OAuth environment variables')
    
    @staticmethod
    def generate_pkce():
        """Generate PKCE code challenge and verifier.
        
        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
        code_verifier = code_verifier.replace('=', '')
        
        code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
        code_challenge = code_challenge.replace('=', '')
        
        return code_verifier, code_challenge
    
    def get_authorization_url(self, state: str) -> tuple:
        """Generate authorization URL with PKCE.
        
        Args:
            state: Random state value for CSRF protection
            
        Returns:
            Tuple of (authorization_url, code_verifier)
        """
        code_verifier, code_challenge = self.generate_pkce()
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'tweet.read users.read offline.access',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
        }
        
        authorization_url = f"{self.auth_url}?{urlencode(params)}"
        return authorization_url, code_verifier
    
    def exchange_code_for_token(self, code: str, code_verifier: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token.
        
        Args:
            code: Authorization code from X
            code_verifier: PKCE code verifier
            
        Returns:
            Token response dictionary or None if error
        """
        try:
            payload = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'code_verifier': code_verifier,
                'client_secret': self.client_secret,
            }
            
            response = requests.post(self.token_url, data=payload, timeout=10)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f'Error exchanging code for token: {e}')
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh an expired access token.
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            New token response or None if error
        """
        try:
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
            
            response = requests.post(self.token_url, data=payload, timeout=10)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f'Error refreshing token: {e}')
            return None
