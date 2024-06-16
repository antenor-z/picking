import json
CONFIG_PATH = "config.json"

def mid_point(acc_cx, acc_cy):
    avg_cx = int(sum(acc_cx) / len(acc_cx))
    avg_cy = int(sum(acc_cy) / len(acc_cy))
    return [avg_cx, avg_cy]

def open_config():
    points_of_interest = []
    try:
        with open(CONFIG_PATH, 'r') as fp:
            points_of_interest = json.load(fp)
    except FileNotFoundError:
        with open(CONFIG_PATH, 'w+') as fp:
            fp.write("[]")
            points_of_interest = []
    return points_of_interest