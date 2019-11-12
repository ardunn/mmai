import requests
import warnings

from bs4 import BeautifulSoup
import pandas as pd

"""
Functions for going from links to raw records.
"""

WIKI_BASE_LINK = "https://en.wikipedia.org"


def get_fighter_record_and_info_from_relative_link(relative_link, condense=True, quiet=True, silent=False):
    """
    Get a fighter's record and info from a relative wikipedia link.

    Args:
        relative_link: A BeautifulSoup text object determined to contain a relative link, e.g., containing
            href="/wiki/Some_Fighter" or a (str) relative link, e.g., "/wiki/Some_Fighter"
        condense (bool): Checks to see if multiple info/records are identical and if they all are, returns one.
        quiet (bool): If False, prints when parsing either record or info fails any table!
        silent (bool): If False, warns when either multiple records or infos are found, or if no record or no info is
            found.

    Returns:
        (dict): Contains "record" and "info" fields. If all the parsing went well, each field's value should be a dict.
            Otherwise, will be a list (if multiple of either item) or None (if not found). Also contains warning_level
            field for determining how good a parsing was: 0 means no warnings, 1 means 1 warning, and 2 means
            both record and info were likely messed up.

    """
    request = get_page_content_by_wiki_relative_link(relative_link)
    soup = BeautifulSoup(request.content, features="html.parser")
    fighter_data = {"record": None, "info": None}
    warning_level = 0

    records = []
    infos = []
    for t, table in enumerate(soup.find_all("table")):
        try:
            record = get_record_from_table(table, quiet=quiet)
            info = get_fighter_info_from_table(soup, quiet=quiet)
        except AttributeError:
            break
        if record:
            records.append(record)
        if info:
            infos.append(info)

    if len(records) == 1:
        fighter_data["record"] = records[0]
    elif len(records) > 1:
        if condense:
            if all([r == records[0] for r in records]):
                fighter_data["record"] = records[0]
            else:
                warning_level += 1
                if not silent:
                    warnings.warn(f"Multiple records found for {relative_link} and could not condense. Keeping all.")
        else:
            warning_level += 1
            if not silent:
                warnings.warn(f"Multiple records found for {relative_link}! Keeping all.")
    else:
        warning_level += 1
        if not silent:
            warnings.warn(f"Fighter record from {relative_link} not parsed.")

    if len(infos) == 1:
        fighter_data["info"] = infos[0]
    elif len(infos) > 1:
        if condense:
            if all([r == infos[0] for r in infos]):
                fighter_data["info"] = infos[0]
            else:
                warning_level += 1
                if not silent:
                    warnings.warn(f"Multiple infos found for {relative_link} and could not condense. Keeping all.")
        else:
            warning_level += 1
            if not silent:
                warnings.warn(f"Multiple infos found for {relative_link}! Keeping all.")
    else:
        warning_level += 1
        if not silent:
            warnings.warn(f"Fighter info from {relative_link} not parsed.")

    fighter_data["warning_level"] = warning_level

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
        fights = []
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            fights.append([ele for ele in cols if ele])  # Get rid of empty values

        # print(table_body)
        # print("\n\n\n\n\n\n\n")
        headers = table_body.find_all('th')
        headers = [ele.text.strip().replace(".", "") for ele in headers]

        fights = [d for d in fights if d]  # remove empty lists/rows
        noted_data = []
        max_len = max([len(f) for f in fights])
        if max_len > fighter_record_table_length:
            if not quiet:
                warnings.warn("Record not parsed from table due to expected column mismatch, is this a some other kind "
                              "of table?")
            return None

        # if not headers or len(headers) != max_len:
        #     if not quiet:
        #         warnings.warn("Record not parsed from table due to header parsing problem. Is this a kickboxing "
        #                       "record?")
        #     return None

        # for f in fights:
        #     print(len(f), f)

        for i, fight in enumerate(fights):
            fight_diff = fighter_record_table_length - len(fight)
            if fight_diff in [1, 2]:
                fight += [''] * fight_diff  # add in blank note(s)
            elif fight_diff == 0:
                pass
            else:
                if not quiet:
                    warnings.warn(f"Fight {i} not matching length of at least one other fight, refusing to add this "
                                  "fight")
                continue
            noted_data.append(fight)

        try:
            raw_df = pd.DataFrame(columns=headers, data=noted_data)
        except:
            if not quiet:
                warnings.warn("Record could not be converted to dataframe.")
            return None
        df_as_list = list(raw_df.T.to_dict().values())
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
        table_body = None
        for tb in table.find_all('tbody'):
            # Make sure it is the right tbody from all of the possible tables!
            if 'class="fn"' in str(tb):
                table_body = tb
        if not table_body:
            if not quiet:
                print("Table body could not be parsed")
            return None

        span_keys = {
            "fn": "Full name",
            "bday": "Formatted birthday",
        }
        info = {v: None for _, v in span_keys.items()}

        for k, v in span_keys.items():
            items = table_body.find_all('span', class_=k)
            if not items:
                if not quiet:
                    warnings.warn("Could not parse basic info from fighter table! Continuing anyways")
                    info[v] = None
            else:
                item = items[0]
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

        rows = table_body.find_all('tr')
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


def get_page_content_by_wiki_relative_link(relative_link, base_link=WIKI_BASE_LINK):
    """
    Fetch the html content for a wikipedia fighter page by relative link.

    Args:
        relative_link: A BeautifulSoup text object determined to contain a relative link, e.g., containing
            href="/wiki/Some_Fighter" or a (str) relative link, e.g., "/wiki/Some_Fighter"
        base_link: The base wikipedia link.

    Returns:

    """
    try:
        r = requests.get(base_link + relative_link.get("href"))
    except AttributeError:
        r = requests.get(base_link + relative_link)
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
