import requests
import warnings
import pandas as pd
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
import difflib
import time
import random

from mmai.data.base import DataBase, THIS_DIR

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 1000)


class OddsScrapeAndProcess(DataBase):

    def __init__(self):
        self.data = None
        self.data_filename = os.path.join(
            THIS_DIR, "static/odds.json"
        )
        self.base_link = "https://www.bestfightodds.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"
        }

    def scrape(self, fighter_names, randomized_wait=False):

        betting_odds = {}

        for name in tqdm(fighter_names):
            if randomized_wait:
                wait = random.random() * 3.0
                time.sleep(wait)

            links = self.get_relative_link_from_fighter_name(name)

            good = []  # warning level 0
            bad = []   # warning level 1
            ugly = []  # warning level 2

            odds_record = None

            if len(links) == 0:
                print(f"No links found for fighter: {name}")
                bad.append(name)
                warning_level = 1
                continue
            elif len(links) > 1:
                warnings.warn(f"Too many links found for {name}, keeping the first one ({links[0]}")
            link = links[0]

            try:
                odds_record = self.get_fighter_record_betting_odds_from_relative_link(link)
                good.append(name)
                warning_level = 0
            except:
                warnings.warn(f"Link {link} for fighter {name} was tried but failed.")
                ugly.append(name)
                warning_level = 2

            data = {
                "warning_level": warning_level,
                "odds_record": odds_record.to_dict()
            }

            betting_odds[name] = data

        self.data = betting_odds

    def get_fighter_record_betting_odds_from_relative_link(self, relative_link):
        """
        Get a single fighter's betting odds for all of their fights from a relative link.

        Args:
            relative_link (str): The relative link after the odds base link, e.g., /fighters/Brandon-Vera-131.

        Returns:
            df (pd.DataFrame): A pandas dataframe of the fighters names for each of the bouts, their

        """
        src = self.base_link + relative_link
        r = requests.get(src, headers=self.headers)
        odds_html = r.content
        soup = BeautifulSoup(odds_html, features="html5lib")

        # print(soup.prettify())
        tables = soup.find_all("table", )

        if len(tables) > 1:
            warnings.warn("Multiple tables. found")
        elif len(tables) == 0:
            warnings.warn("No tables found.")

        t = tables[0]
        rows = t.find_all("tr")
        rows = [r for r in rows if "event-header" not in str(r)]

        # header = rows[0]
        # columns = ["".join(h.contents) for h in header.find_all("th")]

        rows = rows[1:]  # get rid of table header

        if len(rows) % 2 != 0:
            raise ValueError("row lengths are now divisible by 2...")

        row_sets = [(rows[i], rows[i + 1]) for i in range(0, len(rows), 2)]
        row_sets = [r for r in row_sets if "Future Event" not in str(r[0])]
        row_sets = [r for r in row_sets if "n/a" not in str(r[0])]
        row_sets = [r for r in row_sets if "n/a" not in str(r[1])]

        # f1_info = [d.find("span").contents for d in rows[3].find_all("td")]
        headers = [
            "fighter_1",
            "fighter_1_odds_open",
            "fighter_1_odds_close_best",
            "fighter_1_odds_close_worst",
            "fighter_2",
            "fighter_2_odds_open",
            "fighter_2_odds_close_best",
            "fighter_2_odds_close_worst",
            "date"
        ]
        data = []
        for rs in row_sets:
            bout_data = []
            for row in rs:
                info = []
                for cell in row.find_all("td"):
                    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    if any([m + " " in str(cell) for m in months]):
                        info.append(cell.contents[0])
                    else:
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

    def get_relative_link_from_fighter_name(self, name):
        # /search?query=Jon+Jones

        name_url_query = name.strip().replace(" ", "+")
        search_link = f"/search?query={name_url_query}"

        # print(search_link)

        src = self.base_link + search_link
        r = requests.get(src, headers=self.headers)
        soup = BeautifulSoup(r.content, features="html5lib")
        all_links = soup.findAll('a', href=True)

        name_linked = "-".join(name.strip().split(" ")).lower()

        working_links = []
        for link in all_links:
            if link.parent.name == "td":
                lower_link = str(link).lower()
                if name_linked in lower_link:
                    href = str(link["href"]).lower()
                    lower_link_stripped = href.replace("/fighters/", "")
                    # print(name_linked, lower_link_stripped)
                    seq = difflib.SequenceMatcher(a=name_linked, b=lower_link_stripped)
                    if seq.ratio() > 0.5:
                        working_links.append(href)
                    else:
                        print(f"Sequence difference too great between {name_linked} and {lower_link_stripped}")

        return working_links

if __name__ == "__main__":
    from mmai.data.wikipedia import WikiFightersProcessed
    import random

    wikip = WikiFightersProcessed()
    wikip.load()

    fighter_names = list(wikip.data.keys())
    # fighter_names = random.sample(fighter_names, 10)

    odds = OddsScrapeAndProcess()
    # links = odds.get_relative_link_from_fighter_name("Jon Jones")
    # table = odds.get_fighter_record_betting_odds_from_relative_link(links[0])
    odds.scrape(fighter_names, randomized_wait=True)
    odds.save()
    #
    # n_non2 = 0
    # for f in wikip.data.keys():
    #     if len(f.split(" ")) != 2:
    #         print(f)
    #         n_non2 += 1
    #
    # print(n_non2)
