# Mirror-Leech Telegram Bot - Render.com Deployment

This is the **Render.com optimized branch** of the Mirror-Leech Telegram Bot. This branch includes specific configurations and modifications to ensure smooth deployment on Render.com's platform.

## 🚀 Quick Deploy to Render.com

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## What's Different in This Branch?

This `render` branch includes the following Render.com-specific optimizations:

### 1. **Port Binding Support**
- ✅ Automatically detects and uses Render's `PORT` environment variable
- ✅ Modified `bot/core/startup.py` to support dynamic port binding
- ✅ Updated `bot/modules/bot_settings.py` for port flexibility
- ✅ Enhanced `bot/core/config_manager.py` with PORT detection

### 2. **Render Configuration Files**
- ✅ `render.yaml` - Blueprint for one-click deployment
- ✅ `Dockerfile.render` - Optimized Docker configuration
- ✅ `start_render.sh` - Render-specific startup script
- ✅ `RENDER_DEPLOYMENT.md` - Comprehensive deployment guide

### 3. **Environment Variable Handling**
- ✅ All configuration via environment variables
- ✅ No need to modify `config.py` file
- ✅ Secure credential management through Render Dashboard

### 4. **Persistent Storage**
- ✅ Configured persistent disk for downloads
- ✅ MongoDB integration for settings and user data
- ✅ Automatic cleanup and optimization

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Render.com Account** - [Sign up here](https://render.com)
2. **Telegram Bot Token** - Get from [@BotFather](https://t.me/BotFather)
3. **Telegram API Credentials** - Get from [my.telegram.org](https://my.telegram.org)
4. **MongoDB Database** - Use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (free tier available)

## 🔧 Deployment Methods

### Method 1: One-Click Deploy (Recommended)

1. Click the "Deploy to Render" button above
2. Connect your GitHub account
3. Set required environment variables
4. Click "Apply" to deploy

### Method 2: Manual Deploy via Dashboard

1. Fork this repository to your GitHub account
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New +** → **Blueprint**
4. Connect your forked repository
5. Select the `render` branch
6. Render will detect `render.yaml` automatically
7. Configure environment variables
8. Click **Apply**

### Method 3: Deploy as Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your repository
4. Select the `render` branch
5. Render will auto-detect Docker
6. Set environment variables manually
7. Click **Create Web Service**

## 🔑 Required Environment Variables

Set these in Render Dashboard under **Environment** tab:

```bash
# Essential (REQUIRED)
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
OWNER_ID=123456789
TELEGRAM_API=12345678
TELEGRAM_HASH=abcdef1234567890abcdef1234567890
DATABASE_URL=mongodb+srv://user:pass@cluster.mongodb.net/mltb

# Optional but Recommended
AUTHORIZED_CHATS=-100xxxxxxxxxx
SUDO_USERS=123456789
```

See [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) for complete list of environment variables.

## 💰 Pricing Recommendations

### Minimum Setup (Budget)
- **Render Plan**: Standard ($7/month)
- **RAM**: 512MB
- **Disk**: 10GB persistent disk (included)
- **MongoDB**: Atlas M0 (Free)
- **Total**: ~$7/month

### Recommended Setup (Best Value)
- **Render Plan**: Standard Plus ($25/month)
- **RAM**: 1GB
- **Disk**: 20GB persistent disk
- **MongoDB**: Atlas M0 (Free) or M10 ($57/month)
- **Total**: $25-82/month

### High Performance
- **Render Plan**: Pro ($85/month)
- **RAM**: 2GB
- **Disk**: 50GB persistent disk
- **MongoDB**: Atlas M10 ($57/month)
- **Total**: $85-142/month

## 📊 Resource Allocation

The bot requires adequate resources due to multiple background services:

| Service | RAM Usage | Purpose |
|---------|-----------|---------|
| Python Bot | 200-500MB | Main application |
| qBittorrent | 100-300MB | Torrent downloads |
| Aria2c | 50-150MB | Direct downloads |
| SABnzbd | 100-200MB | Usenet downloads |
| JDownloader | 300-500MB | Multi-host downloads |
| **Total** | **1-2GB+** | **Baseline + buffers** |

**Recommendation**: Use at least **Standard Plus (1GB)** plan for reliable operation.

## 🗂️ Persistent Storage

The `render.yaml` configures a persistent disk:

```yaml
disk:
  name: bot-storage
  mountPath: /usr/src/app/downloads
  sizeGB: 10  # Adjust as needed
```

To increase disk size:
1. Edit `render.yaml` and change `sizeGB`
2. Commit and push changes
3. Render will resize the disk automatically

## 🔍 Monitoring and Logs

### View Logs
1. Go to your service in Render Dashboard
2. Click **Logs** tab
3. View real-time application logs

### Check Health
- Render monitors the `/` endpoint automatically
- Health checks run every 30 seconds
- Service restarts automatically if unhealthy

### Metrics
- CPU usage
- Memory usage
- Request count
- Response times

Available in Render Dashboard under **Metrics** tab.

## 🛠️ Post-Deployment Setup

### 1. Verify Deployment
Check logs for successful startup:
```
Bot Started!
```

### 2. Test Bot
Send `/start` to your bot on Telegram

### 3. Configure Settings
Use `/bsetting` command to configure:
- Download clients (aria2, qBittorrent, SABnzbd)
- Upload destinations
- Queue settings
- Private files

### 4. Upload Private Files (Optional)
If you need Google Drive or Rclone:
1. Use `/bsetting` → Private Files
2. Upload `token.pickle`, `rclone.conf`, etc.
3. Files are stored in MongoDB

## 🔄 Updates and Maintenance

### Automatic Updates
The bot auto-updates from `UPSTREAM_REPO` on each restart:
```bash
UPSTREAM_REPO=https://github.com/el-pablos/mirror-leech-telegram-bot
UPSTREAM_BRANCH=render
```

### Manual Update
1. Push changes to your repository
2. Render auto-deploys (if enabled)
3. Or click **Manual Deploy** in dashboard

### Restart Service
- Use `/restart` command in bot
- Or click **Manual Deploy** → **Deploy latest commit**

## ⚠️ Important Notes

### Differences from VPS Deployment

| Feature | VPS | Render.com |
|---------|-----|------------|
| Persistent Storage | ✅ Full disk | ✅ Persistent disk (configurable) |
| Port Binding | Fixed ports | Dynamic PORT variable |
| Resource Limits | Unlimited | Plan-based limits |
| Cost | $12-24/month | $7-85/month |
| Management | Manual | Automated |
| Scaling | Manual | Automatic |

### Limitations

1. **Memory**: Ensure adequate RAM for all services
2. **Disk I/O**: May be slower than dedicated VPS
3. **Network**: Outbound traffic unlimited, but speed varies
4. **Build Time**: Initial deployment takes 5-10 minutes

### Best Practices

1. **Use MongoDB**: Essential for persistence across restarts
2. **Monitor Resources**: Check CPU/RAM usage regularly
3. **Optimize Settings**: Reduce concurrent downloads if needed
4. **Regular Backups**: Export MongoDB data periodically
5. **Security**: Never commit sensitive data to repository

## 🐛 Troubleshooting

### Bot Won't Start
- Check environment variables are set correctly
- Verify BOT_TOKEN is valid
- Check MongoDB connection string
- Review logs for specific errors

### Out of Memory
- Upgrade to higher plan (Standard Plus or Pro)
- Reduce concurrent downloads in settings
- Lower qBittorrent memory limits

### Port Binding Errors
- Ensure code modifications are applied
- Check that PORT environment variable is detected
- Review startup logs

### Download Failures
- Verify persistent disk is mounted
- Check disk space availability
- Review download client logs

## 📚 Additional Resources

- **Full Documentation**: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
- **Main README**: [README.md](README.md)
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Support Group**: [Telegram](https://t.me/mltb_official_support)
- **Support Channel**: [Telegram](https://t.me/mltb_official_channel)

## 🤝 Contributing

This branch is specifically for Render.com deployment. For general contributions:
1. Submit PRs to the `master` branch
2. Render-specific changes go to `render` branch
3. Follow existing code style
4. Test thoroughly before submitting

## 📄 License

Same as the main project. See [LICENSE](LICENSE) file.

## 🙏 Credits

- Original Project: [anasty17/mirror-leech-telegram-bot](https://github.com/anasty17/mirror-leech-telegram-bot)
- Render.com Optimization: This branch
- Community: All contributors and users

---

**Ready to deploy?** Click the button at the top or follow the deployment guide!

For detailed instructions, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)

