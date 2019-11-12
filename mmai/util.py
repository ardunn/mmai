import json


def load_json(datapath):
    """
    Load the raw fighter data from wikipedia.

    Args:
        datapath (str): The path to find the fighters.json file at.

    Returns:
        [dict]: A list of fighter dicts from wikipedia data.
    """

    with open(datapath, "r") as f:
        loaded = json.load(f)
    return loaded
