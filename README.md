# VPS Workflow Automation 🚀

Automated VPS workflow system that runs every 5 hours, cloning repositories, installing Cloudflare, and managing SSHX connections with Telegram notifications.

## Features

✨ **Automated Workflows**: Runs every 5 hours automatically  
🔄 **Self-Restarting**: Immediately starts a new workflow when one completes  
📱 **Telegram Notifications**: Real-time updates on workflow progress  
🔒 **Single Workflow Lock**: Ensures only one workflow runs at a time  
📊 **Status Monitoring**: Built-in API endpoints for monitoring  
☁️ **Cloud Ready**: Deployable on Render.com with one click  

## What It Does

Each workflow execution performs the following steps:

1. **Clone Repository**: Clones https://github.com/Arpitraj02/sapine-nodes-api
2. **Install Cloudflare**: Sets up Cloudflare GPG key and installs cloudflared
3. **Run Installation Script**: Executes `./install.sh` from the cloned repository
4. **Start SSHX**: Launches SSHX and captures the connection URL
5. **Send Notifications**: Sends all progress updates to your Telegram bot
6. **Run for 5 Hours**: Keeps the workflow active for 5 hours
7. **Auto-Restart**: Automatically starts a new workflow after completion

## Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Sapine-Nodes/restarter)

### Manual Deployment Steps

1. **Fork or clone this repository**

2. **Create a new Web Service on Render.com**
   - Connect your GitHub repository
   - Select "Python" as the environment
   - Use the following settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

3. **Configure Environment Variables**

   Required:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (default: `8362379114:AAFg_bOXNSu5uiLagudbPGS4Hshjg53NAmM`)
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID (get it from [@userinfobot](https://t.me/userinfobot))

   Optional:
   - `WORKFLOW_INTERVAL_HOURS`: Hours between workflow runs (default: `5`)
   - `WORKFLOW_DURATION_HOURS`: Duration each workflow runs (default: `5`)
   - `PORT`: Server port (default: `10000`)
   - `REPO_URL`: Repository to clone (default: `https://github.com/Arpitraj02/sapine-nodes-api`)

4. **Deploy!**

   Click "Create Web Service" and Render will automatically deploy your application.

## Local Development

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sapine-Nodes/restarter.git
   cd restarter
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN=8362379114:AAFg_bOXNSu5uiLagudbPGS4Hshjg53NAmM
   TELEGRAM_CHAT_ID=your_chat_id_here
   WORKFLOW_INTERVAL_HOURS=5
   WORKFLOW_DURATION_HOURS=5
   ```

5. **Test the setup (optional but recommended)**
   ```bash
   python test_setup.py
   ```
   
   This will verify all dependencies and configuration.

6. **Run the application**
   ```bash
   python app.py
   ```

   The server will start on `http://0.0.0.0:10000`

## API Endpoints

### `GET /`
Health check and basic status information

**Response:**
```json
{
  "status": "running",
  "service": "VPS Workflow Automation",
  "version": "1.0.0",
  "workflow_status": { ... }
}
```

### `GET /health`
Health check endpoint for monitoring

**Response:**
```json
{
  "status": "healthy"
}
```

### `GET /status`
Get detailed workflow status

**Response:**
```json
{
  "current_workflow": "WF-20260201-141530",
  "is_running": true,
  "last_workflow": "WF-20260201-091530",
  "last_run_time": "2026-02-01T09:15:30",
  "total_runs": 5,
  "successful_runs": 4,
  "failed_runs": 1
}
```

### `POST /trigger`
Manually trigger a workflow (only if no workflow is currently running)

**Response:**
```json
{
  "message": "Workflow triggered successfully",
  "workflow_id": "WF-20260201-141530"
}
```

## Getting Your Telegram Chat ID

### Method 1: Using the Helper Script (Recommended)

1. Send a message to your bot on Telegram (any message)
2. Run the helper script:
   ```bash
   python get_chat_id.py YOUR_BOT_TOKEN
   ```
3. Copy the Chat ID from the output

### Method 2: Using @userinfobot

1. Start a chat with [@userinfobot](https://t.me/userinfobot) on Telegram
2. The bot will respond with your user information including your Chat ID
3. Copy the Chat ID and add it to your environment variables as `TELEGRAM_CHAT_ID`

## Telegram Notifications

The bot sends the following types of notifications:

- 🚀 **Workflow Started**: When a new workflow begins
- ⏳ **Step Progress**: Updates for each step (cloning, installing, etc.)
- ✅ **Step Success**: When a step completes successfully
- 🔗 **SSHX URL**: The connection URL when SSHX is ready
- ✅ **Workflow Completed**: When the workflow finishes successfully
- ❌ **Errors**: Any errors that occur during execution

## Workflow Logs

All workflow activities are logged with timestamps. To view logs:

- **On Render.com**: Check the "Logs" tab in your service dashboard
- **Locally**: Logs are printed to the console

## Architecture

```
┌─────────────────────────────────────────────┐
│           Flask Application                 │
│  ┌─────────────────────────────────────┐   │
│  │   APScheduler (Every 5 hours)       │   │
│  └──────────────┬──────────────────────┘   │
│                 │                           │
│                 ▼                           │
│  ┌─────────────────────────────────────┐   │
│  │     Workflow Executor                │   │
│  │  • Clone Repository                  │   │
│  │  • Install Cloudflare                │   │
│  │  • Run install.sh                    │   │
│  │  • Start SSHX                        │   │
│  │  • Send Telegram Updates             │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │     Telegram Notifier                │   │
│  │  • Send Progress Updates             │   │
│  │  • Send SSHX URLs                    │   │
│  │  • Send Error Alerts                 │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## Important Notes

⚠️ **Limitations on Render.com Free Tier:**
- Sudo commands may not work (Cloudflare installation may fail)
- Services automatically sleep after 15 minutes of inactivity
- Consider upgrading to a paid plan for continuous operation

⚠️ **SSHX Considerations:**
- SSHX requires terminal access which may be limited in containerized environments
- The SSHX URL capture may not work in all deployment scenarios
- Consider testing the full workflow in your specific environment

## Troubleshooting

### Workflows Not Starting

1. Check the logs for any error messages
2. Verify environment variables are set correctly
3. Ensure the service is not sleeping (on free tier)

### Telegram Notifications Not Sending

1. Verify `TELEGRAM_BOT_TOKEN` is correct
2. Ensure `TELEGRAM_CHAT_ID` is set
3. Start a conversation with your bot first
4. Check that the bot has not been blocked

### Cloudflare Installation Failing

This is expected on platforms without sudo access. The workflow continues anyway.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your own purposes.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the logs for error messages
- Verify all environment variables are configured correctly

---

**Made with ❤️ for continuous VPS automation**
