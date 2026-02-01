import os
import subprocess
import logging
import time
import shutil
from datetime import datetime
from telegram_notifier import TelegramNotifier
from config import REPO_URL, WORK_DIR, WORKFLOW_DURATION_HOURS

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """Executes the VPS workflow steps"""
    
    def __init__(self):
        self.notifier = TelegramNotifier()
        self.workflow_id = None
        self.work_dir = None
        self.process = None
    
    def generate_workflow_id(self):
        """Generate a unique workflow ID"""
        return f"WF-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    
    def setup_work_directory(self):
        """Create and setup working directory"""
        self.work_dir = os.path.join(WORK_DIR, self.workflow_id)
        os.makedirs(self.work_dir, exist_ok=True)
        logger.info(f"Work directory created: {self.work_dir}")
    
    def cleanup_work_directory(self):
        """Clean up working directory"""
        if self.work_dir and os.path.exists(self.work_dir):
            try:
                shutil.rmtree(self.work_dir)
                logger.info(f"Work directory cleaned up: {self.work_dir}")
            except Exception as e:
                logger.error(f"Failed to clean up work directory: {e}")
    
    def run_command(self, command, step_name, timeout=300):
        """Run a shell command and return output"""
        logger.info(f"Running: {step_name}")
        self.notifier.send_workflow_step(self.workflow_id, step_name, "In Progress")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.work_dir
            )
            
            if result.returncode == 0:
                logger.info(f"{step_name} completed successfully")
                self.notifier.send_workflow_step(self.workflow_id, step_name, "Success")
                return True, result.stdout
            else:
                logger.error(f"{step_name} failed: {result.stderr}")
                self.notifier.send_workflow_step(self.workflow_id, step_name, f"Failed: {result.stderr[:100]}")
                return False, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"{step_name} timed out")
            self.notifier.send_workflow_step(self.workflow_id, step_name, "Timeout")
            return False, "Command timed out"
        except Exception as e:
            logger.error(f"{step_name} error: {e}")
            self.notifier.send_workflow_step(self.workflow_id, step_name, f"Error: {str(e)}")
            return False, str(e)
    
    def clone_repository(self):
        """Clone the GitHub repository"""
        repo_name = REPO_URL.split('/')[-1].replace('.git', '')
        repo_path = os.path.join(self.work_dir, repo_name)
        
        command = f"git clone {REPO_URL} {repo_path}"
        success, output = self.run_command(command, "Cloning Repository", timeout=600)
        
        if success:
            # Change work directory to cloned repo
            self.work_dir = repo_path
        
        return success
    
    def install_cloudflare(self):
        """Install Cloudflare on the system"""
        # Note: This requires sudo which might not work in all environments
        # For Render.com, this step will likely fail, but we'll log it
        commands = [
            "sudo mkdir -p --mode=0755 /usr/share/keyrings || true",
            "curl -fsSL https://pkg.cloudflare.com/cloudflare-public-v2.gpg | sudo tee /usr/share/keyrings/cloudflare-public-v2.gpg >/dev/null || true",
            "echo 'deb [signed-by=/usr/share/keyrings/cloudflare-public-v2.gpg] https://pkg.cloudflare.com/cloudflared any main' | sudo tee /etc/apt/sources.list.d/cloudflared.list || true",
            "sudo apt-get update && sudo apt-get install -y cloudflared || true"
        ]
        
        for i, cmd in enumerate(commands):
            step_name = f"Installing Cloudflare (Step {i+1}/{len(commands)})"
            success, output = self.run_command(cmd, step_name, timeout=600)
            # Continue even if some steps fail (sudo might not be available)
            if not success:
                logger.warning(f"Cloudflare installation step {i+1} failed, continuing...")
        
        return True  # Return True even if some steps fail
    
    def run_install_script(self):
        """Run the install.sh script"""
        install_script = os.path.join(self.work_dir, "install.sh")
        
        if not os.path.exists(install_script):
            logger.warning(f"install.sh not found at {install_script}")
            self.notifier.send_workflow_step(self.workflow_id, "Running install.sh", "Skipped (not found)")
            return True  # Continue even if script doesn't exist
        
        # Make script executable
        os.chmod(install_script, 0o755)
        
        command = "./install.sh"
        success, output = self.run_command(command, "Running install.sh", timeout=1800)
        
        return success
    
    def run_sshx(self):
        """Run sshx and capture the URL"""
        # First, try to install sshx if not already installed
        install_cmd = "curl -sSf https://sshx.io/get | sh || true"
        self.run_command(install_cmd, "Installing sshx", timeout=300)
        
        # Run sshx in background and capture URL
        # Note: This is a simplified version. In production, you'd want to properly manage this process
        command = "sshx 2>&1 | grep -o 'https://sshx.io/s/[a-zA-Z0-9#]*' | head -1"
        success, output = self.run_command(command, "Starting sshx", timeout=60)
        
        if success and output.strip():
            url = output.strip()
            logger.info(f"SSHX URL: {url}")
            self.notifier.send_sshx_url(self.workflow_id, url)
            return True, url
        else:
            logger.warning("Failed to get SSHX URL")
            return False, None
    
    def execute_workflow(self):
        """Execute the complete workflow"""
        self.workflow_id = self.generate_workflow_id()
        logger.info(f"Starting workflow: {self.workflow_id}")
        
        try:
            # Send start notification
            self.notifier.send_workflow_start(self.workflow_id)
            
            # Setup working directory
            self.setup_work_directory()
            
            # Execute workflow steps
            if not self.clone_repository():
                raise Exception("Failed to clone repository")
            
            self.install_cloudflare()
            
            self.run_install_script()
            
            self.run_sshx()
            
            # Keep the workflow running for the specified duration
            logger.info(f"Workflow will run for {WORKFLOW_DURATION_HOURS} hours")
            self.notifier.send_workflow_step(
                self.workflow_id, 
                f"Workflow Active (will run for {WORKFLOW_DURATION_HOURS} hours)", 
                "Running"
            )
            
            # Sleep for the duration (in production, you'd want better process management)
            time.sleep(WORKFLOW_DURATION_HOURS * 3600)
            
            # Send completion notification
            self.notifier.send_workflow_end(self.workflow_id, success=True)
            logger.info(f"Workflow {self.workflow_id} completed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Workflow {self.workflow_id} failed: {e}")
            self.notifier.send_error(self.workflow_id, str(e))
            self.notifier.send_workflow_end(self.workflow_id, success=False)
            return False
        
        finally:
            # Cleanup
            self.cleanup_work_directory()
