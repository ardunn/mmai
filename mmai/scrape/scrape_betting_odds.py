import requests
import warnings
import pandas as pd
from bs4 import BeautifulSoup

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



ODDS_BASE_LINK = "https://www.bestfightodds.com"


def get_fighter_record_betting_odds_from_relative_link(relative_link):
    """
    Get a single fighter's betting odds for all of their fights from a relative link.

    Args:
        relative_link (str): The relative link after the odds base link, e.g., /fighters/Brandon-Vera-131.

    Returns:
        df (pd.DataFrame): A pandas dataframe of the fighters names for each of the bouts, their

    """
    src = ODDS_BASE_LINK + relative_link
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"}
    r = requests.get(src, headers=headers)
    odds_html = r.content
    soup = BeautifulSoup(odds_html, features="html5lib")

    # print(soup.prettify())
    tables = soup.find_all(
        'table',
    )

    if len(tables) > 1:
        warnings.warn("Multiple tables. found")
    elif len(tables) == 0:
        warnings.warn("No tables found.")

    t = tables[0]
    rows = t.find_all("tr")
    rows = [r for r in rows if "event-header" not in str(r)]

    # header = rows[0]
    # columns = ["".join(h.contents) for h in header.find_all("th")]

    rows = rows[1:]   # get rid of table header

    if len(rows) % 2 != 0:
        raise ValueError("row lengths are now divisible by 2...")

    row_sets = [(rows[i], rows[i+1]) for i in range(0, len(rows), 2)]
    row_sets = [r for r in row_sets if "Future Event" not in str(r[0])]
    row_sets = [r for r in row_sets if "n/a" not in str(r[0])]
    row_sets = [r for r in row_sets if "n/a" not in str(r[1])]

    # f1_info = [d.find("span").contents for d in rows[3].find_all("td")]
    headers = ["fighter_1", "fighter_1_odds_open", "fighter_1_odds_close_best", "fighter_1_odds_close_worst",
               "fighter_2", "fighter_2_odds_open", "fighter_2_odds_close_best", "fighter_2_odds_close_worst"]
    data = []
    for rs in row_sets:
        bout_data = []
        for row in rs:
            info = []
            for cell in row.find_all("td"):
                # print(cell)
                inner_span = cell.find("span")
                if inner_span:
                    contents = inner_span.contents[0]
                    if "–" not in contents and "%" not in contents:
                        info.append(contents)

            fighter = row.find("th").find("a").find("div").contents[0]

            df_row = [fighter] + info
            bout_data += df_row
        data.append(bout_data)

    df = pd.DataFrame(columns=headers, data=data)
    return df


def get_relative_link_from_fighter_name(name):
    # /search?query=Jon+Jones
    pass


if __name__ == "__main__":
    # df = get_fighter_record_betting_odds_from_relative_link("/fighters/Brandon-Vera-173")
    df = get_fighter_record_betting_odds_from_relative_link("/fighters/Israel-Adesanya-7845")

    print(df)