# load yaml from file
import yaml 

def load_yaml(filepath):
    with open(filepath, 'r') as f:
        yaml_data = yaml.safe_load(f)

    return yaml_data