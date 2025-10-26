# Render.com Deployment Guide

This guide explains how to deploy the Mirror-Leech Telegram Bot to Render.com.

## Prerequisites

1. **Render.com Account**: Sign up at [render.com](https://render.com)
2. **Telegram Bot Token**: Get from [@BotFather](https://t.me/BotFather)
3. **Telegram API Credentials**: Get from [my.telegram.org](https://my.telegram.org)
4. **MongoDB Database**: Use MongoDB Atlas (free tier available) or Render's managed database

## Quick Deploy

### Option 1: Deploy via Render Dashboard

1. **Fork this repository** to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Select the `render` branch
6. Render will detect `render.yaml` and configure services automatically
7. Set required environment variables (see below)
8. Click **"Apply"** to deploy

### Option 2: Deploy via render.yaml

1. Push this `render` branch to your GitHub repository
2. In Render Dashboard, create a new **Web Service**
3. Connect your repository and select the `render` branch
4. Render will auto-detect the Docker configuration
5. Configure environment variables
6. Deploy!

## Required Environment Variables

Set these in the Render Dashboard under **Environment** tab:

### Essential Variables (REQUIRED)

```bash
BOT_TOKEN=your_bot_token_from_botfather
OWNER_ID=your_telegram_user_id
TELEGRAM_API=your_api_id_from_my_telegram_org
TELEGRAM_HASH=your_api_hash_from_my_telegram_org
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/dbname
```

### How to Get These Values

1. **BOT_TOKEN**: 
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` and follow instructions
   - Copy the token provided

2. **OWNER_ID**:
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram
   - Copy your user ID

3. **TELEGRAM_API & TELEGRAM_HASH**:
   - Visit [my.telegram.org](https://my.telegram.org)
   - Login with your phone number
   - Go to "API Development Tools"
   - Create an app and copy API ID and API Hash

4. **DATABASE_URL**:
   - Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a free cluster
   - Get connection string (replace `<password>` with your password)
   - Format: `mongodb+srv://username:password@cluster.mongodb.net/mltb`

## Optional Environment Variables

### Google Drive Integration
```bash
GDRIVE_ID=your_google_drive_folder_id
IS_TEAM_DRIVE=False
INDEX_URL=https://your-index-url.workers.dev
USE_SERVICE_ACCOUNTS=False
STOP_DUPLICATE=False
```

### Rclone Configuration
```bash
RCLONE_PATH=remote:path
RCLONE_FLAGS=--flag1 --flag2
```

### Leech Settings
```bash
LEECH_SPLIT_SIZE=2097152000
AS_DOCUMENT=False
LEECH_DUMP_CHAT=-100xxxxxxxxxx
```

### Authorization
```bash
AUTHORIZED_CHATS=-100xxxxxxxxxx -100yyyyyyyyyy
SUDO_USERS=123456789 987654321
```

## Resource Recommendations

### Render Plan Selection

- **Starter (Free)**: ❌ Not recommended - insufficient resources
- **Standard ($7/month)**: ✅ Minimum recommended - 512MB RAM
- **Standard Plus ($25/month)**: ✅ Recommended - 1GB RAM
- **Pro ($85/month)**: ✅ Best performance - 2GB RAM
- **Pro Plus ($200/month)**: For heavy usage - 4GB RAM

### Disk Space

The `render.yaml` configures a 10GB persistent disk for downloads. Adjust in the YAML file:

```yaml
disk:
  name: bot-storage
  mountPath: /usr/src/app/downloads
  sizeGB: 20  # Increase as needed
```

## Post-Deployment Configuration

### 1. Upload Private Files (Optional)

If you need to upload private files (token.pickle, rclone.conf, etc.):

1. Use the bot's `/bsetting` command
2. Select "Private Files"
3. Upload your files through Telegram

These files will be stored in MongoDB and persist across restarts.

### 2. Configure Bot Settings

Use the `/bsetting` command in Telegram to configure:
- Aria2c options
- qBittorrent settings
- SABnzbd configuration
- Upload destinations

### 3. Set Bot Commands

Message [@BotFather](https://t.me/BotFather):
```
/setcommands
```

Then paste the commands from the main README.md.

## Monitoring and Logs

### View Logs
1. Go to your service in Render Dashboard
2. Click **"Logs"** tab
3. View real-time logs

### Health Checks
Render automatically monitors your service health via the `/` endpoint.

### Restart Service
If needed, click **"Manual Deploy"** → **"Clear build cache & deploy"**

## Troubleshooting

### Bot Not Starting

1. **Check Logs**: Look for error messages in Render logs
2. **Verify Environment Variables**: Ensure all required variables are set
3. **Database Connection**: Test MongoDB connection string
4. **Token Validity**: Verify BOT_TOKEN is correct

### Out of Memory Errors

1. Upgrade to a higher Render plan (Standard Plus or Pro)
2. Reduce concurrent downloads in bot settings
3. Lower qBittorrent memory limits via `/bsetting`

### Download Issues

1. **Check Disk Space**: Ensure persistent disk has enough space
2. **Verify Permissions**: The disk should be mounted at `/usr/src/app/downloads`
3. **Check Logs**: Look for download-related errors

### Port Binding Issues

The code has been modified to automatically use Render's `PORT` environment variable. If you see port-related errors:

1. Check that `BASE_URL_PORT` is not hardcoded
2. Verify the web server starts on the correct port
3. Review startup logs

## Updating the Bot

### Automatic Updates (Recommended)

The bot is configured to auto-update from the `UPSTREAM_REPO`:

```bash
UPSTREAM_REPO=https://github.com/el-pablos/mirror-leech-telegram-bot
UPSTREAM_BRANCH=render
```

On each restart, it will pull the latest changes.

### Manual Update

1. Push changes to your GitHub repository
2. Render will auto-deploy (if `autoDeploy: true`)
3. Or manually trigger deploy in Render Dashboard

## Cost Estimation

### Monthly Costs

**Minimum Setup:**
- Render Standard: $7/month
- MongoDB Atlas M0: Free
- **Total: $7/month**

**Recommended Setup:**
- Render Standard Plus: $25/month
- MongoDB Atlas M10: $57/month (optional, M0 free tier works)
- **Total: $25-82/month**

**High Performance:**
- Render Pro: $85/month
- MongoDB Atlas M10: $57/month
- Persistent Disk (20GB): Included
- **Total: $85-142/month**

## Limitations on Render

### What Works ✅
- Docker deployment
- Persistent disk storage
- Multiple background services (aria2, qbittorrent, sabnzbd)
- MongoDB integration
- Auto-deploy from GitHub
- Environment variable management
- Health checks and monitoring

### Considerations ⚠️
- **Memory**: Ensure adequate RAM (minimum 512MB, recommended 1GB+)
- **Disk Space**: Monitor usage, expand as needed
- **Network**: Outbound traffic is unlimited
- **Build Time**: Initial build may take 5-10 minutes
- **Cold Starts**: Free tier services sleep after inactivity (paid plans don't)

## Support

For issues specific to this Render deployment:
1. Check Render logs first
2. Review this documentation
3. Check the main project [README.md](README.md)
4. Visit [Render Community](https://community.render.com)

For bot-specific issues:
- Telegram Group: https://t.me/mltb_official_support
- Telegram Channel: https://t.me/mltb_official_channel

## Security Best Practices

1. **Never commit sensitive data**: Use Render's environment variables
2. **Use MongoDB Atlas IP Whitelist**: Restrict database access
3. **Enable 2FA**: On both Render and GitHub accounts
4. **Rotate Tokens**: Periodically update BOT_TOKEN and API credentials
5. **Monitor Logs**: Regularly check for suspicious activity
6. **Backup Database**: Export MongoDB data periodically

## Advanced Configuration

### Custom Domain

1. Go to service **Settings** → **Custom Domain**
2. Add your domain
3. Update DNS records as instructed
4. Update `BASE_URL` and `RCLONE_SERVE_URL` environment variables

### Scaling

Render automatically handles scaling within your plan limits. For better performance:
- Upgrade to Pro or Pro Plus plans
- Increase persistent disk size
- Optimize qBittorrent and aria2c settings

### Multiple Instances

To run multiple bot instances:
1. Duplicate the service in `render.yaml`
2. Use different `BOT_TOKEN` for each
3. Deploy as separate services

## Migration from Other Platforms

### From Heroku
1. Export environment variables from Heroku
2. Set them in Render Dashboard
3. If using Heroku Postgres, migrate to MongoDB
4. Deploy to Render

### From VPS
1. Export your `config.py` values
2. Set as environment variables in Render
3. Upload private files via bot commands
4. Deploy to Render

## Conclusion

Render.com provides a reliable, cost-effective platform for hosting this bot with:
- ✅ Docker support
- ✅ Persistent storage
- ✅ Automatic deployments
- ✅ Easy scaling
- ✅ Better pricing than Heroku

For production use, we recommend the **Standard Plus** plan ($25/month) with MongoDB Atlas free tier.

