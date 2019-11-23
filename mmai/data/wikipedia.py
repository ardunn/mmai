import requests
import json
import os
import re
from datetime import datetime
import warnings
from string import ascii_letters
import unicodedata

from bs4 import BeautifulSoup
import pandas as pd
import tqdm
import numpy as np

from mmai.util import load_json

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class WikiFightersBase:
    """
    A base class for data operations on wikipedia fighter data.
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


class WikiFightersProcessed(WikiFightersBase):
    """
    A class for processing raw data scraped from wikipedia.

    Attrs:
        data ([dict]): A dict of fighters in {fighter_name: {data}} format.
        data_filename (str): A string of the full path where this class's output is saved
        raw_data: The data which this class cleans and processes.
    """

    def __init__(self, raw_data):
        """
        A list of fighter dicts scraped using the WikiFightersRaw class. Use the .data attr.

        Args:
            raw_data: The output of the WikiFightersRaw class. Use the .data attr.
        """
        self.raw_data = raw_data
        self.data = None
        self.data_filename = os.path.join(
            THIS_DIR, "static/wiki_fighters_processed.json"
        )

    def process(self, warning_level_threshold=1):
        """
        Process the raw wikipedia records.

        Args:
            warning_level_threshold: Only retain records with this warning level or lower.

        Returns:

        """
        raw = self.raw_data
        # fighters = []
        fighters = {}

        for f in raw:
            warning_level = f["warning_level"]
            title = f["title"]
            link = f["link"]

            if warning_level > warning_level_threshold:
                warnings.warn(
                    f"Omitting {title} ({link}) because warning level is {warning_level} > {warning_level_threshold}"
                )
                continue

            info = f["info"]
            if not info:
                warnings.warn(
                    f"Omitting {title} ({link}) because it doesn't have info."
                )
                continue

            record = f["record"]
            if not record:
                warnings.warn(f"Omitting {title} ({link}) because no record was found.")
                continue

            full_name = info["Full name"]
            if not full_name:
                warnings.warn(
                    f"Omitting {title} ({link}) because it doesn't have a full name."
                )
                continue

                # disambiguate names with foreign characters
            modified_name = self.canonicalize_name(full_name)
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
                height_raw = re.search("\(([^)]+)", height_raw).group(1)
                height = height_raw.replace("\xa0m", "").strip()
            except KeyError:
                pass

            reach = np.nan
            try:
                reach_raw = info["Reach"]
                reach_raw = re.search("\(([^)]+)", reach_raw)
                if reach_raw:
                    reach_raw = reach_raw.group(1)
                else:
                    raise AssertionError
                reach = reach_raw.replace("\xa0cm", "").strip()
            except (KeyError, AssertionError):
                # reach_raw = info.get("Reach", "does not have reach")
                # print(f"REACH FINDING FAILED, the reach raw is {reach_raw}")
                pass

            weight = np.nan
            try:
                weight_raw = info["Weight"]
                # print("weight raw is ", weight_raw)
                weight_raw = re.search("\(([^)]+)", weight_raw)
                if weight_raw:
                    weight_raw = weight_raw.group(1)
                else:
                    raise AssertionError
                weight = weight_raw.split(";")[0].replace("\xa0kg", "").strip()
                # print("weight formatted is ", weight)
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
                "reach_cm": reach,
            }

            fighters[full_name] = fighter_data

        self.data = fighters
        return fighters

    ################################################################################################################
    # Auxiliary methods
    ################################################################################################################

    def canonicalize_name(self, full_name):
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
            normalized_name = "".join(
                c
                for c in unicodedata.normalize("NFD", full_name)
                if unicodedata.category(c) != "Mn"
            )
            for letter in normalized_name:
                if letter in allowed_letters:
                    modified_name += letter
                else:
                    pass
            return modified_name


class WikiFightersRaw(WikiFightersBase):
    """
    A class for scraping raw MMA fighter data from wikipedia.

    The main methods to be use are save, load, and scrape.

    Attrs:
        data ([dict]): A list of fighters in dictionary format. The final output of this class.
        data_filename (str): A string of the full path where this class's output is saved.
    """

    def __init__(self):
        self.data = None
        self.data_filename = os.path.join(THIS_DIR, "static/wiki_fighters_raw.json")

    def scrape(self, report=True):
        """
        Scrape wikipedia for all relevant fighter data.

        Args:
            report (bool): If True, saves a report of the good, bad, and ugly parsings based on warning level.

        Returns:
        """
        links = self.get_fighter_links()
        good = []
        bad = []
        ugly = []
        fighters = []

        for link in tqdm.tqdm(links):
            fighter_data = self.get_fighter_record_and_info_from_relative_link(
                link, quiet=True, silent=False
            )

            w = fighter_data["warning_level"]
            if w == 0:
                good.append(link)
            elif w == 1:
                bad.append(link)
            elif w == 2:
                ugly.append(link)
            else:
                raise ValueError("Warning value not [0-2]!")

            fighter_data["link"] = str(link)
            fighter_data["title"] = link.text

            # pprint.pprint(fighter_data)
            fighters.append(fighter_data)

        n_links = len(links)
        print(
            f"Links successfully parsed: {len(good)}/{n_links}"
            f"\nLinks having one problem: {len(bad)}/{n_links}"
            f"\nLinks having multiple problems: {len(ugly)}/{n_links}"
        )

        if report:
            with open("wikipedia_scraping_report.txt", "w") as f:
                designations = {"good": good, "bad": bad, "ugly": ugly}
                for d, l in designations.items():
                    f.write(d + "\n")
                    f.write("-------------------------------------")
                    for item in l:
                        f.write(l.text)
                        f.write("\n")
                    f.write("\n\n\n")

        self.data = fighters
        return fighters

    ################################################################################################################
    # Auxiliary methods
    ################################################################################################################

    def get_fighter_links(
        self,
        src="https://en.wikipedia.org/wiki/List_of_male_mixed_martial_artists",
        return_garbage=False,
    ):
        """
        Get a list of fighters as links to their individual wikipedia pages.
        Args:
            src (str): A string url representing a table of mma fighters on wikipedia with links.
            return_garbage (bool): If True, returns the links determined as garbage.

        Returns:
            a list of links: either fighters as determined by screning or a list of garbage links

        """
        r = requests.get(src)
        fighter_hmtl = r.content
        soup = BeautifulSoup(fighter_hmtl, features="html.parser")
        fighters = []
        garbage = []
        for link in soup.find_all("a"):
            if self.is_fighter(link):
                fighters.append(link)
            else:
                garbage.append(link)

        if return_garbage:
            return garbage
        else:
            return fighters

    def get_fighter_record_and_info_from_relative_link(
        self, relative_link, condense=True, quiet=True, silent=False
    ):
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
        request = self.get_page_content_by_wiki_relative_link(relative_link)
        soup = BeautifulSoup(request.content, features="html.parser")
        fighter_data = {"record": None, "info": None}
        warning_level = 0

        records = []
        infos = []
        for t, table in enumerate(soup.find_all("table")):
            try:
                record = self.get_record_from_table(table, quiet=quiet)
                info = self.get_fighter_info_from_table(soup, quiet=quiet)
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
                        warnings.warn(
                            f"Multiple records found for {relative_link} and could not condense. Keeping all."
                        )
            else:
                warning_level += 1
                if not silent:
                    warnings.warn(
                        f"Multiple records found for {relative_link}! Keeping all."
                    )
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
                        warnings.warn(
                            f"Multiple infos found for {relative_link} and could not condense. Keeping all."
                        )
            else:
                warning_level += 1
                if not silent:
                    warnings.warn(
                        f"Multiple infos found for {relative_link}! Keeping all."
                    )
        else:
            warning_level += 1
            if not silent:
                warnings.warn(f"Fighter info from {relative_link} not parsed.")

        fighter_data["warning_level"] = warning_level

        return fighter_data

    def get_record_from_table(self, table, quiet=True):
        """
        Parse a fighter's record from a wikipedia table.

        Args:
            table: A BeautifulSoup text table from html
            quiet: If False, prints when a parsing fails for a table.

        Returns:
            ([dict], None): The fighter's record as a list of dicts, or None if parsing fails.

        """
        fighter_record_table_length = 10
        if self.is_fighter_record(table):
            fights = []
            table_body = table.find("tbody")
            rows = table_body.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                fights.append([ele for ele in cols if ele])  # Get rid of empty values

            # print(table_body)
            # print("\n\n\n\n\n\n\n")
            headers = table_body.find_all("th")
            headers = [ele.text.strip().replace(".", "") for ele in headers]

            fights = [d for d in fights if d]  # remove empty lists/rows
            noted_data = []
            max_len = max([len(f) for f in fights])
            if max_len > fighter_record_table_length:
                if not quiet:
                    warnings.warn(
                        "Record not parsed from table due to expected column mismatch, is this a some other kind "
                        "of table?"
                    )
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
                    fight += [""] * fight_diff  # add in blank note(s)
                elif fight_diff == 0:
                    pass
                else:
                    if not quiet:
                        warnings.warn(
                            f"Fight {i} not matching length of at least one other fight, refusing to add this "
                            "fight"
                        )
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

    def get_fighter_info_from_table(self, table, quiet=True):
        """
        Get a fighter's basic info from a wikipedia parsed table.

        Args:
            table: A BeautifulSoup text table from html
            quiet (bool): If False, prints when a parsing fails for a table.

        Returns:
            (dict, None): Basic info about the fighter, or None if the parsing failed.

        """
        if self.is_fighter_bio(table):
            table_body = None
            for tb in table.find_all("tbody"):
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
                items = table_body.find_all("span", class_=k)
                if not items:
                    if not quiet:
                        warnings.warn(
                            "Could not parse basic info from fighter table! Continuing anyways"
                        )
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
                "Style",
            ]

            rows = table_body.find_all("tr")
            for row in rows:
                if any([r in row.text for r in row_keys]):
                    header = row.find("th").text.strip()
                    value = row.find("td").text.strip()
                    info[header] = value
            return info
        else:
            if not quiet:
                print("Info not parsed from table.")
            return None

    def get_page_content_by_wiki_relative_link(
        self, relative_link, base_link="https://en.wikipedia.org"
    ):
        """
        Fetch the html content for a wikipedia fighter page by relative link.

        Args:
            relative_link: A BeautifulSoup text object determined to contain a relative link, e.g., containing
                href="/wiki/Some_Fighter" or a (str) relative link, e.g., "/wiki/Some_Fighter"
            base_link: The base wikipedia link.

        Returns:
            The raw html page content.
        """
        try:
            r = requests.get(base_link + relative_link.get("href"))
        except AttributeError:
            r = requests.get(base_link + relative_link)
        return r

    def is_fighter(self, link):
        """
        Determine whether a link from a wikipedia table represents a fighter or is just garbage.

        Args:
            link: A BeautifulSoup result object (or link that can be converted to string).

        Returns:
            (bool): True, if link appears to be fighter. Else, garbage.
        """
        candidate = str(link).lower()

        excluded_terms = [
            "flag_",
            "championship",
            "king of the cage",
            " mma",
            "pancrase",
            "k-1",
            "shooto",
            "cite_note",
            "cite_ref",
            "fighting",
            "affliction entertainment",
            "super fight league",
            "cage warriors",
            "strikeforce",
            "world series",
            "list of",
            "kotc",
            "association",
            "elitexc",
            "m-1",
            "shoxc",
            "category",
            "content",
            "discussion",
            "fights",
            "article",
            "wikipedia",
            "wikimedia",
            "logo",
            "accesskey",
            "developers",
            "mixed martial arts",
            "Sengoku",
            "international fight league",
            "list_of",
            "current_events",
            "help:section",
            "ksw",
        ]
        if any([term in candidate for term in excluded_terms]):
            return False
        required_terms = ["/wiki/"]
        if not all([term in candidate for term in required_terms]):
            return False
        return True

    def is_fighter_record(self, table):
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

    def is_fighter_bio(self, table):
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


if __name__ == "__main__":
    wikir = WikiFightersRaw()
    wikir.load()

    print(len(wikir.data))

    wikip = WikiFightersProcessed(raw_data=wikir.data)
    wikip.process()

    wikip.save()
    print(wikip.data)
