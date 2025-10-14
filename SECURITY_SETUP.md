# 🔒 Security Setup Guide

## ⚠️ IMPORTANT: Never Commit Credentials!

This bot requires sensitive credentials that should **NEVER** be committed to git or shared publicly.

---

## 📋 Initial Setup

### 1. Create Configuration File

Copy the example configuration file:

```bash
cp .env.example config.py
```

### 2. Edit Configuration

Open `config.py` and fill in your credentials:

```bash
nano config.py
# or
vim config.py
# or use any text editor
```

### 3. Verify .gitignore

Make sure `config.py` is in `.gitignore` (it should be by default):

```bash
grep "config.py" .gitignore
```

If not present, add it:

```bash
echo "config.py" >> .gitignore
```

---

## 🔑 Required Credentials

### Telegram Bot Token

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the token and paste it in `config.py`:

```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### Telegram API Credentials

1. Visit https://my.telegram.org
2. Login with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy API ID and API Hash:

```python
TELEGRAM_API = 1234567
TELEGRAM_HASH = "abcdef1234567890abcdef1234567890"
```

### Owner ID

1. Open [@userinfobot](https://t.me/userinfobot) on Telegram
2. Send any message
3. Copy your user ID:

```python
OWNER_ID = 123456789
```

---

## 🗄️ Database Setup (Optional but Recommended)

### MongoDB Atlas (Free Tier)

1. Visit https://www.mongodb.com/cloud/atlas
2. Create a free account
3. Create a new cluster (M0 Free tier)
4. Create a database user:
   - Click "Database Access"
   - Add new database user
   - Choose password authentication
   - **Use a strong password!**
5. Whitelist your IP:
   - Click "Network Access"
   - Add IP Address
   - Allow access from anywhere: `0.0.0.0/0` (for cloud deployments)
6. Get connection string:
   - Click "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database password

```python
DATABASE_URL = "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
```

---

## 📁 Cookie Management for yt-dlp

### Why Cookies Are Needed

Many sites (YouTube, Instagram, etc.) require authentication or have bot protection. Cookies allow the bot to bypass these restrictions.

### Cookie Setup

#### Option 1: User-Specific Cookies (Recommended)

Create a `cookies` directory and add user-specific cookie files:

```bash
mkdir -p cookies
```

Add cookies for specific users:
```
cookies/123456789.txt  # Cookie file for user ID 123456789
cookies/987654321.txt  # Cookie file for user ID 987654321
```

#### Option 2: Global Cookies

Place a single `cookies.txt` file in the root directory:

```bash
# This will be used for all users
cookies.txt
```

### How to Get Cookies

#### Method 1: Browser Extension (Recommended)

1. Install "Get cookies.txt LOCALLY" extension:
   - Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
   - Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

2. Login to the website (YouTube, Instagram, etc.)

3. Click the extension icon and export cookies

4. Save as `cookies.txt` or `cookies/{user_id}.txt`

#### Method 2: yt-dlp Built-in

```bash
yt-dlp --cookies-from-browser chrome --cookies cookies.txt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Cookie Security

⚠️ **IMPORTANT**: Cookies contain authentication tokens!

- **NEVER** commit cookies to git (already in `.gitignore`)
- **NEVER** share cookie files publicly
- Cookies expire after 1-7 days (varies by site)
- Use incognito/private mode cookies for shorter expiry
- Regenerate cookies regularly

### Cookie Validation

The bot now automatically:
- ✅ Checks if cookie file exists
- ✅ Validates cookie file is not empty
- ✅ Falls back to global cookies if user cookies not found
- ✅ Downloads without cookies if none available
- ✅ Logs warnings when cookies are missing

---

## 🔐 Google Drive Setup (Optional)

### Service Accounts (Recommended for heavy usage)

1. Create a Google Cloud Project
2. Enable Google Drive API
3. Create service accounts (up to 100)
4. Download JSON key files
5. Place in `accounts/` directory:

```bash
mkdir -p accounts
# Add your service account JSON files here
accounts/sa_001.json
accounts/sa_002.json
...
```

6. Enable in config:

```python
USE_SERVICE_ACCOUNTS = True
```

### OAuth Credentials

1. Create OAuth 2.0 credentials in Google Cloud Console
2. Download `credentials.json`
3. Run the bot once to generate `token.pickle`

---

## 🌐 Rclone Setup (Optional)

### Configuration

1. Install rclone locally
2. Run `rclone config` to set up remotes
3. Copy `~/.config/rclone/rclone.conf` to bot directory:

```bash
cp ~/.config/rclone/rclone.conf ./rclone.conf
```

4. Configure in `config.py`:

```python
RCLONE_PATH = "remote:folder"
RCLONE_FLAGS = "--buffer-size=64M --transfers=4"
```

---

## 🔒 Security Best Practices

### 1. Use Strong Passwords

- Database passwords: minimum 16 characters, mixed case, numbers, symbols
- JDownloader passwords: minimum 12 characters
- Rclone serve passwords: minimum 12 characters

### 2. Restrict Access

```python
# Only allow specific users
SUDO_USERS = "123456789 987654321"

# Only allow specific chats
AUTHORIZED_CHATS = "-1001234567890"
```

### 3. Enable Web Pincode

```python
WEB_PINCODE = True
```

### 4. Use HTTPS for BASE_URL

```python
BASE_URL = "https://your-domain.com"
```

### 5. Regular Updates

```bash
git pull
pip install -r requirements.txt --upgrade
```

### 6. Monitor Logs

```bash
tail -f log.txt
```

### 7. Rotate Credentials Regularly

- Change bot token every 3-6 months
- Regenerate service accounts yearly
- Update cookies weekly

---

## 🚨 What to Do If Credentials Are Exposed

### 1. Immediately Revoke Compromised Credentials

- **Bot Token**: Use @BotFather to revoke and generate new token
- **Database**: Change database password in MongoDB Atlas
- **Google Drive**: Revoke service accounts in Google Cloud Console
- **Rclone**: Regenerate OAuth tokens

### 2. Remove from Git History

If you accidentally committed credentials:

```bash
# Install BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# Remove config.py from all commits
bfg --delete-files config.py

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (⚠️ WARNING: This rewrites history!)
git push --force
```

### 3. Notify Users

If credentials were public, notify all users to:
- Change their passwords
- Revoke access to the bot
- Monitor for suspicious activity

---

## ✅ Security Checklist

Before deploying:

- [ ] `config.py` is in `.gitignore`
- [ ] No credentials in any committed files
- [ ] Strong passwords for all services
- [ ] Access restricted to authorized users only
- [ ] HTTPS enabled for web interface
- [ ] Cookies stored securely
- [ ] Service accounts properly configured
- [ ] Regular backup schedule established
- [ ] Monitoring and logging enabled
- [ ] Update schedule planned

---

## 📞 Support

If you have security concerns or found a vulnerability:

1. **DO NOT** open a public issue
2. Contact the repository owner privately
3. Provide details about the vulnerability
4. Wait for a fix before disclosing publicly

---

## 📚 Additional Resources

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [MongoDB Security Checklist](https://docs.mongodb.com/manual/administration/security-checklist/)
- [Google Drive API Security](https://developers.google.com/drive/api/guides/security)
- [Rclone Security](https://rclone.org/docs/#security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Remember: Security is not a one-time setup, it's an ongoing process!** 🔒

