import sys
from workflows.registry import run_workflow, list_workflows

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_workflow.py <workflow_name> [--headless]")
        list_workflows()
        sys.exit(1)
    
    workflow_name = sys.argv[1]
    headless = '--headless' in sys.argv
    
    if headless:
        print("[INFO] Running in headless mode")
    
    run_workflow(workflow_name, headless=headless)
