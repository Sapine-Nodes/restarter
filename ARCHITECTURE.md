# VPS Workflow Automation - System Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Render.com / Cloud Platform                 │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │               Flask Web Application                        │ │
│  │                    (Gunicorn)                              │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────┐    │ │
│  │  │         APScheduler Background Service           │    │ │
│  │  │                                                   │    │ │
│  │  │  Trigger: Every 5 hours (IntervalTrigger)        │    │ │
│  │  │  Lock: Ensures only 1 workflow runs at a time    │    │ │
│  │  └────────────────┬─────────────────────────────────┘    │ │
│  │                   │                                        │ │
│  │                   │ Triggers                               │ │
│  │                   ▼                                        │ │
│  │  ┌──────────────────────────────────────────────────┐    │ │
│  │  │           Workflow Executor                       │    │ │
│  │  │                                                   │    │ │
│  │  │  Step 1: Clone Repository                        │    │ │
│  │  │  ├─> git clone sapine-nodes-api                  │    │ │
│  │  │                                                   │    │ │
│  │  │  Step 2: Install Cloudflare                      │    │ │
│  │  │  ├─> Setup GPG keys                              │    │ │
│  │  │  ├─> Add apt repository                          │    │ │
│  │  │  └─> Install cloudflared                         │    │ │
│  │  │                                                   │    │ │
│  │  │  Step 3: Run install.sh                          │    │ │
│  │  │  └─> Execute setup script from repo              │    │ │
│  │  │                                                   │    │ │
│  │  │  Step 4: Start SSHX                              │    │ │
│  │  │  ├─> Install sshx client                         │    │ │
│  │  │  └─> Capture connection URL                      │    │ │
│  │  │                                                   │    │ │
│  │  │  Step 5: Keep Alive (5 hours)                    │    │ │
│  │  │  └─> Maintain workflow state                     │    │ │
│  │  │                                                   │    │ │
│  │  └───────────────┬──────────────────────────────────┘    │ │
│  │                  │                                         │ │
│  │                  │ Sends notifications                     │ │
│  │                  ▼                                         │ │
│  │  ┌──────────────────────────────────────────────────┐    │ │
│  │  │         Telegram Notifier                         │    │ │
│  │  │                                                   │    │ │
│  │  │  • Workflow Start                                │    │ │
│  │  │  • Step Progress Updates                         │    │ │
│  │  │  • SSHX URL Notification                         │    │ │
│  │  │  • Error Alerts                                  │    │ │
│  │  │  • Workflow Completion                           │    │ │
│  │  └───────────────┬──────────────────────────────────┘    │ │
│  │                  │                                         │ │
│  └──────────────────┼─────────────────────────────────────────┤ │
│                     │                                         │ │
│  API Endpoints:     │                                         │ │
│  GET  /            │                                         │ │
│  GET  /health      │                                         │ │
│  GET  /status      │                                         │ │
│  POST /trigger     │                                         │ │
│                     │                                         │ │
└─────────────────────┼─────────────────────────────────────────┘
                      │
                      │ HTTPS API
                      ▼
           ┌──────────────────────┐
           │   Telegram Bot API   │
           │                      │
           │  Bot Token: 8362...  │
           └──────────┬───────────┘
                      │
                      │ Messages
                      ▼
              ┌───────────────┐
              │  Your Phone   │
              │   (Telegram)  │
              └───────────────┘
```

## Workflow Timeline

```
Time: 00:00 - Workflow 1 Starts
├─ 00:00:10 - Repository cloned
├─ 00:00:30 - Cloudflare installation (may skip)
├─ 00:01:00 - install.sh executed
├─ 00:01:30 - SSHX started, URL sent to Telegram
└─ 05:00:00 - Workflow 1 Ends

Time: 05:00:01 - Workflow 2 Starts (automatically)
├─ 05:00:10 - Repository cloned
├─ 05:00:30 - Cloudflare installation (may skip)
├─ 05:01:00 - install.sh executed
├─ 05:01:30 - SSHX started, URL sent to Telegram
└─ 10:00:00 - Workflow 2 Ends

... (continues indefinitely)
```

## Data Flow

```
User Configuration
       │
       ├─> TELEGRAM_BOT_TOKEN ──┐
       ├─> TELEGRAM_CHAT_ID ────┤
       ├─> REPO_URL ────────────┼─> config.py
       ├─> WORKFLOW_INTERVAL ───┤
       └─> WORKFLOW_DURATION ───┘
                │
                ▼
           app.py (Flask)
                │
                ├─> Initializes Scheduler
                │   └─> Triggers every 5 hours
                │
                ├─> workflow_executor.py
                │   ├─> Executes workflow steps
                │   └─> Manages work directory
                │
                └─> telegram_notifier.py
                    └─> Sends updates to Telegram
```

## File Structure

```
restarter/
├── app.py                  # Main Flask application & scheduler
├── config.py               # Configuration management
├── workflow_executor.py    # Workflow logic & step execution
├── telegram_notifier.py    # Telegram bot integration
├── requirements.txt        # Python dependencies
├── render.yaml            # Render.com deployment config
├── Procfile               # Process configuration
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── LICENSE               # MIT License
├── README.md             # Main documentation
├── QUICKSTART.md         # Deployment guide
├── get_chat_id.py        # Helper: Get Telegram chat ID
└── test_setup.py         # Helper: Test installation
```

## Key Features

### 1. Single Workflow Lock
```python
workflow_lock = threading.Lock()

def run_workflow_task():
    with workflow_lock:
        if workflow_status['is_running']:
            logger.warning("Already running, skipping")
            return
        workflow_status['is_running'] = True
    # ... execute workflow
```

### 2. Automatic Restart
```python
# Scheduler configuration
scheduler.add_job(
    func=run_workflow_task,
    trigger=IntervalTrigger(hours=5),
    id='workflow_job'
)
```

### 3. Real-time Notifications
```python
notifier.send_workflow_start(workflow_id)
notifier.send_workflow_step(workflow_id, step, status)
notifier.send_sshx_url(workflow_id, url)
notifier.send_workflow_end(workflow_id, success)
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | - | Yes |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | - | Yes |
| `REPO_URL` | Repository to clone | sapine-nodes-api | No |
| `WORKFLOW_INTERVAL_HOURS` | Hours between workflows | 5 | No |
| `WORKFLOW_DURATION_HOURS` | Duration of each workflow | 5 | No |
| `PORT` | Server port | 10000 | No |

## Monitoring

### Health Check
```bash
curl https://your-app.onrender.com/health
# Response: {"status": "healthy"}
```

### Status Check
```bash
curl https://your-app.onrender.com/status
# Response: Full workflow status JSON
```

### Manual Trigger
```bash
curl -X POST https://your-app.onrender.com/trigger
# Response: {"message": "Workflow triggered successfully"}
```

## Security Considerations

1. **Telegram Bot Token**: Keep secret, never commit to version control
2. **Environment Variables**: Use Render's encrypted environment variables
3. **SSHX Access**: URLs are temporary and expire after workflow ends
4. **Sudo Commands**: May fail in containerized environments (expected)
5. **Work Directory**: Cleaned up after each workflow

## Troubleshooting

### Issue: No Telegram notifications
**Solution**: Verify `TELEGRAM_CHAT_ID` is set and bot has been started

### Issue: Workflow fails to start
**Solution**: Check logs for specific error, verify repo URL is accessible

### Issue: Cloudflare installation fails
**Solution**: Expected in containerized environments, workflow continues

### Issue: Service sleeps (Free tier)
**Solution**: Upgrade to paid plan for 24/7 operation

## Performance

- **Startup Time**: ~10-15 seconds
- **Repository Clone**: ~5-10 seconds (depends on repo size)
- **Cloudflare Install**: Variable (may skip on containerized environments)
- **install.sh**: Depends on script complexity
- **SSHX Setup**: ~5-10 seconds
- **Memory Usage**: ~100-200MB
- **CPU Usage**: Low during idle, medium during workflow execution
