from fastapi import APIRouter, Depends, HTTPException, status
import subprocess
import os
import signal
import psutil
from pydantic import BaseModel

from ..core.dependencies import get_current_active_user
from ..models.user import User
from ..core.config import settings # Import settings

router = APIRouter(
    prefix="/bot",
    tags=["bot_control"],
    responses={404: {"description": "Not found"}},
)

# --- Bot Process Management ---

# Use paths from settings
BOT_PID_FILE = settings.WHATSAPP_BOT_PID_FILE
BOT_LOG_FILE = settings.WHATSAPP_BOT_LOG_FILE
BOT_SCRIPT_PATH = settings.WHATSAPP_BOT_SCRIPT_PATH
BOT_WORKING_DIR = settings.WHATSAPP_BOT_WORKING_DIR

# Global variable to hold the process object (less reliable across restarts/reloads)
# Using PID file is more robust
# BOT_PROCESS = None 

class BotStatusResponse(BaseModel):
    status: str
    pid: int | None = None

def get_bot_pid():
    """Reads the PID from the PID file."""
    if os.path.exists(BOT_PID_FILE):
        try:
            with open(BOT_PID_FILE, "r") as f:
                pid_str = f.read().strip()
                if pid_str:
                    return int(pid_str)
        except (ValueError, IOError):
            # If file is corrupted or unreadable, remove it
            try:
                os.remove(BOT_PID_FILE)
            except OSError:
                pass 
            return None
    return None

def is_process_running(pid: int) -> bool:
    """Checks if a process with the given PID is running."""
    if pid is None:
        return False
    try:
        process = psutil.Process(pid)
        # Check if the process is running and is a node process
        # Checking command line can be brittle, checking name is usually enough
        return process.is_running() and 'node' in process.name().lower()
    except psutil.NoSuchProcess:
        return False
    except psutil.AccessDenied:
        # Might happen on some systems, assume it's running if we can't check
        print(f"Access denied checking PID {pid}. Assuming running.")
        return True 
    except Exception as e:
        print(f"Error checking process {pid}: {e}")
        return False

def write_bot_pid(pid: int | None):
    """Writes the PID to the PID file."""
    try:
        if pid:
            os.makedirs(os.path.dirname(BOT_PID_FILE), exist_ok=True) # Ensure directory exists
            with open(BOT_PID_FILE, "w") as f:
                f.write(str(pid))
        elif os.path.exists(BOT_PID_FILE):
            os.remove(BOT_PID_FILE)
    except IOError as e:
        print(f"Error writing PID file {BOT_PID_FILE}: {e}")

@router.post("/start", response_model=BotStatusResponse)
async def start_bot(current_user: User = Depends(get_current_active_user)):
    """Starts the WhatsApp bot process using configured paths."""
    pid = get_bot_pid()
    if pid and is_process_running(pid):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Bot process is already running with PID {pid}."
        )

    # Clean up stale PID file if process not actually running
    if pid and not is_process_running(pid):
        print(f"Stale PID file found ({BOT_PID_FILE} for PID {pid}). Removing.")
        write_bot_pid(None)

    try:
        # Validate configured paths
        if not os.path.isdir(BOT_WORKING_DIR):
            raise HTTPException(status_code=500, detail=f"Bot working directory not found: {BOT_WORKING_DIR}. Check WHATSAPP_BOT_WORKING_DIR in your .env file or config.")
        if not os.path.isfile(BOT_SCRIPT_PATH):
             raise HTTPException(status_code=500, detail=f"Bot script not found: {BOT_SCRIPT_PATH}. Check WHATSAPP_BOT_SCRIPT_PATH in your .env file or config.")

        # Ensure log directory exists
        os.makedirs(os.path.dirname(BOT_LOG_FILE), exist_ok=True)
        log_file = open(BOT_LOG_FILE, "a")

        # Start the Node.js process
        # Using os.setsid to ensure the child process group can be killed reliably
        process = subprocess.Popen(
            ["node", BOT_SCRIPT_PATH],
            cwd=BOT_WORKING_DIR,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            close_fds=True,
            start_new_session=True # Use start_new_session=True for cross-platform session creation
        )

        write_bot_pid(process.pid)
        print(f"Bot process started with PID {process.pid}")
        return BotStatusResponse(status="running", pid=process.pid)

    except Exception as e:
        write_bot_pid(None) # Clear PID if start failed
        print(f"Error starting bot process: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start bot process: {str(e)}"
        )

@router.post("/stop", response_model=BotStatusResponse)
async def stop_bot(current_user: User = Depends(get_current_active_user)):
    """Stops the WhatsApp bot process using the PID file."""
    pid = get_bot_pid()
    if not pid:
        # Check if maybe a process is running without a PID file (e.g., manual start)
        # This part is complex and potentially dangerous, skipping for now.
        # Focus on managing processes started via the panel.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot PID file not found. Cannot determine process to stop."
        )

    if not is_process_running(pid):
        print(f"Bot process with PID {pid} from file {BOT_PID_FILE} not found or not running. Cleaning up PID file.")
        write_bot_pid(None) # Ensure PID file is removed if process not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bot process (PID: {pid}) is not running."
        )

    try:
        print(f"Attempting to stop bot process group with PID {pid}...")
        # Send SIGTERM to the process group leader (the PID we stored)
        # On Windows, killpg doesn't exist. Need platform-specific logic or rely on psutil.
        # psutil provides a more cross-platform way
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        # Terminate children first
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                continue
        # Wait for children to terminate
        gone, alive = psutil.wait_procs(children, timeout=3)
        for p in alive:
             try:
                 p.kill()
             except psutil.NoSuchProcess:
                 continue
        # Terminate parent
        try:
            parent.terminate()
            parent.wait(timeout=5)
        except psutil.NoSuchProcess:
            pass # Already terminated
        except psutil.TimeoutExpired:
            print(f"Bot process {pid} did not terminate gracefully, sending SIGKILL.")
            parent.kill()

        # Verify it's stopped
        if is_process_running(pid):
             print(f"Process {pid} still running after stop attempt.")
             # If it's somehow still running, raise an error
             raise OSError(f"Failed to stop process {pid}")
        else:
            print(f"Bot process {pid} stopped successfully.")
            write_bot_pid(None)
            return BotStatusResponse(status="stopped", pid=None)

    except psutil.NoSuchProcess:
        # Process was already gone
        print(f"Bot process {pid} was already stopped.")
        write_bot_pid(None)
        return BotStatusResponse(status="stopped", pid=None)
    except Exception as e:
        print(f"Error stopping bot process {pid}: {str(e)}")
        # Check if it stopped despite the error
        if not is_process_running(pid):
             write_bot_pid(None)
             return BotStatusResponse(status="stopped", pid=None)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to stop bot process {pid}: {str(e)}"
            )

@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status(current_user: User = Depends(get_current_active_user)):
    """Gets the current status of the WhatsApp bot process via PID file."""
    pid = get_bot_pid()
    if pid and is_process_running(pid):
        return BotStatusResponse(status="running", pid=pid)
    else:
        # If PID file exists but process isn't running, clean up PID file
        if pid:
             print(f"Cleaning stale PID file {BOT_PID_FILE} for PID {pid}")
             write_bot_pid(None)
        return BotStatusResponse(status="stopped", pid=None)

@router.get("/logs", response_model=str)
async def get_bot_logs(current_user: User = Depends(get_current_active_user), lines: int = 50):
    """Gets the last N lines from the bot log file."""
    if not os.path.exists(BOT_LOG_FILE):
        return f"Log file not found at {BOT_LOG_FILE}."
    try:
        # Using tail might not be available on Windows. Python read is more portable.
        with open(BOT_LOG_FILE, "r", encoding='utf-8', errors='ignore') as f:
            # Read all lines and return the last N
            log_lines = f.readlines()
            return "".join(log_lines[-lines:])
    except Exception as e:
        print(f"Error reading log file {BOT_LOG_FILE}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read log file: {str(e)}"
        )

