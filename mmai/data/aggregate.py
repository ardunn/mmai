import string
import requests

from mmai.data.base import DataBase


class AggregateStatsScraper(DataBase):

    def __init__(self):
        self.data = None
        self.data_filename = None

    def get_all_links_from_table(self):
        for char in string.ascii_lowercase:
            src = f"http://ufcstats.com/statistics/fighters?char={char}&page=all"
