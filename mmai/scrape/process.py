import warnings

from mmai.scrape.load import load_wikipedia_raw

def process_wikipedia(warning_level_threshold=1):
    """
    Process the raw wikipedia records.

    Args:
        warning_level_threshold: Only retain records with this warning level or lower.

    Returns:

    """
    raw = load_wikipedia_raw()
    fighters = {}

    for f in raw:
        if f["warning_level"] > warning_level_threshold:
