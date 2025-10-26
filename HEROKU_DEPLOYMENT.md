# Heroku Deployment Guide - Mirror-Leech Telegram Bot

## ⚠️ Important Compatibility Notes

This bot has several compatibility challenges with Heroku:

### Known Limitations:
1. **Ephemeral Filesystem** - Downloads will be lost on dyno restart (every 24 hours minimum)
2. **Memory Requirements** - Bot needs 1.5-2.5GB RAM for all services
3. **Multiple Background Services** - Aria2c, qBittorrent, SABnzbd, JDownloader run simultaneously
4. **Port Bindings** - Services use fixed ports (6800, 8090, 8070, 8080)
5. **Docker Image Size** - May exceed Heroku's slug size limits

### Recommended Solutions:
- Use **MongoDB** for persistent data (settings, user data, RSS feeds)
- Configure **external storage** for downloads (Google Drive, Rclone)
- Use **Heroku Eco/Basic dynos** minimum ($7/month)
- Consider **upgrading to Standard** ($25/month) for better performance

---

## Prerequisites

1. **Heroku Account** - Sign up at https://heroku.com
2. **Heroku CLI** - Install from https://devcenter.heroku.com/articles/heroku-cli
3. **Git** - Installed and configured
4. **MongoDB Database** - MongoDB Atlas (free tier available)
5. **Telegram Bot Token** - From @BotFather
6. **Telegram API Credentials** - From my.telegram.org

---

## Deployment Methods

### Method 1: Heroku CLI (Recommended)

#### Step 1: Login to Heroku
```bash
heroku login
```

#### Step 2: Create Heroku App
```bash
heroku create your-app-name
```

Or let Heroku generate a name:
```bash
heroku create
```

#### Step 3: Set Stack to Container
```bash
heroku stack:set container -a your-app-name
```

#### Step 4: Add MongoDB (Optional but Recommended)
```bash
# Using MongoDB Atlas (Free)
# Get connection string from https://www.mongodb.com/cloud/atlas
# Then set it as environment variable (see Step 5)
```

#### Step 5: Configure Environment Variables (SKIP - Using config.py)

**Note**: This deployment uses `config.py` file for configuration, NOT environment variables.
The `config.py` file is included in the repository with all your settings.

If you want to override any settings, you can set environment variables:
```bash
heroku config:set BOT_TOKEN=your_token -a your-app-name
heroku config:set OWNER_ID=your_id -a your-app-name
```

But this is **NOT required** since config.py is used.

#### Step 6: Deploy to Heroku
```bash
git push heroku heroku:main
```

Or if you're on the heroku branch:
```bash
git push heroku heroku:master
```

#### Step 7: Scale the Worker Dyno
```bash
heroku ps:scale worker=1 -a your-app-name
```

#### Step 8: Check Logs
```bash
heroku logs --tail -a your-app-name
```

Look for "Bot Started!" message.

---

### Method 2: Heroku Dashboard

#### Step 1: Create New App
1. Go to https://dashboard.heroku.com
2. Click **"New"** → **"Create new app"**
3. Enter app name
4. Choose region (US or Europe)
5. Click **"Create app"**

#### Step 2: Connect GitHub Repository
1. Go to **"Deploy"** tab
2. Select **"GitHub"** as deployment method
3. Connect your GitHub account
4. Search for: `el-pablos/mirror-leech-telegram-bot`
5. Click **"Connect"**

#### Step 3: Select Branch
1. Choose branch: **`heroku`**
2. Enable **"Automatic deploys"** (optional)

#### Step 4: Manual Deploy
1. Scroll to **"Manual deploy"**
2. Select branch: **`heroku`**
3. Click **"Deploy Branch"**

#### Step 5: Configure Dyno
1. Go to **"Resources"** tab
2. Turn OFF **"web"** dyno (if present)
3. Turn ON **"worker"** dyno
4. Click **"Change Dyno Type"**
5. Select **"Eco"** ($7/month) or **"Basic"** ($7/month)
6. Click **"Confirm"**

#### Step 6: Monitor Deployment
1. Go to **"Activity"** tab
2. Watch build progress
3. Go to **"More"** → **"View logs"**
4. Look for "Bot Started!" message

---

### Method 3: Heroku Button (One-Click Deploy)

Click the button below to deploy:

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/el-pablos/mirror-leech-telegram-bot/tree/heroku)

**Note**: This uses the `app.json` configuration file.

---

## Configuration

### Using config.py (Current Setup)

All configuration is in the `config.py` file which is included in the repository:

```python
# REQUIRED CONFIG
BOT_TOKEN = "your_bot_token"
OWNER_ID = your_telegram_id
TELEGRAM_API = your_api_id
TELEGRAM_HASH = "your_api_hash"

# DATABASE (REQUIRED for persistence)
DATABASE_URL = "mongodb+srv://..."

# GOOGLE DRIVE
GDRIVE_ID = "your_drive_id"
IS_TEAM_DRIVE = False
STOP_DUPLICATE = False

# ... and more settings
```

**Security Note**: The config.py file contains your credentials. Make sure your repository is **PRIVATE** or regenerate tokens after deployment.

---

## Post-Deployment Steps

### 1. Verify Bot is Running

Send a message to your bot on Telegram:
```
/start
```

Expected response: Bot should respond with welcome message.

### 2. Check Dyno Status

```bash
heroku ps -a your-app-name
```

Should show:
```
=== worker (Eco): bash start.sh (1)
worker.1: up 2024/10/26 12:34:56 +0000 (~ 1m ago)
```

### 3. Monitor Logs

```bash
heroku logs --tail -a your-app-name
```

Look for:
- "Bot Started!"
- No error messages
- Services starting (Aria2c, qBittorrent, etc.)

### 4. Configure Bot Settings

Use `/bsetting` command in Telegram to configure:
- Download clients
- Upload destinations
- Queue settings
- Private files

### 5. Upload Private Files (if needed)

Use `/bsetting` → Private Files to upload:
- `token.pickle` (Google Drive authentication)
- `rclone.conf` (Rclone configuration)
- `accounts.zip` (Service accounts)
- `.netrc` (Authentication file)
- `cookies.txt` (Browser cookies)

Files are stored in MongoDB, not on dyno filesystem.

---

## Troubleshooting

### Bot Not Starting

**Check Logs:**
```bash
heroku logs --tail -a your-app-name
```

**Common Issues:**
- Invalid BOT_TOKEN in config.py
- Invalid TELEGRAM_API or TELEGRAM_HASH
- MongoDB connection failed
- Docker build failed

**Solutions:**
- Verify config.py has correct values
- Check MongoDB connection string
- Ensure container stack is set: `heroku stack:set container`

### Out of Memory (R14 Error)

**Symptoms:**
```
Error R14 (Memory quota exceeded)
```

**Solutions:**
- Upgrade to **Standard-1X** dyno ($25/month, 512MB RAM)
- Upgrade to **Standard-2X** dyno ($50/month, 1GB RAM) - Recommended
- Reduce concurrent downloads in bot settings
- Lower qBittorrent memory limits

### Dyno Sleeping (H10 Error)

**Symptoms:**
```
Error H10 (App crashed)
```

**Solutions:**
- Check logs for crash reason
- Ensure worker dyno is enabled (not web)
- Verify Docker build completed successfully
- Check all required services started

### Downloads Disappearing

**Symptoms:**
- Files download but disappear
- "File not found" errors

**Cause:**
- Heroku's ephemeral filesystem
- Dyno restarts every 24 hours

**Solutions:**
- Use MongoDB for persistent data (already configured)
- Upload directly to Google Drive (set DEFAULT_UPLOAD=gd)
- Use Rclone for cloud storage
- Don't rely on local filesystem for storage

### Port Binding Issues

**Symptoms:**
- "Address already in use"
- Services fail to start

**Solutions:**
- This is expected on Heroku
- Services will try to bind to fixed ports
- Some services may fail but bot should still work
- Use external services if needed

---

## Resource Requirements

### Minimum Setup (Eco Dyno)
- **Dyno**: Eco ($7/month)
- **RAM**: 512MB (may be insufficient)
- **MongoDB**: Atlas M0 (Free)
- **Total**: ~$7/month
- **Status**: ⚠️ May have performance issues

### Recommended Setup (Standard-2X)
- **Dyno**: Standard-2X ($50/month)
- **RAM**: 1GB
- **MongoDB**: Atlas M0 (Free)
- **Total**: ~$50/month
- **Status**: ✅ Should work reliably

### High Performance (Performance-M)
- **Dyno**: Performance-M ($250/month)
- **RAM**: 2.5GB
- **MongoDB**: Atlas M10 ($57/month)
- **Total**: ~$307/month
- **Status**: ✅ Best performance

**Note**: With GitHub Education credits ($13/month), you can run Eco dyno for free for 24 months.

---

## Heroku CLI Commands Reference

### App Management
```bash
# List apps
heroku apps

# Create app
heroku create app-name

# Delete app
heroku apps:destroy app-name

# Rename app
heroku apps:rename new-name -a old-name
```

### Deployment
```bash
# Deploy
git push heroku heroku:master

# Deploy specific branch
git push heroku branch-name:master

# Rollback
heroku rollback -a app-name
```

### Dyno Management
```bash
# Scale dynos
heroku ps:scale worker=1 -a app-name

# Restart dynos
heroku restart -a app-name

# Stop dynos
heroku ps:scale worker=0 -a app-name

# Check dyno status
heroku ps -a app-name
```

### Logs
```bash
# View logs
heroku logs -a app-name

# Tail logs
heroku logs --tail -a app-name

# View specific number of lines
heroku logs -n 200 -a app-name
```

### Configuration
```bash
# View config vars
heroku config -a app-name

# Set config var
heroku config:set KEY=value -a app-name

# Unset config var
heroku config:unset KEY -a app-name
```

---

## Important Notes

### Ephemeral Filesystem
- Heroku dynos have ephemeral filesystem
- All files are lost on dyno restart (every 24 hours minimum)
- Use MongoDB for persistent data
- Upload files directly to Google Drive or cloud storage

### Dyno Sleeping
- Eco dynos sleep after 30 minutes of inactivity
- Bot will wake up when receiving messages
- Use Basic or higher to prevent sleeping

### Build Time
- Initial deployment takes 10-15 minutes
- Docker image build can be slow
- Subsequent deploys are faster (cached layers)

### Security
- config.py contains sensitive credentials
- Keep repository PRIVATE
- Or use environment variables instead
- Regenerate tokens if repository is public

---

## Support Resources

- **Heroku Documentation**: https://devcenter.heroku.com
- **Heroku Support**: https://help.heroku.com
- **Bot Support Group**: https://t.me/mltb_official_support
- **Bot Support Channel**: https://t.me/mltb_official_channel
- **GitHub Issues**: https://github.com/el-pablos/mirror-leech-telegram-bot/issues

---

## Alternative Platforms

If Heroku doesn't work well, consider:

1. **Render.com** - $7-25/month, Docker-friendly, persistent storage
2. **Railway.app** - $5-20/month, excellent Docker support
3. **DigitalOcean App Platform** - $12-24/month, managed platform
4. **VPS (DigitalOcean/Linode)** - $6-12/month, full control

---

**Status**: Ready for Heroku deployment with config.py configuration.

**Last Updated**: 2025-10-26

