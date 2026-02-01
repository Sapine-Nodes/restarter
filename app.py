from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import threading
from datetime import datetime
from workflow_executor import WorkflowExecutor
from config import PORT, HOST, WORKFLOW_INTERVAL_HOURS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global state
workflow_status = {
    'current_workflow': None,
    'is_running': False,
    'last_workflow': None,
    'last_run_time': None,
    'next_run_time': None,
    'total_runs': 0,
    'successful_runs': 0,
    'failed_runs': 0
}

workflow_lock = threading.Lock()


def run_workflow_task():
    """Task to run the workflow - ensures only one runs at a time"""
    with workflow_lock:
        if workflow_status['is_running']:
            logger.warning("Workflow already running, skipping this execution")
            return
        
        workflow_status['is_running'] = True
        workflow_status['last_run_time'] = datetime.utcnow().isoformat()
        workflow_status['total_runs'] += 1
    
    try:
        executor = WorkflowExecutor()
        workflow_id = executor.generate_workflow_id()
        workflow_status['current_workflow'] = workflow_id
        
        logger.info(f"Starting scheduled workflow: {workflow_id}")
        success = executor.execute_workflow()
        
        with workflow_lock:
            workflow_status['last_workflow'] = workflow_id
            if success:
                workflow_status['successful_runs'] += 1
            else:
                workflow_status['failed_runs'] += 1
        
        logger.info(f"Workflow {workflow_id} finished. Success: {success}")
        
    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        with workflow_lock:
            workflow_status['failed_runs'] += 1
    
    finally:
        with workflow_lock:
            workflow_status['is_running'] = False
            workflow_status['current_workflow'] = None


# Create scheduler
scheduler = BackgroundScheduler()


@app.route('/')
def index():
    """Health check and status endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'VPS Workflow Automation',
        'version': '1.0.0',
        'workflow_status': workflow_status
    })


@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/status')
def status():
    """Get detailed workflow status"""
    return jsonify(workflow_status)


@app.route('/trigger', methods=['POST'])
def trigger_workflow():
    """Manually trigger a workflow"""
    if workflow_status['is_running']:
        return jsonify({
            'error': 'Workflow already running',
            'current_workflow': workflow_status['current_workflow']
        }), 409
    
    # Run workflow in background thread
    thread = threading.Thread(target=run_workflow_task)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'Workflow triggered successfully',
        'workflow_id': workflow_status.get('current_workflow', 'pending')
    }), 202


@app.route('/logs')
def get_logs():
    """Get recent logs (simplified version)"""
    return jsonify({
        'message': 'Check application logs for detailed information',
        'status': workflow_status
    })


def initialize_scheduler():
    """Initialize the workflow scheduler"""
    # Schedule workflow to run every WORKFLOW_INTERVAL_HOURS hours
    scheduler.add_job(
        func=run_workflow_task,
        trigger=IntervalTrigger(hours=WORKFLOW_INTERVAL_HOURS),
        id='workflow_job',
        name='Run VPS Workflow',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info(f"Scheduler initialized. Workflows will run every {WORKFLOW_INTERVAL_HOURS} hours")
    
    # Trigger the first workflow immediately on startup
    logger.info("Triggering initial workflow on startup")
    threading.Thread(target=run_workflow_task, daemon=True).start()


if __name__ == '__main__':
    logger.info("Starting VPS Workflow Automation Service")
    
    # Initialize scheduler
    initialize_scheduler()
    
    # Run Flask app
    try:
        app.run(host=HOST, port=PORT, debug=False)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        scheduler.shutdown()
