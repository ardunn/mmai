import os
import json

thisdir = os.path.dirname(os.path.abspath(__file__))
wikipedia_file_path = os.path.join(thisdir, "data/fighters.json")


def load_fighters_wikipedia(datapath=wikipedia_file_path):
    """
    Load the raw fighter data from wikipedia.

    Args:
        datapath (str): The path to find the fighters.json file at.

    Returns:
        [dict]: A list of fighter dicts from wikipedia data.
    """

    with open(datapath, "r") as f:
        fighters_wikipedia = json.load(f)
    return fighters_wikipedia
