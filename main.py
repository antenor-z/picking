# Import necessary libraries
import sys
import requests
from tqdm.notebook import tqdm
from pathlib import Path
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.pylab import rcParams

from yolov9.detect import run as run_detect_yolov9

# URLs of weight files
weight_files = [
    "https://github.com/WongKinYiu/yolov9/releases/download/v0.1/yolov9-c.pt",
    "https://github.com/WongKinYiu/yolov9/releases/download/v0.1/yolov9-e.pt",
    "https://github.com/WongKinYiu/yolov9/releases/download/v0.1/gelan-c.pt",
    "https://github.com/WongKinYiu/yolov9/releases/download/v0.1/gelan-e.pt"
]
CODE_FOLDER = Path("yolo_test").resolve()
WEIGHTS_FOLDER = CODE_FOLDER / "weights"
DATA_FOLDER = CODE_FOLDER / "data"

# Iterates over the list of URLs to download the weight files
for i, url in enumerate(weight_files, start=1):
    filename = url.split('/')[-1]
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kilobyte
    # progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Downloading file {i}/{len(weight_files)}: {filename}")
    with open(WEIGHTS_FOLDER / filename, 'wb') as file:
        for data in response.iter_content(block_size):
            # progress_bar.update(len(data))
            file.write(data)
    # progress_bar.close()