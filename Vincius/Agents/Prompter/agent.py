from typing import Dict, Any
from Vincius.Core.brain_model import BrainModel
from Vincius.Agents.base_agent import BaseAgent
from Vincius.Core.file_system_manager import FileSystemManager

class PrompterAgent(BaseAgent):
    """
    An agent that executes a prompt using a language model and passes the output to the next step.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "Prompter"
        self.config = config
        self.brain = BrainModel()
        self.fs_manager = FileSystemManager(agent=self)
        print(f"🔧 Initialized {self.name} agent with UUID: {self.uuid[:8]}")

    def execute(self, input_data: Any = None) -> str:
        """
        Executes the prompt using the language model and returns the output.
        """
        try:
            prompt = self.config.get("prompt")
            if not prompt:
                raise ValueError("Prompt not defined in agent configuration.")

            # Format the prompt with input data if needed
            if input_data:
                prompt = prompt.format(input_data)

            print("\n📝 Executing prompt...")
            output = self.brain.generate(prompt, self.config)

            if not output:
                raise ValueError("No output generated from prompt.")

            print(f"✅ Prompt executed successfully.")
            return output

        except Exception as e:
            print(f"\n❌ Error executing prompt: {e}")
            return f"Error executing prompt: {str(e)}"
