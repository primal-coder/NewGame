import json

def load_json(path):
    """Load a JSON file from the given path."""
    with open(path, 'r') as f:
        return json.load(f)
    
def save_json(path, data):
    """Save a JSON file to the given path."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)