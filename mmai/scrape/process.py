import warnings
from string import ascii_letters
import unicodedata
from datetime import datetime
import re

import numpy as np

from mmai.scrape.load import load_wikipedia_raw


def process_wikipedia(warning_level_threshold=1):
    """
    Process the raw wikipedia records.

    Args:
        warning_level_threshold: Only retain records with this warning level or lower.

    Returns:

    """
    raw = load_wikipedia_raw()
    # fighters = []
    fighters = {}

    for f in raw:
        warning_level = f["warning_level"]
        title = f["title"]
        link = f["link"]

        if warning_level > warning_level_threshold:
            warnings.warn(
                f"Omitting {title} ({link}) because warning level is {warning_level} > {warning_level_threshold}")
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
        modified_name = canonicalize_name(full_name)
        print(f"Formatted name {full_name} to {modified_name}")

        info = f.get("info", np.nan)
        today = datetime.today()
        age_days = np.nan
        try:
            bday_raw = info["Formatted birthday"]
            bday = datetime.strptime(bday_raw)
            diff = today - bday
            age_days = diff.days
        except:
            pass

        height = np.nan
        try:
            height_raw = info["Height"]
            height_raw = re.search('\(([^)]+)', height_raw).group(1)
            height = height_raw.replace("\xa0m", "")
        except KeyError:
            pass

        reach = np.nan
        try:
            reach_raw = info["Reach"]
            reach_raw = re.search('\(([^)]+)', reach_raw)
            if reach_raw:
                reach_raw = reach_raw.group(1)
            else:
                raise AssertionError
            reach = reach_raw.replace("\xa0cm", "")
        except (KeyError, AssertionError):
            pass

        weight = np.nan
        try:
            weight_raw = info["Weight"]
            print("weight raw is ", weight_raw)
            weight_raw = re.search('\(([^)]+)', weight_raw)
            if weight_raw:
                weight_raw = weight_raw.group(1)
            else:
                raise AssertionError
            weight = weight_raw.split(";")[0].replace("\xa0kg", "")
            print("weight formatted is ", weight)
        except (KeyError, AssertionError):
            pass

        fighter_data = {
            "record": record,
            "link": f["link"],
            "warning_level": warning_level,
            "name_raw": full_name,
            "name": modified_name,
            "age_days": age_days,
            "height_m": height,
            "weight_kg": weight,
            "reach_cm": reach
        }

        fighters[full_name] = fighter_data
    return fighters


def canonicalize_name(full_name):
    """
    Turn a name containing foreign characters into a name containing all ASCII chars.

    Accented characters are turned into their ASCII equivalents.

    Args:
        full_name: (str) The full name with (possibly) foreign characters.

    Returns:
        modified_name (str): The ASCII-compatible name.
    """
    allowed_letters = ascii_letters + " -`'"
    if all([letter in allowed_letters for letter in full_name]):
        return full_name
    else:
        modified_name = ""
        warnings.warn(f"Processing full name {full_name} with non-allowed letters.")
        normalized_name = ''.join(c for c in unicodedata.normalize('NFD', full_name) if unicodedata.category(c) != 'Mn')
        for letter in normalized_name:
            if letter in allowed_letters:
                modified_name += letter
            else:
                pass
        return modified_name





if __name__ == "__main__":
    fighters = process_wikipedia()
    print(len(fighters))
    import pprint

    # pprint.pprint(fighters["Jon Jones"])
    # pprint.pprint(fighters["Shane Burgos"])


    stats = ["reach_cm", "weight_kg", "height_m"]
    for stat in stats:
        n_parsed = 0
        n_not_parsed = 0
        for fighter, fdata in fighters.items():
            if type(fdata[stat]) == str:
                n_parsed += 1
            else:
                n_not_parsed += 1
        print(f"For {stat}: {n_parsed} parsed, {n_not_parsed} not parsed.")

    # seen = []
    # duplicated = []
    # for fighter in fighters:
    #     if fighter in seen:
    #         duplicated.append(fighter)
    #     seen.append(fighter)

    # pprint.pprint(fighters)
    # print(len(set(fighters)))
    # print(duplicated)


