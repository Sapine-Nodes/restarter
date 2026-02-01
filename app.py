from flask import Flask, jsonify, request
import requests
import os
from datetime import datetime
import logging
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO = os.environ.get('GITHUB_REPO', '')  # Format: owner/repo
WORKFLOW_FILE = os.environ.get('WORKFLOW_FILE', '')  # e.g., main.yml
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', '60'))  # seconds
PORT = int(os.environ.get('PORT', '10000'))

# State management
monitor_state = {
    'is_monitoring': False,
    'last_check': None,
    'current_run_id': None,
    'current_run_status': None,
    'last_run_id': None,
    'last_run_status': None,
    'total_checks': 0,
    'triggered_workflows': 0
}

monitor_lock = threading.Lock()


class GitHubWorkflowMonitor:
    """Monitor and manage GitHub workflow runs"""
    
    def __init__(self, token, repo, workflow_file):
        self.token = token
        self.repo = repo
        self.workflow_file = workflow_file
        self.base_url = f"https://api.github.com/repos/{repo}"
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_workflow_runs(self, status=None, per_page=1):
        """Get workflow runs for the specified workflow file"""
        try:
            params = {
                'per_page': per_page
            }
            if status:
                params['status'] = status
                
            url = f"{self.base_url}/actions/workflows/{self.workflow_file}/runs"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting workflow runs: {e}")
            return None
    
    def is_workflow_running(self):
        """Check if a workflow is currently running"""
        try:
            # Check for in_progress or queued workflows
            for status in ['in_progress', 'queued']:
                data = self.get_workflow_runs(status=status, per_page=1)
                if data and data.get('total_count', 0) > 0:
                    run = data['workflow_runs'][0]
                    logger.info(f"Found {status} workflow: {run['id']} - {run['status']}")
                    return True, run['id'], run['status']
            
            return False, None, None
        except Exception as e:
            logger.error(f"Error checking workflow status: {e}")
            return False, None, None
    
    def trigger_workflow(self, ref='main', inputs=None):
        """Trigger a new workflow run"""
        try:
            url = f"{self.base_url}/actions/workflows/{self.workflow_file}/dispatches"
            payload = {
                'ref': ref
            }
            if inputs:
                payload['inputs'] = inputs
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            logger.info(f"Workflow triggered successfully on ref: {ref}")
            return True
        except Exception as e:
            logger.error(f"Error triggering workflow: {e}")
            return False


def monitor_and_trigger():
    """Background task to monitor and trigger workflows"""
    global monitor_state
    
    if not GITHUB_TOKEN or not GITHUB_REPO or not WORKFLOW_FILE:
        logger.error("Missing required configuration. Set GITHUB_TOKEN, GITHUB_REPO, and WORKFLOW_FILE")
        return
    
    monitor = GitHubWorkflowMonitor(GITHUB_TOKEN, GITHUB_REPO, WORKFLOW_FILE)
    
    with monitor_lock:
        monitor_state['is_monitoring'] = True
    
    logger.info("Starting workflow monitoring...")
    
    try:
        while monitor_state['is_monitoring']:
            with monitor_lock:
                monitor_state['last_check'] = datetime.utcnow().isoformat()
                monitor_state['total_checks'] += 1
            
            # Check if workflow is running
            is_running, run_id, status = monitor.is_workflow_running()
            
            with monitor_lock:
                monitor_state['current_run_id'] = run_id
                monitor_state['current_run_status'] = status
            
            if not is_running:
                # No workflow running, trigger a new one
                logger.info("No workflow running. Triggering new workflow...")
                success = monitor.trigger_workflow()
                
                if success:
                    with monitor_lock:
                        monitor_state['triggered_workflows'] += 1
                    logger.info("Workflow triggered successfully. Waiting for it to start...")
                    time.sleep(10)  # Wait a bit for the workflow to start
                else:
                    logger.error("Failed to trigger workflow")
            else:
                logger.info(f"Workflow {run_id} is {status}. Waiting for it to complete...")
            
            # Wait before next check
            time.sleep(CHECK_INTERVAL)
            
    except Exception as e:
        logger.error(f"Error in monitoring loop: {e}")
    finally:
        with monitor_lock:
            monitor_state['is_monitoring'] = False
        logger.info("Monitoring stopped")


@app.route('/')
def index():
    """API information"""
    return jsonify({
        'service': 'GitHub Workflow Monitor',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            '/': 'API information',
            '/health': 'Health check',
            '/status': 'Get monitoring status',
            '/start': 'Start monitoring (POST)',
            '/stop': 'Stop monitoring (POST)',
            '/trigger': 'Manually trigger workflow (POST)',
            '/config': 'Get current configuration'
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/status')
def status():
    """Get current monitoring status"""
    return jsonify(monitor_state)


@app.route('/config')
def config():
    """Get current configuration (without sensitive data)"""
    return jsonify({
        'github_repo': GITHUB_REPO,
        'workflow_file': WORKFLOW_FILE,
        'check_interval': CHECK_INTERVAL,
        'token_configured': bool(GITHUB_TOKEN)
    })


@app.route('/start', methods=['POST'])
def start_monitoring():
    """Start the workflow monitoring"""
    if monitor_state['is_monitoring']:
        return jsonify({
            'error': 'Monitoring already running',
            'status': monitor_state
        }), 409
    
    if not GITHUB_TOKEN or not GITHUB_REPO or not WORKFLOW_FILE:
        return jsonify({
            'error': 'Missing configuration',
            'message': 'Please set GITHUB_TOKEN, GITHUB_REPO, and WORKFLOW_FILE environment variables'
        }), 400
    
    # Start monitoring in background thread
    thread = threading.Thread(target=monitor_and_trigger, daemon=True)
    thread.start()
    
    return jsonify({
        'message': 'Monitoring started',
        'config': {
            'repo': GITHUB_REPO,
            'workflow': WORKFLOW_FILE,
            'check_interval': CHECK_INTERVAL
        }
    }), 200


@app.route('/stop', methods=['POST'])
def stop_monitoring():
    """Stop the workflow monitoring"""
    if not monitor_state['is_monitoring']:
        return jsonify({
            'error': 'Monitoring not running'
        }), 409
    
    with monitor_lock:
        monitor_state['is_monitoring'] = False
    
    return jsonify({
        'message': 'Monitoring stopped',
        'status': monitor_state
    }), 200


@app.route('/trigger', methods=['POST'])
def trigger_workflow():
    """Manually trigger a workflow"""
    if not GITHUB_TOKEN or not GITHUB_REPO or not WORKFLOW_FILE:
        return jsonify({
            'error': 'Missing configuration',
            'message': 'Please set GITHUB_TOKEN, GITHUB_REPO, and WORKFLOW_FILE environment variables'
        }), 400
    
    data = request.get_json() or {}
    ref = data.get('ref', 'main')
    inputs = data.get('inputs', None)
    
    monitor = GitHubWorkflowMonitor(GITHUB_TOKEN, GITHUB_REPO, WORKFLOW_FILE)
    success = monitor.trigger_workflow(ref=ref, inputs=inputs)
    
    if success:
        return jsonify({
            'message': 'Workflow triggered successfully',
            'repo': GITHUB_REPO,
            'workflow': WORKFLOW_FILE,
            'ref': ref
        }), 200
    else:
        return jsonify({
            'error': 'Failed to trigger workflow'
        }), 500


if __name__ == '__main__':
    logger.info("Starting GitHub Workflow Monitor API")
    logger.info(f"Repository: {GITHUB_REPO}")
    logger.info(f"Workflow: {WORKFLOW_FILE}")
    logger.info(f"Check interval: {CHECK_INTERVAL}s")
    
    # Auto-start monitoring if configured
    if GITHUB_TOKEN and GITHUB_REPO and WORKFLOW_FILE:
        logger.info("Configuration detected. Auto-starting monitoring...")
        thread = threading.Thread(target=monitor_and_trigger, daemon=True)
        thread.start()
    else:
        logger.warning("Missing configuration. Monitoring not started automatically.")
        logger.warning("Please set GITHUB_TOKEN, GITHUB_REPO, and WORKFLOW_FILE environment variables")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
