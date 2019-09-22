import requests
import warnings

from bs4 import BeautifulSoup
import pandas as pd

"""
Functions for going from links to raw records.
"""

WIKI_BASE_LINK = "https://en.wikipedia.org"
KNOWN_TABLE_LENGTH = 10


def get_page_content_by_wiki_relative_link(relative_link, base_link=WIKI_BASE_LINK):
    r = requests.get(base_link + relative_link.get("href"))
    return r


def is_fighter_record(table):
    if "Location" not in str(table):
        return False
    else:
        return True


def is_fighter_bio(table):
    if 'class="infobox vcard"' in str(table):
        return True
    else:
        return False


def get_fighter_record_and_info_from_relative_link(relative_link, quiet=True, silent=False):
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
        if max_len > KNOWN_TABLE_LENGTH:
            raise ValueError(
                "max_len is more than the known table length? {} > {}".format(max_len, KNOWN_TABLE_LENGTH))

        for fight in data:
            fight_diff = KNOWN_TABLE_LENGTH - len(fight)
            if fight_diff == 1:
                fight.append('')  # add in blank note
            elif fight_diff == 0:
                pass
            else:
                raise ValueError(
                    "Difference in length of fight and known length is {}? fight is: {}".format(fight_diff, fight))
            noted_data.append(fight)
        raw_df = pd.DataFrame(columns=headers, data=noted_data)
        return raw_df
    else:
        if not quiet:
            print("Record not parsed from table.")
        return None


def get_fighter_info_from_table(table, quiet=True):
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
