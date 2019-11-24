import string
import requests

from bs4 import BeautifulSoup
from tqdm import tqdm

from mmai.data.base import DataBase


class AggregateStatsScraper(DataBase):

    def __init__(self):
        self.data = None
        self.data_filename = None

        self.base_link = "http://ufcstats.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"
        }

    def get_all_links_from_table(self):
        all_links = []
        for char in tqdm(string.ascii_lowercase):
            src = f"http://ufcstats.com/statistics/fighters?char={char}&page=all"
            r = requests.get(src, headers=self.headers).content
            soup = BeautifulSoup(r, features="html5lib")

            for l in soup.findAll('a', class_="b-link b-link_style_black", href=True):
                href = l["href"]
                if "fighter-details" in href:
                    if href not in all_links:
                        all_links.append(href)

        all_links = [s.replace(self.base_link, "") for s in all_links]
        return all_links

    def get_fighter_aggregate_stats_from_relative_link(self, relative_link):
        src = self.base_link + relative_link
        r = requests.get(src, headers=self.headers).content
        soup = BeautifulSoup(r, features="html5lib")

        print(soup.prettify())

    def get_fighter_record_from_relative_link(self, relative_link):
        pass




if __name__ == "__main__":
    ass = AggregateStatsScraper()
    # ass.get_all_links_from_table()
    ass.get_fighter_aggregate_stats_from_relative_link("/fighter-details/eef9b891edbd4604")