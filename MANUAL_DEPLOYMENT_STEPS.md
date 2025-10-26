# Manual Deployment Steps for Render.com

Since automated deployment requires payment information to be added first, follow these steps to deploy manually.

## Prerequisites

✅ **Payment Method Added**: You must add a credit/debit card at https://dashboard.render.com/billing

---

## Method 1: Blueprint Deployment (EASIEST - RECOMMENDED)

This method uses the pre-configured `render.yaml` file which includes all settings.

### Steps:

1. **Add Payment Information**
   - Visit: https://dashboard.render.com/billing
   - Add your credit/debit card
   - No charges until you deploy

2. **Deploy via Blueprint**
   - Go to: https://dashboard.render.com
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub account if not already connected
   - Select repository: `el-pablos/mirror-leech-telegram-bot`
   - Select branch: **`render`**
   - Render will automatically detect `render.yaml`

3. **Review Configuration**
   - Service name: `mirror-leech-bot`
   - Plan: Standard ($7/month) - **Upgrade to Standard Plus ($25/month) recommended**
   - Region: Oregon
   - All environment variables are pre-filled from `render.yaml`

4. **Customize Environment Variables (IMPORTANT)**
   - The `render.yaml` has placeholder values
   - **You MUST update these with your actual values**:
     - `BOT_TOKEN` - Already set correctly
     - `OWNER_ID` - Already set correctly
     - `TELEGRAM_API` - Already set correctly
     - `TELEGRAM_HASH` - Already set correctly
     - `DATABASE_URL` - Already set correctly
     - `GDRIVE_ID` - Already set correctly
   - All other values are already configured from your `config.py`

5. **Review Disk Configuration**
   - Persistent disk: 10GB
   - Mount path: `/usr/src/app/downloads`
   - This is automatically configured in `render.yaml`

6. **Click "Apply"**
   - Render will create the service
   - Initial deployment takes 5-10 minutes
   - Monitor logs in real-time

7. **Wait for Deployment**
   - Watch the logs for "Bot Started!"
   - Service URL will be provided (though bot doesn't need it)

---

## Method 2: Manual Web Service Creation

If Blueprint doesn't work, create the service manually:

### Steps:

1. **Create New Web Service**
   - Go to: https://dashboard.render.com
   - Click **"New +"** → **"Web Service"**
   - Connect repository: `https://github.com/el-pablos/mirror-leech-telegram-bot`

2. **Configure Basic Settings**
   - **Name**: `mirror-leech-bot`
   - **Region**: Oregon (or closest to you)
   - **Branch**: `render`
   - **Runtime**: Docker (auto-detected)
   - **Dockerfile Path**: `./Dockerfile.render`

3. **Select Plan**
   - **Minimum**: Standard ($7/month, 512MB RAM)
   - **Recommended**: Standard Plus ($25/month, 1GB RAM) ⭐
   - **Best**: Pro ($85/month, 2GB RAM)

4. **Add Environment Variables**
   - Click **"Advanced"** → **"Add Environment Variable"**
   - Copy variables from `render_env_variables.txt` file
   - Add each variable one by one, OR
   - Use "Add from .env" and paste the entire file content

   **Required Variables:**
   ```
   BOT_TOKEN=8024373376:AAEz4GX0D0q1qARO-ym-UE5Z_JQdxw6umBA
   OWNER_ID=5476148500
   TELEGRAM_API=18555351
   TELEGRAM_HASH=9227b60247cb82162d27c33d942088c1
   DATABASE_URL=mongodb+srv://kontol:kontolodon@mirrornich.8ki9rl1.mongodb.net/?retryWrites=true&w=majority&appName=mirrornich
   ```

   **All other variables** are in `render_env_variables.txt`

5. **Configure Persistent Disk**
   - Scroll to **"Disks"** section
   - Click **"Add Disk"**
   - **Name**: `bot-storage`
   - **Mount Path**: `/usr/src/app/downloads`
   - **Size**: 10 GB (increase if needed)

6. **Auto Deploy**
   - Enable **"Auto-Deploy"** (recommended)
   - This will auto-deploy when you push to `render` branch

7. **Create Web Service**
   - Click **"Create Web Service"**
   - Deployment will start automatically

8. **Monitor Deployment**
   - Go to **"Logs"** tab
   - Watch for build progress
   - Look for "Bot Started!" message

---

## Post-Deployment Steps

### 1. Verify Bot is Running

Send a message to your bot on Telegram:
```
/start
```

Expected response: Bot should respond with welcome message

### 2. Check Service Health

- Go to Render Dashboard → Your Service
- Check **"Events"** tab for deployment status
- Check **"Metrics"** tab for resource usage
- Check **"Logs"** tab for any errors

### 3. Configure Bot Settings

Use the `/bsetting` command in Telegram to configure:
- Download clients (aria2, qBittorrent, SABnzbd)
- Upload destinations
- Queue settings
- Private files (token.pickle, rclone.conf, etc.)

### 4. Upload Private Files (if needed)

If you need Google Drive or Rclone:
1. Use `/bsetting` → Private Files
2. Upload required files:
   - `token.pickle` (Google Drive authentication)
   - `rclone.conf` (Rclone configuration)
   - `accounts.zip` (Service accounts)
   - `.netrc` (Authentication file)
   - `cookies.txt` (Browser cookies)

Files are stored in MongoDB, not on disk.

### 5. Test Downloads

Try a small download to verify everything works:
```
/mirror https://example.com/small-file.zip
```

---

## Troubleshooting

### Bot Not Starting

**Check Logs:**
- Go to Render Dashboard → Logs
- Look for error messages

**Common Issues:**
- Invalid BOT_TOKEN
- Invalid TELEGRAM_API or TELEGRAM_HASH
- MongoDB connection failed
- Missing required environment variables

**Solutions:**
- Verify all environment variables are set correctly
- Check MongoDB connection string is valid
- Ensure database is accessible from Render's IP

### Out of Memory

**Symptoms:**
- Service crashes randomly
- "Out of memory" in logs
- Slow performance

**Solutions:**
- Upgrade to Standard Plus (1GB RAM)
- Reduce concurrent downloads in bot settings
- Lower qBittorrent memory limits

### Port Binding Errors

**Symptoms:**
- "Address already in use"
- "Failed to bind to port"

**Solutions:**
- Ensure `Dockerfile.render` is being used
- Check that PORT environment variable is detected
- Review startup logs for port configuration

### Download Failures

**Symptoms:**
- Downloads fail to start
- "No space left on device"
- Files disappear after download

**Solutions:**
- Check persistent disk is mounted correctly
- Verify disk space is available
- Increase disk size if needed

---

## Monitoring and Maintenance

### View Logs
```
Render Dashboard → Your Service → Logs
```

### Check Metrics
```
Render Dashboard → Your Service → Metrics
```
- CPU usage
- Memory usage
- Request count
- Response times

### Restart Service
- Use `/restart` command in bot
- Or click **"Manual Deploy"** → **"Deploy latest commit"**

### Update Bot
- Push changes to `render` branch
- Render auto-deploys (if enabled)
- Or manually trigger deploy

---

## Cost Estimation

### Minimum Setup
- **Render Plan**: Standard ($7/month)
- **Disk**: 10GB (included)
- **MongoDB**: Atlas M0 (Free)
- **Total**: ~$7/month

### Recommended Setup
- **Render Plan**: Standard Plus ($25/month) ⭐
- **Disk**: 20GB (included)
- **MongoDB**: Atlas M0 (Free)
- **Total**: ~$25/month

### High Performance
- **Render Plan**: Pro ($85/month)
- **Disk**: 50GB (included)
- **MongoDB**: Atlas M10 ($57/month)
- **Total**: ~$142/month

---

## Important Notes

### Security
- ⚠️ **Never commit sensitive data** to repository
- ✅ Use environment variables for all credentials
- ✅ Set `AUTHORIZED_CHATS` to restrict bot access
- ✅ Set `SUDO_USERS` for admin access

### Backups
- Export MongoDB data regularly
- Keep backup of environment variables
- Document any custom configurations

### Updates
- Monitor upstream repository for updates
- Test updates in development before production
- Keep dependencies up to date

---

## Support Resources

- **Render Documentation**: https://render.com/docs
- **Bot Support Group**: https://t.me/mltb_official_support
- **Bot Support Channel**: https://t.me/mltb_official_channel
- **GitHub Issues**: https://github.com/el-pablos/mirror-leech-telegram-bot/issues

---

## Quick Reference

### Service Details
- **Repository**: https://github.com/el-pablos/mirror-leech-telegram-bot
- **Branch**: render
- **Dockerfile**: Dockerfile.render
- **Start Script**: start_render.sh
- **Config File**: render.yaml

### Environment Variables File
- **Location**: `render_env_variables.txt`
- **Contains**: All configuration from your `config.py`

### Documentation
- **Quick Start**: README_RENDER.md
- **Full Guide**: RENDER_DEPLOYMENT.md
- **This Guide**: MANUAL_DEPLOYMENT_STEPS.md

---

**Ready to deploy?** Follow Method 1 (Blueprint) for the easiest deployment!

