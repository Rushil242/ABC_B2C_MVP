from workflows.filed_returns import FiledReturnsWorkflow
from workflows.form_26as import Form26ASWorkflow
from workflows.ais_download import AISDownloadWorkflow
from workflows.eproceedings import EProceedingsWorkflow

# Registry of all available workflows
WORKFLOWS = {
    'filed_returns': FiledReturnsWorkflow,
    'form_26as': Form26ASWorkflow,
    'ais_download': AISDownloadWorkflow,
    'eproceedings': EProceedingsWorkflow,
}

def list_workflows():
    """List all available workflows"""
    print("\nAvailable workflows:")
    for name in WORKFLOWS.keys():
        print(f"  - {name}")

def run_workflow(workflow_name, headless=False):
    """Run a specific workflow by name"""
    if workflow_name not in WORKFLOWS:
        print(f"[ERROR] Workflow '{workflow_name}' not found")
        list_workflows()
        return
    
    workflow_class = WORKFLOWS[workflow_name]
    workflow = workflow_class(headless=headless)
    workflow.run()
