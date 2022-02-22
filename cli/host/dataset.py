import json
import os

with open("./configs/datasets.json", "r") as file:
    datasets_file = file.read()

class DatasetList:
    def __init__(self):
        datasets_file = json.loads(datasets_file)
        datasets_file = json.dumps(datasets_file, indent=2)

        self.datasets = datasets_file