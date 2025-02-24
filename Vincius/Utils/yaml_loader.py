import yaml

class YamlLoader:
    def __init__(self, yaml_file: str):
        self.yaml_file = f"Workflows/{yaml_file}"

    def load_yaml(self) -> dict:
        try:
            with open(self.yaml_file, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                if not data or 'workflow' not in data:
                    raise ValueError("Invalid YAML file: Missing 'workflow' key.")
                workflow_data = data.get('workflow')
                if not isinstance(workflow_data, dict):
                    raise ValueError("Invalid YAML file: 'workflow' must be a dictionary.")
                for step_name, step_info in workflow_data.items():
                    if not isinstance(step_info, dict):
                        raise ValueError(f"Invalid YAML file: Step '{step_name}' must be a dictionary.")
                return workflow_data
        except FileNotFoundError:
            raise Exception(f"YAML file not found: {self.yaml_file}")
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing YAML file: {str(e)}")