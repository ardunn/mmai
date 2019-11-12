import warnings
from string import ascii_letters
import unicodedata

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

        record = f["record"]
        if not record:
            warnings.warn(f"Omitting {title} ({link}) because no record was found.")
            continue

        full_name = info["Full name"]
        if not full_name:
            warnings.warn(f"Omitting {title} ({link}) because it doesn't have a full name.")
            continue

        # disambiguate names with foreign characters
        allowed_letters = ascii_letters + " -`'"
        if not all([letter in allowed_letters for letter in full_name]):
            warnings.warn(f"Processing full name {full_name} with non-allowed letters.")
            # print(full_name)
            normalized_name = ''.join(c for c in unicodedata.normalize('NFD', full_name) if unicodedata.category(c) != 'Mn')
            modified_name = ""
            for letter in normalized_name:
                # print(type(letter))
                if letter in allowed_letters:
                    modified_name += letter
                else:
                    pass
            print(f"Formatted name {full_name} to {modified_name}")




        fighter_data = {
            "record": record,
            "link": f["link"],
            "warning_level": warning_level,
            "name_raw": full_name,
            "name": modified_name,


        }




if __name__ == "__main__":
    process_wikipedia()


