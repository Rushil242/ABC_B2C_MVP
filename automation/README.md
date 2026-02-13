# Income Tax Website Scraper - Workflow System

Modular workflow system using Playwright for automated income tax website data extraction.

## Features

- **Modular Workflows**: Easy to add new workflows by extending base class
- **Automated Login**: Handles two-step login with session modal detection
- **Anti-Detection**: Stealth mode with disabled automation flags
- **Pagination Support**: Automatically processes all pages
- **Headless Mode**: Run with or without browser UI
- **Organized Output**: Each workflow stores results in separate directories

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Usage

### Run a workflow:
```bash
python run_workflow.py filed_returns
```

### Run in headless mode:
```bash
python run_workflow.py filed_returns --headless
```

### List available workflows:
```bash
python run_workflow.py
```

## Available Workflows

- **filed_returns**: Download all filed income tax returns as JSON files with pagination support

## Architecture

```
workflows/
├── base_workflow.py      # Base class with browser setup & login
├── filed_returns.py      # Filed returns workflow
├── registry.py           # Workflow registry
└── __init__.py

run_workflow.py           # Main entry point
config.py                 # Configuration loader
.env                      # Credentials (not in git)
```

## Creating New Workflows

1. Create new file in `workflows/` directory:
```python
from workflows.base_workflow import BaseWorkflow

class MyWorkflow(BaseWorkflow):
    def execute(self):
        # Your workflow logic here
        # self.page is available for Playwright operations
        # self.workflow_dir contains output directory path
        pass
```

2. Register in `workflows/registry.py`:
```python
from workflows.my_workflow import MyWorkflow

WORKFLOWS = {
    'filed_returns': FiledReturnsWorkflow,
    'my_workflow': MyWorkflow,  # Add here
}
```

3. Run it:
```bash
python run_workflow.py my_workflow
```

## Output Structure

```
downloads/
├── filedreturns/
│   ├── return_1_*.json
│   ├── return_2_*.json
│   └── results.json
└── otherworkflow/
    └── results.json
```

## Configuration

Edit `.env` file:
```
INCOME_TAX_USERNAME=YOUR_PAN_OR_AADHAAR
INCOME_TAX_PASSWORD=YOUR_PASSWORD
INCOME_TAX_URL=https://eportal.incometax.gov.in/iec/foservices/#/login
DOWNLOAD_PATH=./downloads
```

## Requirements

- Python 3.8+
- playwright==1.48.0
- langgraph==0.2.45
- langchain-core==0.3.15
- python-dotenv==1.0.1
