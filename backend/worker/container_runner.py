#!/usr/bin/env python3
"""
Container runner script.

This script runs inside the Docker container and executes the demo
with the provided parameters.
"""
import json
import sys
import os
from pathlib import Path


def main():
    """Main execution function for container."""
    if len(sys.argv) != 3:
        print("Usage: container_runner.py <params_file> <output_file>")
        sys.exit(1)
    
    params_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    # Get demo ID from environment
    demo_id = os.environ.get("DEMO_ID")
    if not demo_id:
        result = {
            "success": False,
            "data": None,
            "error": "DEMO_ID environment variable not set",
            "metadata": {}
        }
        with open(output_file, 'w') as f:
            json.dump(result, f)
        sys.exit(1)
    
    try:
        # Load parameters
        with open(params_file, 'r') as f:
            parameters = json.load(f)
        
        # Import and execute demo
        from backend.demos.registry import get_registry
        
        registry = get_registry()
        result = registry.execute_demo(demo_id, parameters)
        
        # Write output
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Exit with appropriate code
        sys.exit(0 if result.get("success", False) else 1)
        
    except Exception as e:
        result = {
            "success": False,
            "data": None,
            "error": f"Container execution error: {str(e)}",
            "metadata": {}
        }
        with open(output_file, 'w') as f:
            json.dump(result, f)
        sys.exit(1)


if __name__ == "__main__":
    main()
