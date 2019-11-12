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
        warning_level = f["warning_level"]
        title = f["title"]
        link = f["link"]

        if warning_level > warning_level_threshold:
            warnings.warn(f"Omitting {title} ({link}) because warning level is {warning_level} > {warning_level_threshold}")
            continue

        info = f["info"]
        if not info:
            warnings.warn(f"Omitting {title} ({link}) because it doesn't have info.")
            continue

        full_name = info["Full name"]
        if not full_name:
            warnings.warn(f"Omitting {title} ({link}) because it doesn't have a full name.")


