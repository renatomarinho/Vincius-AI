import sys
from pathlib import Path

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv 
from Vincius.Core.workflow_manager import WorkflowManager

def main():
    load_dotenv()
    manager = WorkflowManager()
    manager.execute_workflow()

if __name__ == "__main__":
    main()