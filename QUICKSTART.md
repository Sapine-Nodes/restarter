# Quick Start Guide

## Deployment to Render.com

### Step 1: Prepare Your Telegram Bot

1. **Create a Telegram Bot** (if you don't have one):
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot` and follow the instructions
   - Copy the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **Get Your Chat ID**:
   - Send any message to your bot
   - Use one of these methods:
     - **Method A**: Message [@userinfobot](https://t.me/userinfobot) and copy your Chat ID
     - **Method B**: Run `python get_chat_id.py YOUR_BOT_TOKEN` (locally)

### Step 2: Deploy to Render

#### Option A: One-Click Deploy (Recommended)

1. Click the Deploy to Render button in the README
2. Fill in the required environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
   - `TELEGRAM_CHAT_ID`: Your chat ID from step 1
3. Click "Apply" to start deployment

#### Option B: Manual Deploy

1. **Fork this repository** to your GitHub account

2. **Go to [Render.com](https://render.com)** and sign up/login

3. **Create a New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select your forked repository
   
4. **Configure the service**:
   - **Name**: `vps-workflow-automation` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 0`
   
5. **Set Environment Variables**:
   
   Required:
   - `TELEGRAM_BOT_TOKEN` = Your bot token
   - `TELEGRAM_CHAT_ID` = Your chat ID
   
   Optional (with defaults):
   - `WORKFLOW_INTERVAL_HOURS` = `5` (hours between workflows)
   - `WORKFLOW_DURATION_HOURS` = `5` (how long each workflow runs)
   - `PORT` = `10000` (server port)

6. **Deploy**: Click "Create Web Service"

### Step 3: Verify Deployment

1. **Check the service logs** on Render dashboard:
   - You should see: "Scheduler initialized. Workflows will run every 5 hours"
   - You should see: "Triggering initial workflow on startup"

2. **Check Telegram**:
   - You should receive a message: "🚀 New VPS Workflow Started"
   - Followed by progress updates for each step

3. **Test the API** (optional):
   - Visit your service URL (e.g., `https://your-service.onrender.com`)
   - You should see a JSON response with status information

### Step 4: Monitor and Maintain

- **View Logs**: Check the "Logs" tab in Render dashboard
- **Check Status**: Visit `https://your-service.onrender.com/status`
- **Manual Trigger**: POST to `https://your-service.onrender.com/trigger`

## Important Notes

### Free Tier Limitations

If you're using Render's free tier:

1. **Service Sleep**: The service will spin down after 15 minutes of inactivity
   - Incoming requests will wake it up (with delay)
   - Consider upgrading to a paid plan for 24/7 operation
   
2. **Resource Limits**: Free tier has limited CPU and memory
   - Workflows might run slower
   - Some operations (like Cloudflare installation) may fail

3. **Build Time**: Free tier builds can be slower
   - Initial deployment may take 5-10 minutes

### Recommendations for Production Use

1. **Upgrade to Starter Plan** ($7/month):
   - 24/7 uptime
   - More resources
   - Better performance

2. **Set Up Monitoring**:
   - Use Render's built-in monitoring
   - Set up alerts for errors

3. **Regular Checks**:
   - Monitor Telegram messages
   - Check logs periodically
   - Verify workflows are completing successfully

## Troubleshooting

### No Telegram Messages Received

1. Verify bot token is correct
2. Ensure chat ID is correct (must be a number)
3. Make sure you've started a conversation with your bot
4. Check service logs for errors

### Workflow Fails Immediately

1. Check if the repository URL is accessible
2. Verify all environment variables are set correctly
3. Check logs for specific error messages

### Service Not Responding

1. Check if service is running in Render dashboard
2. If on free tier, service might be sleeping - send a request to wake it
3. Check logs for startup errors

### Cloudflare Installation Fails

This is expected in containerized environments without sudo access. The workflow will continue with other steps.

## Support

For issues:
- Check the logs first
- Review this guide
- Open an issue on GitHub
- Verify all environment variables

## Next Steps

After successful deployment:
1. Monitor the first workflow completion
2. Verify you receive all Telegram notifications
3. Check that workflows restart automatically every 5 hours
4. Consider upgrading to a paid plan for production use
