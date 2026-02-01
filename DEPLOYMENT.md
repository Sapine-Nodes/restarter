# Deployment Checklist

Use this checklist to ensure successful deployment of the VPS Workflow Automation system.

## Pre-Deployment Checklist

### 1. Telegram Bot Setup
- [ ] Created a bot with [@BotFather](https://t.me/BotFather)
- [ ] Copied the bot token (format: `123456789:ABC...`)
- [ ] Started a conversation with the bot (sent at least one message)
- [ ] Obtained your Chat ID using one of these methods:
  - [ ] Used [@userinfobot](https://t.me/userinfobot), OR
  - [ ] Ran `python get_chat_id.py YOUR_BOT_TOKEN`

### 2. Repository Setup
- [ ] Forked/cloned this repository (if deploying manually)
- [ ] Verified all files are present (see File Checklist below)

### 3. Environment Variables Ready
- [ ] `TELEGRAM_BOT_TOKEN` - Your bot token from BotFather
- [ ] `TELEGRAM_CHAT_ID` - Your Telegram chat ID (as a number)

## Deployment Options

### Option A: One-Click Deploy to Render (Recommended)

1. [ ] Click "Deploy to Render" button in README
2. [ ] Connect your GitHub account
3. [ ] Fill in environment variables:
   - [ ] `TELEGRAM_BOT_TOKEN`
   - [ ] `TELEGRAM_CHAT_ID`
4. [ ] Click "Apply" to start deployment
5. [ ] Wait 5-10 minutes for initial deployment
6. [ ] Proceed to "Post-Deployment Verification"

### Option B: Manual Deploy to Render

1. [ ] Go to [Render.com](https://render.com) and sign in
2. [ ] Click "New +" → "Web Service"
3. [ ] Connect your GitHub repository
4. [ ] Configure the service:
   - [ ] Name: `vps-workflow-automation`
   - [ ] Environment: `Python 3`
   - [ ] Build Command: `pip install -r requirements.txt`
   - [ ] Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 0`
5. [ ] Add environment variables:
   - [ ] `TELEGRAM_BOT_TOKEN` = Your bot token
   - [ ] `TELEGRAM_CHAT_ID` = Your chat ID
   - [ ] `WORKFLOW_INTERVAL_HOURS` = `5` (optional)
   - [ ] `WORKFLOW_DURATION_HOURS` = `5` (optional)
6. [ ] Click "Create Web Service"
7. [ ] Wait 5-10 minutes for deployment
8. [ ] Proceed to "Post-Deployment Verification"

## Post-Deployment Verification

### 1. Check Service Status
- [ ] Service shows as "Live" in Render dashboard
- [ ] No error messages in deployment logs

### 2. Check Application Logs
Look for these messages in the logs:
- [ ] "Starting gunicorn..."
- [ ] "Scheduler initialized. Workflows will run every 5 hours"
- [ ] "Triggering initial workflow on startup"
- [ ] "Starting scheduled workflow: WF-XXXXXXXX-XXXXXX"
- [ ] "Starting workflow: WF-XXXXXXXX-XXXXXX"

### 3. Check Telegram Messages
You should receive these notifications:
- [ ] "🚀 New VPS Workflow Started"
- [ ] "⏳ Workflow ... Step: Cloning Repository - In Progress"
- [ ] "✅ Workflow ... Step: Cloning Repository - Success"
- [ ] Additional step notifications for Cloudflare, install.sh, etc.

### 4. Test API Endpoints
- [ ] Visit `https://your-service.onrender.com/` - Should show JSON status
- [ ] Visit `https://your-service.onrender.com/health` - Should return `{"status": "healthy"}`
- [ ] Visit `https://your-service.onrender.com/status` - Should show workflow status

### 5. Verify Workflow Progress
Within 2-3 minutes of deployment:
- [ ] First workflow should be running
- [ ] Telegram messages arriving for each step
- [ ] SSHX URL sent to Telegram (if successful)

## File Checklist

Verify all required files are present:

### Core Application Files
- [ ] `app.py` - Main Flask application (171 lines)
- [ ] `config.py` - Configuration management (24 lines)
- [ ] `workflow_executor.py` - Workflow execution logic (193 lines)
- [ ] `telegram_notifier.py` - Telegram integration (83 lines)

### Configuration Files
- [ ] `requirements.txt` - Python dependencies (6 lines)
- [ ] `render.yaml` - Render deployment config (18 lines)
- [ ] `Procfile` - Process configuration (1 line)
- [ ] `.env.example` - Environment variables template (13 lines)
- [ ] `.gitignore` - Git ignore rules (38 lines)

### Documentation Files
- [ ] `README.md` - Main documentation (231 lines)
- [ ] `QUICKSTART.md` - Deployment guide (136 lines)
- [ ] `ARCHITECTURE.md` - System architecture (242 lines)
- [ ] `DEPLOYMENT.md` - This checklist (you're reading it!)
- [ ] `LICENSE` - MIT License (21 lines)

### Helper Scripts
- [ ] `get_chat_id.py` - Get Telegram chat ID (72 lines)
- [ ] `test_setup.py` - Test installation (95 lines)

## Troubleshooting

### Issue: Service fails to deploy
- [ ] Check build logs for errors
- [ ] Verify `requirements.txt` is present
- [ ] Ensure Python 3.9+ is available

### Issue: No Telegram messages received
- [ ] Verify `TELEGRAM_BOT_TOKEN` is correct
- [ ] Verify `TELEGRAM_CHAT_ID` is a number (not username)
- [ ] Ensure you started a conversation with the bot
- [ ] Check service logs for "TELEGRAM_CHAT_ID not set" warnings

### Issue: Workflow fails to start
- [ ] Check logs for error messages
- [ ] Verify repository URL is accessible
- [ ] Check if git is available in the environment

### Issue: Service shows as "Deploying" for long time
- [ ] Wait up to 10 minutes for first deployment
- [ ] Check build logs for any errors
- [ ] Try redeploying if stuck

### Issue: Cloudflare installation fails
- [ ] This is expected in containerized environments
- [ ] Workflow will continue with other steps
- [ ] Not a critical failure

## Post-Deployment Tasks

### Monitor First Workflow
- [ ] Check logs for "Workflow ... completed successfully"
- [ ] Verify you received all Telegram notifications
- [ ] Confirm SSHX URL was sent (if applicable)

### Verify Auto-Restart
- [ ] Wait 5 hours for first workflow to complete
- [ ] Verify new workflow starts automatically
- [ ] Check Telegram for new workflow start notification

### Set Up Monitoring
- [ ] Bookmark your service URL for quick access
- [ ] Enable email notifications in Render (if desired)
- [ ] Consider upgrading to paid plan for 24/7 operation

## Success Criteria

Your deployment is successful if:
- ✅ Service is running and accessible
- ✅ Scheduler is initialized and running
- ✅ First workflow started automatically
- ✅ Telegram notifications are being received
- ✅ Workflow progresses through all steps
- ✅ API endpoints respond correctly
- ✅ Logs show no critical errors

## Next Steps

After successful deployment:
1. Monitor the first complete workflow cycle (5 hours)
2. Verify auto-restart happens after 5 hours
3. Check workflow status regularly via API or Telegram
4. Consider upgrading to Render paid plan for production use
5. Customize workflow parameters if needed

## Support

If you encounter issues:
1. Check the logs first (most issues are visible there)
2. Review this checklist to ensure all steps were completed
3. Consult the QUICKSTART.md for common solutions
4. Check ARCHITECTURE.md for technical details
5. Open an issue on GitHub with:
   - Error messages from logs
   - Steps you've already tried
   - Service configuration details

---

**Deployment Date**: _________________

**Deployed By**: _________________

**Service URL**: _________________

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Deployed | ⬜ Verified
