import os

from mmai.util import load_json

this_dir = os.path.dirname(os.path.abspath(__file__))


def load_wikipedia_raw():
    """
    Load the raw wikipedia data from scraping.

    Returns:
        (list): The raw scraped data.
    """
    wikipedia_raw_file_path = os.path.join(this_dir, "data/wiki_fighters_raw.json")
    return load_json(wikipedia_raw_file_path)


def load_wikipedia_processed():
    """
    Load the processed data from wikipedia processed.

    Returns:
        (dict): {fighter: {everything}}
    """
    wikipedia_processed_file_path = os.path.join(this_dir, "data/wiki_fighters_processed.json")
    return load_json(wikipedia_processed_file_path)
