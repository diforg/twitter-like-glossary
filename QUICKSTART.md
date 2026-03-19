# Quick Start Guide

Get your Twitter Likes Archive running in 5 minutes!

## Prerequisites
- Docker & Docker Compose installed
- X (Twitter) Developer Account

## 1️⃣ Get Your X API Credentials (2 minutes)

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Click on your app in the "Development Apps" section
3. Go to "Keys and tokens"
4. Copy:
   - **API Key** → This is your `X_CLIENT_ID`
   - **API Key Secret** → This is your `X_CLIENT_SECRET`

5. Go to "App Settings" 
6. Scroll to "Authentication settings"
7. Click "Edit"
8. Set **OAuth 2.0 Redirect URLs** to: `http://localhost:5000/callback`
9. Save

## 2️⃣ Configure Environment Variables (1 minute)

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
# X_CLIENT_ID=your_client_id_from_step_1
# X_CLIENT_SECRET=your_client_secret_from_step_1
```

## 3️⃣ Start the Application (1 minute)

```bash
docker-compose up --build
```

Wait for the message: `Running on http://0.0.0.0:5000`

## 4️⃣ Access the Application (1 minute)

1. Open http://localhost:5000 in your browser
2. Click "Login with X"
3. Grant permission
4. Click "Refresh Likes"
5. Wait while tweets are fetched
6. Start browsing your likes! 📚

---

## 📚 Full Guide

See [README.md](README.md) for detailed documentation, troubleshooting, and advanced configuration.

## ⚡ Common Commands

```bash
# Start (background)
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f app

# Restart
docker-compose restart

# Rebuild after code changes
docker-compose up --build
```

## 🆘 Troubleshooting

**Port already in use?**
```bash
# Edit docker-compose.yml and change:
# "5000:5000" to "5001:5000"
# Then access http://localhost:5001
```

**Credentials not working?**
- Ensure OAuth 2.0 is enabled for your app
- Verify redirect URI is set to `http://localhost:5000/callback`
- Check your credentials are copied correctly

**Still stuck?**
See the Troubleshooting section in [README.md](README.md)

---

Happy archiving! 🎉
