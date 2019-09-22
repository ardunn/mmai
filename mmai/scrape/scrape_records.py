import requests
import warnings

from bs4 import BeautifulSoup
import pandas as pd

"""
Functions for going from links to raw records.
"""

WIKI_BASE_LINK = "https://en.wikipedia.org"


def get_page_content_by_wiki_relative_link(relative_link, base_link=WIKI_BASE_LINK):
    """
    Fetch the html content for a wikipedia fighter page by relative link.

    Args:
        relative_link: The relative wikipedia link, e.g. /wiki/Some_Fighter
        base_link: The base wikipedia link.

    Returns:

    """
    r = requests.get(base_link + relative_link.get("href"))
    return r


def is_fighter_record(table):
    """
    Determine if a table is a fighter's bio.

    Args:
        table: Beautiful soup text from html table.

    Returns:
        (bool): true, if the table is a fighter record

    """
    if "Location" not in str(table):
        return False
    else:
        return True


def is_fighter_bio(table):
    """
    Determine if a table is a fighter's bio.

    Args:
        table: Beautiful soup text from html table.

    Returns:
        (bool): true, if the table is a fighter bio

    """
    if 'class="infobox vcard"' in str(table):
        return True
    else:
        return False


def get_fighter_record_and_info_from_relative_link(relative_link, quiet=True, silent=False):
    """
    Get a fighter's record and info from a relative wikipedia link.

    Args:
        relative_link (str): The relative link, e.g., /wiki/Some_Fighter
        quiet (bool): If False, prints when parsing either record or info fails any table!
        silent (bool): If False, warns when either multiple records or infos are found, or if no record or no info is
            found.

    Returns:

    """
    request = get_page_content_by_wiki_relative_link(relative_link)
    soup = BeautifulSoup(request.content, features="html.parser")
    fighter_data = {"record": None, "info": None}

    records = []
    infos = []
    for t, table in enumerate(soup.find_all("table")):
        record = get_record_from_table(table, quiet)
        info = get_fighter_info_from_table(soup, quiet)
        if record:
            records.append(record)
        if info:
            infos.append(info)

    if not silent:
        if not records:
            warnings.warn(f"Fighter record from {relative_link} not parsed.")
        elif len(records) > 1:
            warnings.warn(f"Multiple records found for {relative_link}! Keeping all.")
        if not infos:
            warnings.warn(f"Fighter info from {relative_link} not parsed.")
        elif len(infos) > 1:
            warnings.warn(f"Mulitple info blocks found for {relative_link}! Keeping all.")

    if len(records) == 1:
        fighter_data["record"] = records[0]
    else:
        fighter_data["record"] = records

    if len(infos) == 1:
        fighter_data["info"] = infos[0]
    else:
        fighter_data["info"] = infos
    return fighter_data


def get_record_from_table(table, quiet=True):
    """
    Parse a fighter's record from a wikipedia table.

    Args:
        table: A BeautifulSoup text table from html
        quiet: If False, prints when a parsing fails for a table.

    Returns:
        ([dict], None): The fighter's record as a list of dicts, or None if parsing fails.

    """
    fighter_record_table_length = 10
    if is_fighter_record(table):
        data = []
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])  # Get rid of empty values

        headers = table_body.find_all('th')
        headers = [ele.text.strip() for ele in headers]

        data = [d for d in data if d]  # remove empty lists/rows
        noted_data = []
        max_len = max([len(d) for d in data])
        if max_len > fighter_record_table_length:
            raise ValueError(
                "max_len is more than the known table length? {} > {}".format(max_len, fighter_record_table_length))

        for fight in data:
            fight_diff = fighter_record_table_length - len(fight)
            if fight_diff == 1:
                fight.append('')  # add in blank note
            elif fight_diff == 0:
                pass
            else:
                raise ValueError(
                    "Difference in length of fight and known length is {}? fight is: {}".format(fight_diff, fight))
            noted_data.append(fight)
        raw_df = pd.DataFrame(columns=headers, data=noted_data)
        df_as_list = raw_df.T.to_dict().values()
        return df_as_list
    else:
        if not quiet:
            print("Record not parsed from table.")
        return None


def get_fighter_info_from_table(table, quiet=True):
    """
    Get a fighter's basic info from a wikipedia parsed table.

    Args:
        table: A BeautifulSoup text table from html
        quiet (bool): If False, prints when a parsing fails for a table.

    Returns:
        (dict, None): Basic info about the fighter, or None if the parsing failed.

    """
    if is_fighter_bio(table):
        table_body = table.find('tbody')

        span_keys = {
            "fn": "Full name",
            "bday": "Formatted birthday",
        }
        info = {v: None for _, v in span_keys.items()}

        for k, v in span_keys.items():
            item = table_body.find_all('span', class_="fn")[0]
            info[v] = item.text.strip()

        row_keys = [
            "Born",
            "Other names",
            "Nationality",
            "Height",
            "Weight",
            "Division",
            "Reach",
            "Fighting out of",
            "Team",
            "Trainer",
            "Rank",
            "Years active",
            "Style"
        ]

        rows = table.find_all('tr')
        for row in rows:
            if any([r in row.text for r in row_keys]):
                header = row.find('th').text.strip()
                value = row.find('td').text.strip()
                info[header] = value
        return info
    else:
        if not quiet:
            print("Info not parsed from table.")
        return None
