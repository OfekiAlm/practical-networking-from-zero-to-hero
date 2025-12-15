"""Job executor for running demos in isolated Docker containers."""
import json
import logging
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any

from backend.demos.registry import get_registry
from backend.schemas.base import JobStatus

logger = logging.getLogger(__name__)


def execute_demo_in_container(
    job_id: str,
    demo_id: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a demo in an isolated Docker container.
    
    This is the main worker function that will be called by RQ.
    It spawns a Docker container with security constraints and
    executes the demo.
    
    Args:
        job_id: Unique job identifier
        demo_id: Demo to execute
        parameters: Validated parameters
        
    Returns:
        Execution result as dictionary
    """
    logger.info(f"Job {job_id}: Starting execution of {demo_id}")
    start_time = time.time()
    
    try:
        # Get demo from registry
        registry = get_registry()
        demo = registry.get_demo(demo_id)
        
        if not demo:
            return {
                "success": False,
                "data": None,
                "error": f"Demo '{demo_id}' not found",
                "metadata": {
                    "job_id": job_id,
                    "execution_time_ms": (time.time() - start_time) * 1000
                }
            }
        
        # Check if Docker is available
        docker_available = _check_docker_available()
        
        if docker_available and demo.recipe.requires_root:
            # Execute in Docker container with proper isolation
            result = _execute_in_docker(job_id, demo_id, parameters, demo.recipe.max_runtime)
        else:
            # Fallback: Execute directly (for development/testing)
            # In production, this should always use Docker
            logger.warning(f"Job {job_id}: Executing without Docker isolation")
            result = _execute_directly(demo_id, parameters)
        
        execution_time = (time.time() - start_time) * 1000
        result["metadata"]["execution_time_ms"] = execution_time
        
        logger.info(f"Job {job_id}: Completed in {execution_time:.2f}ms")
        return result
        
    except Exception as e:
        logger.error(f"Job {job_id}: Execution failed: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "error": f"Execution error: {str(e)}",
            "metadata": {
                "job_id": job_id,
                "execution_time_ms": (time.time() - start_time) * 1000
            }
        }


def _check_docker_available() -> bool:
    """Check if Docker is available."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _execute_in_docker(
    job_id: str,
    demo_id: str,
    parameters: Dict[str, Any],
    max_runtime: int
) -> Dict[str, Any]:
    """
    Execute demo in a Docker container with security constraints.
    
    Security measures:
    - Non-root user
    - Read-only filesystem
    - CPU and memory limits
    - Execution timeout
    - Network disabled (unless required)
    - No privilege escalation
    """
    logger.info(f"Job {job_id}: Executing in Docker container")
    
    # Create temporary directory for input/output
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Write parameters to file
        params_file = tmppath / "params.json"
        with open(params_file, 'w') as f:
            json.dump(parameters, f)
        
        # Output file
        output_file = tmppath / "output.json"
        
        # Docker run command with security constraints
        docker_cmd = [
            "docker", "run",
            "--rm",  # Remove container after execution
            "--read-only",  # Read-only filesystem
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=100m",  # Writable /tmp with restrictions
            "--security-opt", "no-new-privileges:true",  # No privilege escalation
            "--cap-drop", "ALL",  # Drop all capabilities
            "--cpus", "1.0",  # CPU limit
            "--memory", "512m",  # Memory limit
            "--memory-swap", "512m",  # No swap
            "--pids-limit", "100",  # Process limit
            "--network", "none",  # No network access (can be changed per demo)
            "-v", f"{params_file}:/input/params.json:ro",  # Mount params as read-only
            "-v", f"{tmppath}:/output:rw",  # Mount output directory
            "-e", f"DEMO_ID={demo_id}",
            "-e", "PYTHONUNBUFFERED=1",
            "networking-demo-worker:latest",  # Worker image
            "python", "-m", "backend.worker.container_runner",
            "/input/params.json",
            "/output/output.json"
        ]
        
        try:
            # Execute with timeout
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=max_runtime + 5  # Add buffer to max_runtime
            )
            
            # Read output
            if output_file.exists():
                with open(output_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": "No output generated",
                    "metadata": {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode
                    }
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"Job {job_id}: Execution timeout")
            return {
                "success": False,
                "data": None,
                "error": f"Execution timeout after {max_runtime}s",
                "metadata": {"timeout": max_runtime}
            }
        except Exception as e:
            logger.error(f"Job {job_id}: Docker execution error: {e}")
            return {
                "success": False,
                "data": None,
                "error": f"Docker execution error: {str(e)}",
                "metadata": {}
            }


def _execute_directly(demo_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute demo directly without Docker (fallback for development).
    
    WARNING: This should only be used in development. Production
    should always use Docker containers for isolation.
    """
    try:
        registry = get_registry()
        result = registry.execute_demo(demo_id, parameters)
        return result
    except Exception as e:
        logger.error(f"Direct execution error: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "error": f"Execution error: {str(e)}",
            "metadata": {}
        }


if __name__ == "__main__":
    """Test execution."""
    # Example test
    result = execute_demo_in_container(
        job_id="test-123",
        demo_id="tcp-handshake",
        parameters={
            "target_ip": "142.250.185.46",
            "target_port": 80,
            "timeout": 5
        }
    )
    print(json.dumps(result, indent=2))
