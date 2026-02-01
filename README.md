# GitHub Workflow Monitor API 🚀

A Flask API that monitors GitHub repository workflows and automatically triggers new workflow runs when the previous one completes.

## Features

✨ **Automatic Monitoring**: Continuously checks if workflows are running  
🔄 **Auto-Trigger**: Starts new workflows when previous ones complete  
🔒 **Smart Detection**: Prevents duplicate workflow runs  
📊 **Status API**: Real-time monitoring status and statistics  
☁️ **Deploy to Render**: One-click deployment to Render.com  

## How It Works

1. **Monitor**: The API periodically checks if a GitHub workflow is running
2. **Detect**: If no workflow is running (completed, failed, or not started)
3. **Trigger**: Automatically starts a new workflow run
4. **Repeat**: Continues monitoring and triggering to keep workflows running continuously

## Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Sapine-Nodes/restarter)

### Manual Deployment Steps

1. **Create a new Web Service on Render.com**
   - Connect your GitHub repository
   - Select "Python" as the environment
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

2. **Configure Environment Variables**

   Required:
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token with `repo` and `workflow` permissions
   - `GITHUB_REPO`: Repository to monitor (format: `owner/repo`, e.g., `octocat/hello-world`)
   - `WORKFLOW_FILE`: Workflow file to monitor (e.g., `main.yml`, `.github/workflows/ci.yml`)

   Optional:
   - `CHECK_INTERVAL`: Seconds between checks (default: `60`)
   - `PORT`: Server port (default: `10000`)

3. **Deploy!**
   Click "Create Web Service" and Render will automatically deploy your application.

## Setup GitHub Token

### Create a Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Workflow Monitor")
4. Select the following scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
5. Click "Generate token"
6. **Copy the token immediately** (you won't be able to see it again)

### Configure the Token

Add the token to your environment:
- **On Render**: Add as an environment variable in your service settings
- **Locally**: Add to your `.env` file

## Local Development

### Prerequisites

- Python 3.9 or higher
- pip package manager
- GitHub Personal Access Token

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sapine-Nodes/restarter.git
   cd restarter
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file (copy from `.env.example`):
   ```env
   GITHUB_TOKEN=ghp_your_token_here
   GITHUB_REPO=owner/repository
   WORKFLOW_FILE=main.yml
   CHECK_INTERVAL=60
   PORT=10000
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

   The server will start on `http://0.0.0.0:10000` and automatically begin monitoring.

## API Endpoints

### `GET /`
Get API information and available endpoints

**Response:**
```json
{
  "service": "GitHub Workflow Monitor",
  "version": "1.0.0",
  "status": "running",
  "endpoints": { ... }
}
```

### `GET /health`
Health check endpoint for monitoring services

**Response:**
```json
{
  "status": "healthy"
}
```

### `GET /status`
Get current monitoring status and statistics

**Response:**
```json
{
  "is_monitoring": true,
  "last_check": "2026-02-01T19:15:30.123456",
  "current_run_id": 123456789,
  "current_run_status": "in_progress",
  "total_checks": 45,
  "triggered_workflows": 12
}
```

### `GET /config`
Get current configuration (without sensitive data)

**Response:**
```json
{
  "github_repo": "owner/repo",
  "workflow_file": "main.yml",
  "check_interval": 60,
  "token_configured": true
}
```

### `POST /start`
Start workflow monitoring (if not already running)

**Response:**
```json
{
  "message": "Monitoring started",
  "config": {
    "repo": "owner/repo",
    "workflow": "main.yml",
    "check_interval": 60
  }
}
```

### `POST /stop`
Stop workflow monitoring

**Response:**
```json
{
  "message": "Monitoring stopped",
  "status": { ... }
}
```

### `POST /trigger`
Manually trigger a workflow run

**Request Body (optional):**
```json
{
  "ref": "main",
  "inputs": {
    "key": "value"
  }
}
```

**Response:**
```json
{
  "message": "Workflow triggered successfully",
  "repo": "owner/repo",
  "workflow": "main.yml",
  "ref": "main"
}
```

## Workflow Requirements

Your GitHub workflow must be configured to accept manual triggers (workflow_dispatch):

```yaml
name: My Workflow

on:
  workflow_dispatch:
    inputs:
      # Optional inputs
      example:
        description: 'Example input'
        required: false
        default: 'default-value'
  # Other triggers...

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # Your workflow steps...
```

## Architecture

```
┌─────────────────────────────────────────────┐
│           Flask API Server                  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │   Background Monitor Thread         │   │
│  │                                     │   │
│  │  1. Check workflow status           │   │
│  │  2. If not running → Trigger        │   │
│  │  3. Wait CHECK_INTERVAL             │   │
│  │  4. Repeat                          │   │
│  └─────────────────────────────────────┘   │
│                 │                           │
│                 ▼                           │
│  ┌─────────────────────────────────────┐   │
│  │   GitHub API Integration            │   │
│  │                                     │   │
│  │  • GET workflow runs                │   │
│  │  • POST workflow dispatches         │   │
│  │  • Check run status                 │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## Configuration Guide

### Check Interval

The `CHECK_INTERVAL` determines how often the API checks workflow status:
- **Lower values** (30-60s): More responsive, but more API calls
- **Higher values** (120-300s): Fewer API calls, but slower response

GitHub API rate limits:
- **Authenticated requests**: 5,000 requests per hour
- With `CHECK_INTERVAL=60`, you'll make ~60 requests per hour

### Workflow File

Specify the workflow file you want to monitor:
- Full path: `.github/workflows/main.yml`
- Filename only: `main.yml`
- Use the exact filename from your repository

## Troubleshooting

### Monitoring Not Starting

1. Check logs for error messages
2. Verify all environment variables are set
3. Ensure GitHub token has correct permissions
4. Verify repository and workflow file names are correct

### Workflows Not Triggering

1. Check that workflow has `workflow_dispatch` trigger
2. Verify token has `workflow` scope
3. Check GitHub API rate limits
4. Review logs for error messages

### "404 Not Found" Errors

1. Verify `GITHUB_REPO` format is correct (`owner/repo`)
2. Check that `WORKFLOW_FILE` exists in the repository
3. Ensure token has access to the repository

## Security Considerations

⚠️ **Keep your GitHub token secure:**
- Never commit tokens to version control
- Use environment variables only
- Rotate tokens regularly
- Use minimum required scopes

⚠️ **Token Permissions:**
- Grants full control of workflows
- Can trigger potentially expensive operations
- Monitor usage and costs

## Limitations

- GitHub API rate limits apply (5,000 requests/hour authenticated)
- Free Render tier may sleep after 15 minutes of inactivity
- Workflow must support `workflow_dispatch` trigger

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your own purposes.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the logs for error messages
- Verify environment variables are configured correctly

---

**Made with ❤️ for continuous workflow automation**
