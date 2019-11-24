import json
import os

from mmai.util import load_json


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class DataBase:
    """
    A base class for data operations onighter data.
    """

    def __init__(self):
        self.data = None
        self.data_filename = None

    def load(self):
        """
        Load the raw scraped data from a static file.

        Returns:
            [dict]: a list of raw fighter data dicts

        """
        d = load_json(self.data_filename)
        self.data = d
        return d

    def save(self):
        """
        Saves the raw scraped data list to a file.

        Returns:
            None
        """
        with open(self.data_filename, "w") as f:
            json.dump(self.data, f)
        print(f"File dumped to {self.data_filename}!")
