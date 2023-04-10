import json

CONFIG_PATH = "output config.json"

with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)


def get_target_commit_path():
    return config['target commit']


def get_smell_detection_path():
    return config['smell detection']


def get_graph_data_path():
    return config['graph data']


def get_line_diff_path():
    return config['line diff']


def get_duplicated_instances_path():
    return config['duplicated instances']
