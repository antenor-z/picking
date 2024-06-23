import json

def open_config(CONFIG_PATH):
    points_of_interest = []
    try:
        with open(CONFIG_PATH, 'r') as fp:
            points_of_interest = json.load(fp)
    except FileNotFoundError:
        with open(CONFIG_PATH, 'w+') as fp:
            fp.write("[]")
            points_of_interest = []
    return points_of_interest

def point_inside(box, point):
    inside_x = min(box['point_1'][0], box['point_2'][0]) \
      < point[0] < max(box['point_1'][0], box['point_2'][0])
    inside_y = min(box['point_1'][1], box['point_2'][1]) \
      < point[1] < max(box['point_1'][1], box['point_2'][1])
    return inside_x and inside_y