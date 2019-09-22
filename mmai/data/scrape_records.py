import requests

from bs4 import BeautifulSoup
import pandas as pd

from mmai.data.scrape_fighters import get_fighter_links


"""
Functions for going from links to raw records.
"""


WIKI_BASE_LINK = "https://en.wikipedia.org"
KNOWN_TABLE_LENGTH = 10
# KNOWN_TABLE_HEADERS =

def get_page_content_by_wiki_relative_link(relative_link, base_link=WIKI_BASE_LINK):
    r = requests.get(base_link + relative_link.get("href"))
    return r

def is_fighter_record(table):
    if "Location" not in str(table):
        return False
    else:
        return True

def is_fighter_bio(table):
    if "Location" not in str(table):
        return False
    else:
        return True


def link_to_raw_fighter_record(link, quiet=True, very_quiet=False):
    request = get_page_content_by_wiki_relative_link(link)
    soup = BeautifulSoup(request.content, features="html.parser")

    for t, table in enumerate(soup.find_all("table")):
        data = []
        if is_fighter_record(table):
            # print(table)
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])  # Get rid of empty values

            headers = table_body.find_all('th')
            headers = [ele.text.strip() for ele in headers]
            # print(headers)

            data = [d for d in data if d]  # remove empty lists/rows
            noted_data = []
            max_len = max([len(d) for d in data])
            if max_len > KNOWN_TABLE_LENGTH:
                raise ValueError("max_len is more than the known table length? {} > {}".format(max_len, KNOWN_TABLE_LENGTH))

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

            if not very_quiet:
                print(f"Fighter link {link} successfully parsed from table {t}")
            return raw_df
        else:
            if not quiet:
                print(f"Fighter record not parsed from table {t}.")
            continue
    else:
        if not very_quiet:
            print(f"Fighter link could not be parsed from any table!")
        return None

if __name__ == "__main__":
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    links = get_fighter_links()

    # print(links)

    link = links[241]

    df = link_to_raw_fighter_record(link)
    print(df)
